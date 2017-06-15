# def _get_size_data(self, current_val: Any, possible_vals: List[Any]) -> AVP:
#     if isinstance(self.config.size, Dimension):
#         # TODO FIXME currently, size only affects plot in one direction -> bigger, need to clamp this
#         size = possible_vals.index(current_val)
#         size_avp = AVP(self.config.size, (size + 1))
#         return size_avp
#     else:  # for measures
#         relative_in_range = reverse_lerp(current_val, possible_vals)  # between 0 and 1
#         # turn into value from 0.5 to 2
#         size_factor = (relative_in_range + 0.5) * (4/3)
#         size_avp = AVP(self.config.size, size_factor)
#         return size_avp
