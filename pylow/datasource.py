
from typing import Callable, List, Optional, Generator, Tuple

import pandas

from . import Dimension, Measure


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

    def get_prepared_data(
        self,
        dimensions: List[Dimension],
        measures: List[Measure]
    ) -> Generator[Tuple[Measure, 'pandas.Series'], None, None]:

        dimension_names = [d.col_name for d in dimensions]
        grouped_data = self.data.groupby(dimension_names)
        for measure in measures:
            grouped_measure = grouped_data[measure.col_name]
            aggregated_data = getattr(grouped_measure, measure.aggregation)().to_dict()  # is a pandas object
            yield measure, aggregated_data

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
