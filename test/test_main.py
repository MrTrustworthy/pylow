import pathlib
import unittest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pylow

TESTDATA_PATH = pathlib.Path('test/data')  # as seen from project root


class ConfigTest(unittest.TestCase):

    def test_delete_clear(self):
        d = {
            'dimensions': [pylow.Dimension('Testcol')],
            'measures': [pylow.Measure('Testmeasure')]
        }
        pc = pylow.PlotConfig.from_dict(d)

        with self.assertRaises(AttributeError):
            pc.measures = []

        self.assertEqual(len(pc.dimensions), 1)
        self.assertEqual(len(pc.measures), 1)

        pc.clear(property='dimensions')
        self.assertEqual(len(pc.dimensions), 0)
        self.assertEqual(len(pc.measures), 1)

        pc.clear()
        self.assertEqual(len(pc.dimensions), 0)
        self.assertEqual(len(pc.measures), 0)

    def test_0_1_config(self):
        """ Generates config with 1 dimension and 1 measure and returns it for other tests"""
        d = {
            'dimensions': [],
            'measures': [pylow.Measure('Price', draw_type='bar', color='y')]
        }
        pc = pylow.PlotConfig.from_dict(d)
        self.assertEqual(len(pc.dimensions), 0)
        self.assertEqual(len(pc.measures), 1)
        return pc

    def test_0_2_config(self):
        """ Generates config with 1 dimension and 1 measure and returns it for other tests"""
        d = {
            'dimensions': [],
            'measures': [pylow.Measure('Price', draw_type='bar', color='y'), pylow.Measure('Number of records', draw_type='plot', color='b', options={'marker': 'o'})]
        }
        pc = pylow.PlotConfig.from_dict(d)
        self.assertEqual(len(pc.dimensions), 0)
        self.assertEqual(len(pc.measures), 2)
        return pc

    def test_1_1_config(self):
        """ Generates config with 1 dimension and 1 measure and returns it for other tests"""
        d = {
            'dimensions': [pylow.Dimension('Product')],
            'measures': [pylow.Measure('Price', draw_type='plot', color='r')]
        }
        pc = pylow.PlotConfig.from_dict(d)
        self.assertEqual(len(pc.dimensions), 1)
        self.assertEqual(len(pc.measures), 1)
        return pc

    def test_2_1_config(self):
        """ Generates config with 2 dimensions and 1 measure and returns it for other tests"""
        d = {
            'dimensions': [pylow.Dimension('Product'), pylow.Dimension('Payment_Type')],
            'measures': [pylow.Measure('Price', draw_type='plot')]
        }
        pc = pylow.PlotConfig.from_dict(d)
        self.assertEqual(len(pc.dimensions), 2)
        self.assertEqual(len(pc.measures), 1)
        return pc

    def test_1_2_config(self):
        """ Generates config with 1 dimension and 2 measures and returns it for other tests"""
        d = {
            'dimensions': [pylow.Dimension('Product')],
            'measures': [pylow.Measure('Price', aggregation='mean', draw_type='bar', color='r'), pylow.Measure('Number of records', draw_type='plot', color='b')]
        }
        pc = pylow.PlotConfig.from_dict(d)
        self.assertEqual(len(pc.dimensions), 1)
        self.assertEqual(len(pc.measures), 2)
        return pc

    def test_2_2_config(self):
        """ Generates config with 2 dimensions and 2 measures and returns it for other tests"""
        d = {
            'dimensions': [pylow.Dimension('Product'), pylow.Dimension('Payment_Type')],
            'measures': [pylow.Measure('Price', aggregation='mean', draw_type='bar', color='r'), pylow.Measure('Number of records', draw_type='plot', color='b')]
        }
        pc = pylow.PlotConfig.from_dict(d)
        self.assertEqual(len(pc.dimensions), 2)
        self.assertEqual(len(pc.measures), 2)
        return pc

    def test_invalid_config(self):
        pass


class MainTest(unittest.TestCase):

    def setUp(self):
        self.test_file = TESTDATA_PATH / 'SalesJan2009.csv'

    def test_example_0_1(self):
        config = ConfigTest().test_0_1_config()
        ds = pylow.Datasource.from_csv(self.test_file.absolute())
        plotter = pylow.Plotter(ds, config)
        frame = plotter.create_figure()
        plotter.display(frame, export_file='test/data/temp/test_0_1', wait=True)

    def test_example_0_2(self):
        config = ConfigTest().test_0_2_config()
        ds = pylow.Datasource.from_csv(self.test_file.absolute())
        plotter = pylow.Plotter(ds, config)
        frame = plotter.create_figure()
        plotter.display(frame, export_file='test/data/temp/test_0_2', wait=True)

    def test_example_1_1(self):
        config = ConfigTest().test_1_1_config()
        ds = pylow.Datasource.from_csv(self.test_file.absolute())
        plotter = pylow.Plotter(ds, config)
        frame = plotter.create_figure()
        plotter.display(frame, export_file='test/data/temp/test_1_1', wait=True)

    def test_example_2_1(self):
        config = ConfigTest().test_2_1_config()
        ds = pylow.Datasource.from_csv(self.test_file.absolute())
        plotter = pylow.Plotter(ds, config)
        frame = plotter.create_figure()
        plotter.display(frame, export_file='test/data/temp/test_2_1', wait=True)

    def test_example_1_2(self):
        config = ConfigTest().test_1_2_config()
        ds = pylow.Datasource.from_csv(self.test_file.absolute())
        plotter = pylow.Plotter(ds, config)
        frame = plotter.create_figure()
        plotter.display(frame, export_file='test/data/temp/test_1_2', wait=True)

    def test_example_2_2(self):
        config = ConfigTest().test_2_2_config()
        ds = pylow.Datasource.from_csv(self.test_file.absolute())
        plotter = pylow.Plotter(ds, config)
        frame = plotter.create_figure()
        plotter.display(frame, export_file='test/data/temp/test_2_2', wait=True)

    def test_config_constructor(self):
        conf = pylow.plot_config.PlotConfig()
        # TODO Specific tests once needed


class DatasourceTest(unittest.TestCase):

    def setUp(self):
        self.test_file = TESTDATA_PATH / 'SalesJan2009.csv'

    def test_datasource_from_file(self):
        ds = pylow.Datasource.from_csv(self.test_file.absolute())
        self.assertFalse(ds.data.empty)
        self.assertEqual(ds.data.shape, (998, 13))
        self.assertIn('Number of records', ds.data.dimensions)
        # pandas data types
        self.assertEqual(str(ds.data.Latitude.dtype), 'float64')
        self.assertEqual(str(ds.data.Product.dtype), 'object')
        self.assertEqual(str(ds.data.Transaction_date.dtype), 'datetime64[ns]')

    def test_datasource_from_file(self):
        ds = pylow.Datasource.from_csv(self.test_file.absolute())

        with self.subTest('Test custom calculated fields 1'):
            # double the amount of measures
            target_sum = ds.data.shape[0] * 2
            ds.add_column('Test_Double', lambda x: 2)
            number = ds.data.Test_Double.sum()
            self.assertEqual(number, target_sum)

        with self.subTest('Test custom calculated fields 2'):
            # double the aggregated sum of Price
            target_sum = ds.data.Price.sum() * 2
            ds.add_column('Test_Double_Price', lambda x: x['Price'] * 2)
            number = ds.data.Test_Double_Price.sum()
            self.assertEqual(number, target_sum)

        with self.subTest('Test custom calculated fields 3'):
            # double the aggregated mean of Latitude for a subset of data
            target_sum = ds.data.Latitude[:-200].mean() * 2
            ds.add_column('Test_Double_Latitude', lambda x: x['Latitude'] * 2)
            number = ds.data.Test_Double_Latitude[:-200].mean()
            self.assertEqual(number, target_sum)

if __name__ == '__main__':
    unittest.main()
    input()  # avoid closing all graphs immediately
