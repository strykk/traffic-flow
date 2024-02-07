from traffic_flow.models.road import Road


class TrafficFlow:
    """Single simulation of a traffic flow"""

    def __init__(self) -> None:
        self.time_step = 1 / 60  # seconds
        self.total_time = 600  # seconds

        self.roads: list[Road] = []
