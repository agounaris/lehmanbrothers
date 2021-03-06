import os
import errno
import click
import sys
from pluginbase import PluginBase
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from functools import partial
from pathlib import Path
import configparser


def initialize_directories(app_directory):
    directories = [
        os.path.join(app_directory),
        os.path.join(app_directory, 'cache'),
        os.path.join(app_directory, 'plugins'),
    ]
    # init app directory

    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise


@click.command()
@click.option('--redis-url', default='', help='redis-url')
def main(redis_url):

    here = os.path.abspath(os.path.dirname(__file__))
    get_path = partial(os.path.join, here)

    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.abspath(
        os.path.dirname(__file__)), 'conf', 'lehman.ini'))

    storage = 'filestore'
    if redis_url:
        storage = 'redisstore'
        print(redis_url.split(':'))
        config.set('app', 'redis_url', redis_url.split(':')[0])
        config.set('app', 'redis_port', redis_url.split(':')[1])

    plugin_base = PluginBase(package='plugins',
                             searchpath=[get_path('./plugins'),
                                         get_path('./cache'),
                                         get_path('./datasource')])

    home = str(Path.home())
    app_directory = '{}/{}'.format(home, config['app']['app_directory'])

    initialize_directories(app_directory)

    additional_plugins_path = get_path(os.path.join(
                                       app_directory,
                                       'plugins'))

    # register additional plugins command line parameter
    source = plugin_base.make_plugin_source(
        searchpath=[additional_plugins_path],
        identifier='plugins')

    available_plugins = [plugin for plugin in source.list_plugins()
                         if plugin != 'abstractplugin']

    # history = InMemoryHistory()
    history = FileHistory(os.path.join(app_directory,
                                       'history.txt'))


    # init cache source command line parameter
    cache_obj = source.load_plugin([item for item in available_plugins
                                    if item == storage][0])
    cache_service = cache_obj.DataStore(config)

    # init data source, command line parameter
    data_obj = source.load_plugin([item for item in available_plugins
                                   if item == 'quandl'][0])
    data_service = data_obj.Retriever(config, cache_service)

    try:
        while True:
            input_string = prompt("> ", history=history)

            if input_string in ['exit', 'quit']:
                raise KeyboardInterrupt

            tokens = input_string.split(" ")
            plugin_name = tokens.pop(0)

            if plugin_name in available_plugins:
                object = source.load_plugin(plugin_name)
                try:
                    obj = object.Plugin(data_service, config, tokens)
                except (TypeError, AttributeError) as e:
                    print('There was an issue initializing \
                           the {} object: {}'.format(plugin_name, e))
                    continue

                # try:
                result = obj.run()
                # except Exception as e:
                    # print('There was an issue running '
                          # 'the {} object: {}: {}'.format(plugin_name,
                                                         # repr(e),
                                                         # str(e)))

    except KeyboardInterrupt:
        # just exit
        pass


if __name__ == '__main__':
    main()
