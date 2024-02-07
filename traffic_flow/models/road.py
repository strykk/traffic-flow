import numpy as np


class Road:
    """Single lane of a road in a simulation

    For now, it's simply given by a start and an end point on a 2d grid.
    The scale is 1 -> 1 m.
    """

    def __init__(self, start_point: tuple[int, int], end_point: tuple[int, int]) -> None:

        self.start_point = start_point
        self.end_point = end_point
        self.length = self._calculate_road_length()  # length in meters

    def _calculate_road_length(self):
        return np.linalg.norm(np.array(self.start_point) - np.array(self.end_point))
