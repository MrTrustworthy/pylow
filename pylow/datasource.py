
from typing import Callable, Optional

import pandas


class Datasource:

    def __init__(self, data: pandas.DataFrame) -> None:
        self.data = data
        self._add_noc()

    def add_column(self, name: str, formula: Callable) -> None:
        self.data[name] = formula(self.data)

    def _add_noc(self) -> None:
        self.add_column('Number of records', lambda x: 1)

    def _guess_types(self) -> None:
        # TODO handle fields with percentage signs
        for column in self.data.columns:
            try:
                self.data[column] = pandas.to_numeric(self.data[column])
            except ValueError:
                try:
                    self.data[column] = pandas.to_datetime(self.data[column])
                except ValueError:
                    pass

    @classmethod
    def from_csv(cls, filename: str, options: Optional[dict]=None) -> 'Datasource':
        if options is None:
            options = options = {
                'delimiter': ';',
                'quotechar': '"',
                'escapechar': '\\'
            }
        data = pandas.read_csv(filename, **options)
        ds = cls(data)
        ds._guess_types()
        return ds

if __name__ == '__main__':
    ds = Datasource.from_csv('SalesJan2009.csv')
    ds.add_column('account_age', lambda x: x['Last_Login'] - x['Account_Created'])
    # print(ds.data.head)
