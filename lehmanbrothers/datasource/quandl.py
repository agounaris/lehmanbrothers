import quandl
import pandas as pd

class Retriever(object):

    def __init__(self, config, cache_service):
        self._config = config
        self._cache_service = cache_service
        
    def get_data(self, tokens, key):
        if not tokens:
            return None

        data = self._cache_service.get_data(key)
        if not data:
            quandl.ApiConfig.api_key = self._config['quandl']['api_key']
            data = quandl.get_table('WIKI/PRICES', 
                                    qopts = { 'columns': ['ticker', 'date', 'close'] }, 
                                    ticker = tokens['dependent_variable'], 
                                    date = { 'gte':tokens['date_from'], 'lte': tokens['date_to'] })

            if not isinstance(data, pd.DataFrame):
                return None
        
            self._cache_service.save_data(key, data.to_csv())
        return data