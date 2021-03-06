class NotValidSymbolException(Exception):
    pass

class Difference(object):
    def __init__(self, values=None):
        if isinstance(values, dict):
            for key, value in values.items():
                super(Difference, self).__setattr__(key, value)
        else:
            raise ValueError('Parameter not a dict')

    def __repr__(self):
        text = []
        for attr, value in self.__dict__.items():
            text.append(
                'Attribute {attr:30} changed by {value:.2%}'.format(attr=attr,
                                                                    value=value))
        return '\n'.join(text)

    def __setattr__(self, name, value):
        """"""
        msg = "You are not allowed to set an attribute after init"
        raise AttributeError(msg)


class Statement(object):
    def __init__(self, values=None):
        if isinstance(values, dict):
            for key, value in values.items():
                # setattr(self, key, value)
                super(Statement, self).__setattr__(key, value)
        else:
            raise ValueError('Parameter not a dict')

    def __eq__(self, statement):
        differences = {}
        for attr, value_one in self.__dict__.items():
            try:
                value_two = statement.__dict__[attr]
            except KeyError:
                return None
            if not isinstance(value_one, float) or not isinstance(value_two,
                                                                  float):
                continue

            if value_two:
                percentage = (value_two - value_one) / value_two
                differences[attr] = percentage
            else:
                differences[attr] = 0

        return Difference(differences)

    def __setattr__(self, name, value):
        """"""
        msg = "You are not allowed to set an attribute after init"
        raise AttributeError(msg)


class IncomeStatement(Statement):
    def __init__(self, *args, **kwargs):
        super(IncomeStatement, self).__init__(*args, **kwargs)


class BalanceSheet(Statement):
    def __init__(self, *args, **kwargs):
        super(BalanceSheet, self).__init__(*args, **kwargs)


class CashFlow(Statement):
    def __init__(self, *args, **kwargs):
        super(CashFlow, self).__init__(*args, **kwargs)


class FinancialPerformance(object):
    def __init__(self,
                 symbol=None,
                 income_statements=None,
                 balance_sheets=None,
                 cash_flows=None):
        if not symbol:
            raise NotValidSymbolException

        self._income_statements = income_statements or []
        self._balance_sheets = balance_sheets or []
        self._cash_flows = cash_flows or []

    @property
    def income_statements(self):
        return self._income_statements

    @property
    def balance_sheets(self):
        return self._balance_sheets

    @property
    def cash_flows(self):
        return self._cash_flows

    def get_income_statement_by_year(self, year=None):
        """

        :param year:
        :return:
        """
        if not year:
            raise ValueError('Not a valid year')

        return [income for income in self._income_statements
                if income.year == int(year)][0]

    def get_balance_sheet_by_year(self, year=None):
        """

        :param year:
        :return:
        """
        if not year:
            raise ValueError('Not a valid year')

        return [bs for bs in self._balance_sheets
                if bs.year == int(year)][0]

    def get_cash_flow_by_year(self, year=None):
        """

        :param year:
        :return:
        """
        if not year:
            raise ValueError('Not a valid year')

        return [cf for cf in self._cash_flows
                if cf.year == int(year)][0]

    def return_on_asset(self, end_year=None):
        """

        :param end_year:
        :return:
        """
        if not end_year:
            return None

        try:
            income_statement = [income for income in self._income_statements
                                if income.year == end_year][0]
            balance_sheets = [bs for bs in self._balance_sheets
                              if int(bs.year) in [int(end_year),
                                                  int(end_year) - 1]]
        except IndexError:
            return None

        ebit = income_statement.ebit
        this_years_assets = balance_sheets[0].total_assets
        previous_years_assets = balance_sheets[1].total_assets
        average_total_assets = (this_years_assets + previous_years_assets) / 2
        return ebit / average_total_assets

    def return_on_equity(self, end_year=None):
        """

        :param end_year:
        :return:
        """
        if not end_year:
            return None

        try:
            income_statement = [income for income in self._income_statements
                                if income.year == end_year][0]
            balance_sheets = [bs for bs in self._balance_sheets
                              if int(bs.year) in [int(end_year),
                                                  int(end_year) - 1]]
        except IndexError:
            return None

        net_income = income_statement.net_income
        this_years_equity = balance_sheets[0].total_stockholder_equity
        previous_years_equity = balance_sheets[1].total_stockholder_equity
        equity = (this_years_equity + previous_years_equity) / 2
        return net_income / equity

    def profit_margin(self, end_year=None, use_ebit=False):
        """

        :param end_year:
        :param use_ebit:
        :return:
        """
        if not end_year:
            return None
        income_statement = [income for income in self._income_statements
                            if income.year == end_year][0]
        profit = income_statement.gross_profit
        if use_ebit:
            profit = income_statement.ebit

        return profit / income_statement.total_revenue
