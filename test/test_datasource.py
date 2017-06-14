import pytest

from pylow.data import Datasource
from .testutils import TEST_FILE


def test_datasource_from_file_types():
    ds = Datasource.from_csv(TEST_FILE.absolute())
    assert ds.data.empty is False
    assert ds.data.shape == (300, 22) if 'min' in str(TEST_FILE) else (9994, 22)
    assert 'Number of records' in ds.data
    # pandas data types
    assert str(ds.data['Postal Code'].dtype) == 'int64'
    assert str(ds.data['Profit Ratio'].dtype) == 'object'
    assert str(ds.data['State'].dtype) == 'object'
    assert str(ds.data['Ship Date'].dtype) == 'datetime64[ns]'


def test_datasource_from_file_calcs_1():
    ds = Datasource.from_csv(TEST_FILE.absolute())
    # double the amount of measures
    target_sum = ds.data.shape[0] * 2
    ds.add_column('Test_Double', lambda x: 2)
    number = ds.data.Test_Double.sum()
    assert number == target_sum


def test_datasource_from_file_calcs_2():
    ds = Datasource.from_csv(TEST_FILE.absolute())
    # double the aggregated sum of Price
    target_sum = ds.data['Postal Code'].sum() * 2
    ds.add_column('Test_Double_Postal', lambda x: x['Postal Code'] * 2)
    number = ds.data['Test_Double_Postal'].sum()
    assert number == target_sum


def test_datasource_from_file_calcs_3():
    ds = Datasource.from_csv(TEST_FILE.absolute())
    # double the aggregated mean of Latitude for a subset of data
    target_sum = ds.data['Quantity'][:-200].mean() * 2
    ds.add_column('Test Quantity', lambda x: x['Quantity'] * 2)
    number = ds.data['Test Quantity'][:-200].mean()
    assert number == target_sum


def test_datasource_data_preparation():
    ds = Datasource.from_csv(TEST_FILE.absolute())
    # TODO More validation
    assert True

if __name__ == '__main__':
    pytest.main(['-s'])
