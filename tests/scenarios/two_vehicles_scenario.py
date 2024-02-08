import numpy as np
from plotly.subplots import make_subplots

from traffic_flow import models
from traffic_flow.simulation_helpers.vehicle_generator import VehiclesGenerator


def run_scenario() -> list[dict]:
    highway = models.Road((0, 0), (4_000, 0), "A4")
    roadmap = {"A4": highway}
    route = ["A4"]

    vehicles_generator = VehiclesGenerator()
    vehicles_generator.add_vehicle(route, 0.01)
    vehicles_generator.add_special_vehicle(route, 0, {"desired_velocity": 25}, {"position": 400})

    vehicles_specifications = vehicles_generator.vehicles_specifications

    two_vehicles_simulation = models.TrafficFlow(vehicles_specifications, roadmap)
    two_vehicles_simulation.total_time = 360

    two_vehicles_simulation.run()
    return two_vehicles_simulation.simulation_evolution


def plot_result(data):
    properties = ["position", "velocity", "acceleration"]
    car_names = ["Maluch", "Merol"]
    colors = ["green", "red"]
    fig = make_subplots(
        3, 1, shared_xaxes=True, row_titles=[_property.title() for _property in properties]
    )

    for k, car_data in enumerate(data):
        road_data = car_data["roads_data"]["A4"]
        time = np.arange(len(road_data.get("position"))) / 60  # type: ignore

        for n, _property in enumerate(properties):
            fig.add_scatter(
                x=time,
                y=road_data.get(_property)[0:-2],
                row=n + 1,
                col=1,
                name=car_names[k],
                marker_color=colors[k],
            )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Time (s)",
    )
    fig.show()


if __name__ == "__main__":
    simulation_evolution = run_scenario()

    plot_result(simulation_evolution)
