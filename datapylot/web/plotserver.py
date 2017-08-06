from bokeh.embed import file_html, components
from bokeh.resources import CDN
from flask import Flask, render_template, request
from functools import lru_cache
from typing import List, Dict
from datapylot.data.attributes import Dimension, Measure, Attribute
from datapylot.data.datasource import Datasource
from datapylot.data.vizconfig import VizConfig
from datapylot.plotting.bokeh_plotter import Plotter

app = Flask(__name__)

# TODO: Only for developing the base implementation, replace this with filechooser
TEST_DS = 'test/data/testdata.csv'


@lru_cache(maxsize=64)
def get_cached_datasource(ds_name: str) -> Datasource:
    ds = Datasource.from_csv(ds_name)
    return ds


def get_datasource_attributes(ds_name: str) -> Dict[str, str]:
    return get_cached_datasource(ds_name).columns


def make_conf_from_form(data: Dict[str, str]) -> VizConfig:
    # only the base fields that are like "attribute_1"
    attributes = [k for k in data.keys() if k.count('_') <= 1]

    viz_dict = {
        'columns': [],
        'rows': []
    }
    singles = ['size', 'color']

    for attribute in attributes:
        col = data[attribute]
        _type = data[attribute + '_type']
        target = data[attribute + '_target'].split('_')[0]
        constructor = Measure if _type == 'Measure' else Dimension
        obj = constructor(col)
        if target not in singles:
            viz_dict[target].append(obj)
        else:
            viz_dict[target] = obj

    return VizConfig.from_dict(viz_dict)


@app.route('/', methods=['GET', 'POST'])
def root():
    # default values
    script, div = '', ''

    if request.method == 'POST':
        try:
            config = make_conf_from_form(request.form)
            ds = get_cached_datasource(TEST_DS)
            plotter = Plotter(ds, config)
            plotter.create_viz()
            grid = plotter.get_output()
            script, div = components(grid)
        except Exception as e:
            div = f'Could not process request due to {e}. Is this a valid plot configuration?'

    return render_template(
        'ui.html',
        attributes=get_cached_datasource(TEST_DS).columns,
        bokeh_script=script,
        bokeh_div=div
    )


if __name__ == '__main__':
    app.run(port=8081)
