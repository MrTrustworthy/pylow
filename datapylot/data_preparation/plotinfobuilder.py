from itertools import chain
from typing import List

from datapylot.data.vizconfig import VizConfig, NoSuchAttributeException
from datapylot.data_preparation.avp import AVP
from datapylot.data_preparation.colorization_behaviour import ColorizationBehaviour
from datapylot.data_preparation.plotinfo import PlotInfo
from datapylot.data_preparation.sizing_behaviour import SizingBehaviour
from datapylot.logger import log


class PlotInfoBuilder:
    @classmethod
    def create_all_plotinfos(cls, data: List[List[AVP]], config: VizConfig):
        """ The single public interface of PlotInfoBuilder

        Will take a list of AVP-Lists and create a list of PlotInfo objects from them
        """
        log('PlotInfoBuilder_class', f'Creating all plot infos for {len(data)} rows of data [config is {config}]')
        plotinfo_cache: List[PlotInfo] = []

        for dataset in data:
            cls._make_plot_info(dataset, config, plotinfo_cache)

        # sort data so that dimensions and measures stay grouped
        plotinfo_cache.sort(key=lambda x: [avp.val for avp in chain(x.y_seps[::-1], x.x_seps[::-1])])
        return plotinfo_cache

    @classmethod
    def _make_plot_info(cls, plot_data: List[AVP], config: VizConfig, plotinfo_cache: List[PlotInfo]) -> None:
        """ Gathers the data necessary for a single PlotInfo object and creates it

        Will not return an object but rather put it into the plotinfo_cache
        """
        dims_and_measures = list(chain(config.dimensions, config.measures))
        find_index = dims_and_measures.index
        x_coords: List[AVP] = []  # default value, in case no values are there
        y_coords: List[AVP] = []  # default value, in case no values are there

        try:
            x_coords = [plot_data[find_index(config.x_data)]]
        except NoSuchAttributeException:
            pass
        try:
            y_coords = [plot_data[find_index(config.y_data)]]
        except NoSuchAttributeException:
            pass

        x_seps = [plot_data[find_index(col)] for col in config.x_separators]
        y_seps = [plot_data[find_index(col)] for col in config.y_separators]

        # gather additional data that is not used for X/Y placement of glyphs (eg. for colors and sizes)
        used_indicies = set(find_index(col) for col in config.rows + config.columns)
        all_indicies = set(range(len(plot_data)))
        additional_data_indicies = all_indicies - used_indicies
        additional_data = [plot_data[i] for i in additional_data_indicies]

        col_behaviour = ColorizationBehaviour.get_correct_behaviour(config, plotinfo_cache)
        size_behaviour = SizingBehaviour.get_correct_behaviour(config, plotinfo_cache)

        # create new object and determine if there are already fitting existing objects
        # TODO FIXME: Determine this without creating a new PlotInfo object for each
        existing_plotinfos = list(filter(lambda ppi: ppi.is_in_plot_of(x_seps, y_seps), plotinfo_cache))

        if len(existing_plotinfos) == 0:
            new_plotinfo = PlotInfo(x_coords, y_coords, x_seps, y_seps, additional_data, col_behaviour, size_behaviour)
            # use the new object
            log('PlotInfoBuilder_class', f'Created a new PlotInfo object as {new_plotinfo}')
            plotinfo_cache.append(new_plotinfo)
        elif len(existing_plotinfos) == 1:
            # use an existing object and discard the newly created one
            existing = existing_plotinfos[0]
            existing.x_coords.extend(x_coords)
            existing.y_coords.extend(y_coords)
            existing.additional_data.extend(additional_data)

        else:
            # There should never be more than 1 existing object
            assert False, f'Already have {len(existing_plotinfos)} objects'
