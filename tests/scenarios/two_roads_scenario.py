import numpy as np
from plotly.subplots import make_subplots

from traffic_flow import models
from traffic_flow.simulation_helpers.vehicle_generator import VehiclesGenerator


def run_scenario() -> list[dict]:
    highway = models.Road((0, 0), (2_000, 0), "A4")
    highway_back = models.Road((2_000, 0), (0, 0), "A4-back")
    highway.add_next_road(highway_back)

    roadmap = {"A4": highway, "A4-back": highway_back}
    route = ["A4", "A4-back"]

    vehicles_generator = VehiclesGenerator()
    vehicles_generator.add_vehicle(route, 0)
    vehicles_specifications = vehicles_generator.vehicles_specifications

    single_vehicle_simulation = models.TrafficFlow(vehicles_specifications, roadmap)
    single_vehicle_simulation.total_time = 240

    single_vehicle_simulation.run()
    return single_vehicle_simulation.simulation_evolution


def process_simulation_evolution(
    simulation_evolution: list[dict],
) -> dict[str, list]:

    clean_data = simulation_evolution.pop()["roads_data"]
    return clean_data


def plot_result(data):
    properties = ["position", "velocity", "acceleration"]
    fig = make_subplots(
        3, 2, shared_xaxes=True, row_titles=[_property.title() for _property in properties]
    )

    for k, road_data in enumerate(data.values()):
        time = np.arange(len(road_data.get("position"))) / 60  # type: ignore

        for n, _property in enumerate(properties):
            fig.add_scatter(
                x=time, y=road_data.get(_property), row=n + 1, col=k + 1, showlegend=False
            )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Time (s)",
        xaxis2_title="Time (s)",
        yaxis4_range=(0, 33.333),
        yaxis5_range=(0, 0.8),
        yaxis6_range=(0, 0.8),
    )
    fig.show()


if __name__ == "__main__":
    simulation_evolution = run_scenario()
    clean_data = process_simulation_evolution(simulation_evolution)

    plot_result(clean_data)
