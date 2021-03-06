import pathlib
import warnings

from bokeh.io import save

from datapylot.data import Datasource

TEMP_FOLDER = pathlib.Path('test/temp')
TESTDATA_PATH = pathlib.Path('test/data')  # as seen from project root
TEST_FILE = TESTDATA_PATH / 'testdata.csv'
DATASOURCE = Datasource.from_csv(str(TEST_FILE.absolute()))


def save_plot_temp(plot, name):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        save(plot, TEMP_FOLDER / f'{name}.html')


def get_plot_temp(name):
    return TEMP_FOLDER / f'{name}.html'
