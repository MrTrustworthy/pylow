from typing import Callable, Optional, Union, List, Any, Dict

import pandas
from pandas.core.groupby import DataFrameGroupBy

from datapylot.data.attributes import Attribute, Dimension, Measure
from datapylot.logger import log


class Datasource:
    def __init__(self, data: pandas.DataFrame) -> None:
        self.data = data
        self._add_noc()
        log(self, 'Init Datasource')

    @property
    def columns(self) -> Dict[str, str]:
        """ Returns all available column headers with the associated data type
        """
        numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']

        def mapping(dtype):
            return 'Measure' if str(dtype) in numerics else 'Dimension'

        output = {col: mapping(self.data[col].dtype) for col in self.data.columns}
        return output

    def add_column(self, name: str, formula: Callable) -> None:
        self.data[name] = formula(self.data)

    def _add_noc(self) -> None:
        """ Adds a default 'number of rows' column so things like counts are possible
        """
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
        """ Performs a grouping based on all given dimensions and returns the result
        """
        log(self, f'grouping data bases on {dimensions}')
        dimension_names = [d.col_name for d in dimensions]
        if len(dimension_names) == 0:
            # If no dimensions are given to group by, create grouping object based on no filter at all
            return self.data.groupby(lambda _: True)
        return self.data.groupby(dimension_names)

    @classmethod
    def from_csv(cls, filename: str, options: Optional[dict] = None) -> 'Datasource':
        """ If given the path to a csv-file, read the file and return a datasource with its contents
        """
        log('Datasource_class', f'loading datasource from csv file {filename}')
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
