from typing import Callable, Optional, Union, List, Any

import pandas
from pandas.core.groupby import DataFrameGroupBy

from pylow.data.attributes import Attribute, Dimension


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

    def get_variations_of(self, column: Union[str, Attribute]) -> List[Any]:
        """Returns all possible values for a given column

        Only makes sense to call this for columns
        TODO: Must be adapted to work with filtered data
        """
        col = getattr(column, 'col_name', column)
        return list(set(self.data[col]))

    def group_by(self, dimensions: List[Dimension]) -> DataFrameGroupBy:
        dimension_names = [d.col_name for d in dimensions]
        if len(dimension_names) == 0:
            # If no dimensions are given to group by, create grouping object based on no filter at all
            return self.data.groupby(lambda _: True)
        return self.data.groupby(dimension_names)

    @classmethod
    def from_csv(cls, filename: str, options: Optional[dict] = None) -> 'Datasource':
        if options is None:
            options = {
                'delimiter': ';',
                'quotechar': '"',
                'escapechar': '\\'
            }
        assert options is not None
        data = pandas.read_csv(filename, **options)
        datasource = cls(data)
        datasource._guess_types()
        return datasource


if __name__ == '__main__':
    ds = Datasource.from_csv('SalesJan2009.csv')
    ds.add_column('account_age', lambda x: x['Last_Login'] - x['Account_Created'])
    # print(ds.data.head)
