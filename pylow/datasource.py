
import pandas as pd



class Datasource:

    def __init__(self, data):
        self.data = data
        self.aspects = {}
        self._add_noc()

    def add_column(self, name, formula):
        self.data[name] = formula(self.data)

    def _add_noc(self):
        self.add_column('Number of records', lambda x: 1)

    def _guess_aspects(self):
        self.aspects = {}
        for column in self.data.columns:
            o_type = self.data[column].dtype.name
            self.aspects[column] = 'measure' if o_type in ('int64', 'float64') else 'dimension'

    def _guess_types(self):
        for column in self.data.columns:
            try:
                self.data[column] = pd.to_numeric(self.data[column])
            except ValueError:
                try:
                    self.data[column] = pd.to_datetime(self.data[column])
                except ValueError:
                    pass

    @classmethod
    def from_csv(cls, filename, options=None):
        if options is None:
            options = options = {
                'delimiter': ',',
                'quotechar': '"',
                'escapechar': '\\'
            }
        data = pd.read_csv(filename, **options)
        ds = cls(data)
        ds._guess_types()
        ds._guess_aspects()
        return ds

if __name__ == '__main__':
    ds = Datasource.from_csv('SalesJan2009.csv')
    ds.add_column('account_age', lambda x: x['Last_Login'] - x['Account_Created'])
    # print(ds.data.head)
