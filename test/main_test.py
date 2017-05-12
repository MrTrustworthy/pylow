import pathlib
import time
import unittest

from import_hook import pylow

TESTDATA_PATH = pathlib.Path('test/data')  # as seen from project root


class ConfigTest(unittest.TestCase):

    def test_delete_clear(self):
        d = {
            'columns': [pylow.ConfigAttribute('Testcol', 'dimension')],
            'rows': [pylow.ConfigAttribute('Testrow', 'measure')],
            'aggregations': ['sum'],  # callable on pandas.grouped, in [mean, sum, max, min]
            'draw_types': ['bar'],  # depends on cols or rows?
            'colors': ['b'],
        }
        pc = pylow.PlotConfig.from_dict(d)

        with self.assertRaises(AttributeError):
            pc.rows = []

        for key in d.keys():
            self.assertEqual(len(getattr(pc, key)), 1)

        pc.clear(property='columns')
        for key in d.keys():
            if key == 'columns':
                self.assertEqual(len(getattr(pc, key)), 0)
            else:
                self.assertEqual(len(getattr(pc, key)), 1)

        pc.clear()
        for key in d.keys():
            self.assertEqual(len(getattr(pc, key)), 0)

    def test_2_1_config(self):
        """ Generates config with 2 columns and 1 row and returns it for other tests"""
        d = {
            'columns': [pylow.ConfigAttribute('Product', 'dimension'), pylow.ConfigAttribute('Payment_Type', 'dimension')],
            'rows': [pylow.ConfigAttribute('Price', 'measure')],
            'aggregations': ['sum'],  # callable on pandas.grouped, in [mean, sum, max, min]
            'draw_types': ['bar'],  # depends on cols or rows?
            'colors': ['b'],
        }
        pc = pylow.PlotConfig.from_dict(d)
        for key in d.keys():
            if key == 'columns':
                self.assertEqual(len(getattr(pc, key)), 2)
            else:
                self.assertEqual(len(getattr(pc, key)), 1)
        return pc

    def test_invalid_config(self):
        pass


class MainTest(unittest.TestCase):

    def setUp(self):
        self.test_file = TESTDATA_PATH / 'SalesJan2009.csv'

    def test_example(self):
        config = ConfigTest().test_2_1_config()
        ds = pylow.Datasource.from_csv(self.test_file.absolute())
        self.plotter = pylow.Plotter(ds, config)
        frame = self.plotter.create_frame()
        self.plotter.display(frame, export_file='test/data/temp/test_2_1')
        time.sleep(1)

    def test_config_constructor(self):
        pass
        # conf = pylow.plot_config.PlotConfig()


class DatasourceTest(unittest.TestCase):

    def setUp(self):
        self.test_file = TESTDATA_PATH / 'SalesJan2009.csv'

    def test_datasource_from_file(self):
        ds = pylow.Datasource.from_csv(self.test_file.absolute())
        self.assertFalse(ds.data.empty)
        self.assertEqual(ds.data.shape, (998, 13))
        self.assertIn('Number of records', ds.data.columns)
        # pandas data types
        self.assertEqual(str(ds.data.Latitude.dtype), 'float64')
        self.assertEqual(str(ds.data.Product.dtype), 'object')
        self.assertEqual(str(ds.data.Transaction_date.dtype), 'datetime64[ns]')

    def test_datasource_from_file(self):
        ds = pylow.Datasource.from_csv(self.test_file.absolute())

        # double the amount of rows
        target_sum = ds.data.shape[0] * 2
        ds.add_column('Test_Double', lambda x: 2)
        number = ds.data.Test_Double.sum()
        self.assertEqual(number, target_sum)

        # double the aggregated sum of Price
        target_sum = ds.data.Price.sum() * 2
        ds.add_column('Test_Double_Price', lambda x: x['Price'] * 2)
        number = ds.data.Test_Double_Price.sum()
        self.assertEqual(number, target_sum)

        # double the aggregated mean of Latitude for a subset of data
        target_sum = ds.data.Latitude[:-200].mean() * 2
        ds.add_column('Test_Double_Latitude', lambda x: x['Latitude'] * 2)
        number = ds.data.Test_Double_Latitude[:-200].mean()
        self.assertEqual(number, target_sum)

if __name__ == '__main__':
    unittest.main()
