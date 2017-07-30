from bokeh.embed import file_html
from bokeh.resources import CDN
from flask import Flask, render_template, request

from datapylot.data.attributes import Dimension, Measure
from datapylot.data.datasource import Datasource
from datapylot.data.vizconfig import VizConfig
from datapylot.plotting.bokeh_plotter import Plotter

app = Flask(__name__)

# TODO: Only for developing the base implementation, replace this with filechooser
ds_name = '../../test/data/testdata.csv'
DATASOURCE = Datasource.from_csv(ds_name)


def get_datasource_attributes(ds_name=''):
    return DATASOURCE.columns


def make_conf(data):
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


@app.route('/')
def root():
    return render_template('ui.html', attributes=get_datasource_attributes())


@app.route('/recalculate', methods=['POST'])
def recalculate():
    try:
        config = make_conf(request.form)
        plotter = Plotter(DATASOURCE, config)
        plotter.create_viz()
        grid = plotter.get_output()
        return file_html(grid, CDN)

    except Exception as e:
        return f'Could not process request due to {e}. Is this a valid plot configuration?'


if __name__ == '__main__':
    app.run(port=8081)
