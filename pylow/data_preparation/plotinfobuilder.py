from itertools import chain
from typing import List

from pylow.data.vizconfig import VizConfig
from pylow.data_preparation.avp import AVP
from pylow.data_preparation.colorization_behaviour import ColorizationBehaviour
from pylow.data_preparation.plotinfo import PlotInfo


class PlotInfoBuilder:
    _plotinfo_cache = []

    @classmethod
    def create_all_plotinfos(cls, data: List[List[AVP]], config: VizConfig):
        """ The single public interface of PlotInfoBuilder

        Will take a list of AVP-Lists and create a list of PlotInfo objects from them
        """
        for dataset in data:
            cls._make_plot_info(dataset, config)

        output = cls._plotinfo_cache[:]
        cls._plotinfo_cache.clear()

        # sort data so that dimensions and measures stay grouped
        output.sort(key=lambda x: [avp.val for avp in chain(x.y_seps[::-1], x.x_seps[::-1])])
        return output

    @classmethod
    def _make_plot_info(cls, plot_data: List[AVP], config: VizConfig) -> None:
        """ Gathers the data necessary for a single PlotInfo object and creates it

        Will not return an object but rather put it into the _plotinfo_cache
        """
        find_index = config.all_attrs.index

        x_coords = [plot_data[find_index(config.last_column)]]
        y_coords = [plot_data[find_index(config.last_row)]]
        x_seps = [plot_data[find_index(col)] for col in config.previous_columns]
        y_seps = [plot_data[find_index(col)] for col in config.previous_rows]

        # gather additional data that is not used for X/Y placement of glyphs (eg. for colors and sizes)
        used_indicies = set(find_index(col) for col in config.rows + config.columns)
        all_indicies = set(range(len(plot_data)))
        additional_data_indicies = all_indicies - used_indicies
        additional_data = [plot_data[i] for i in additional_data_indicies]

        col_behaviour = ColorizationBehaviour.get_correct_behaviour(config)

        cls._create_new_or_update(x_coords, y_coords, x_seps, y_seps, additional_data, col_behaviour)

    @classmethod
    def _create_new_or_update(
            cls,
            x_coords: List[AVP],
            y_coords: List[AVP],
            x_seps: List[AVP],
            y_seps: List[AVP],
            additional_data: List[AVP],
            col_behaviour: ColorizationBehaviour
    ) -> None:
        """ Creates a new PlotInfo object or, if one already exists for those plot separators, extends it"""

        # create new object and determine of there are already fitting existing objects
        new_plotinfo = PlotInfo(x_coords, y_coords, x_seps, y_seps, additional_data, col_behaviour)
        existing_plotinfos = list(filter(lambda ppi: ppi.would_be_in_same_plot(new_plotinfo), cls._plotinfo_cache))

        if len(existing_plotinfos) == 0:
            # use the new object
            cls._plotinfo_cache.append(new_plotinfo)
        elif len(existing_plotinfos) == 1:
            # use an existing object and discard the newly created one
            existing = existing_plotinfos[0]
            existing.x_coords.extend(x_coords)
            existing.y_coords.extend(y_coords)
            existing.additional_data.extend(additional_data)

        else:
            # There should never be more than 1 existing object
            assert False, f'Already have {len(existing_plotinfos)} objects'
