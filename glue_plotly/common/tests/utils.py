from numpy import zeros

from glue.core import Coordinates


class SimpleCoordinates(Coordinates):

    def __init__(self):
        super().__init__(pixel_n_dim=3, world_n_dim=3)

    def pixel_to_world_values(self, *args):
        return tuple([2.0 * p for p in args])

    def world_to_pixel_values(self, *args):
        return tuple([0.5 * w for w in args])

    @property
    def axis_correlation_matrix(self):
        matrix = zeros((self.world_n_dim, self.pixel_n_dim), dtype=bool)
        matrix[2, 2] = True
        matrix[0:2, 0:2] = True
        return matrix
