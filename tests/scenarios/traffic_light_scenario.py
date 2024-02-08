from collections import defaultdict

import numpy as np
from plotly.subplots import make_subplots

from traffic_flow import models
from traffic_flow.simulation_helpers.vehicle_generator import VehiclesGenerator


def run_scenario() -> list[dict]:
    in_street1 = models.Road((0, 0), (400, 0), "Street1")
    out_street = models.Road((0, 0), (200, 0), "Street3")

    in_street1.add_next_road(out_street)

    roadmap = {"Street1": in_street1, "Street3": out_street}
    route1 = ["Street1", "Street3"]

    traffic_lights = models.TrafficLights(
        [in_street1],
        [15, 20],
        [
            (True,),
            (False,),
        ],  # type: ignore
        approaching_speed=5,
        slowing_down_distance=100,
        stopping_distance=30,
    )

    vehicles_generator = VehiclesGenerator({"desired_velocity": 15}, {"velocity": 15})

    vehicles_generator.add_vehicle(route1, 0)

    vehicles_specifications = vehicles_generator.vehicles_specifications
    two_vehicles_simulation = models.TrafficFlow(
        vehicles_specifications, roadmap, [traffic_lights]
    )
    two_vehicles_simulation.total_time = 120

    two_vehicles_simulation.run()
    return two_vehicles_simulation.simulation_evolution


def plot_result(data):
    properties = ["position", "velocity", "acceleration"]
    colors = ["green", "red"]
    fig = make_subplots(
        3,
        2,
        shared_xaxes=True,
        row_titles=[_property.title() for _property in properties],
        column_titles=["Street1", "Street3"],
    )

    car_data = data.pop()["roads_data"]
    for k, (street_name, street_data) in enumerate(car_data.items()):
        clean_data = street_data

        time = np.arange(len(clean_data.get("position"))) / 60  # type: ignore
        for n, _property in enumerate(properties):
            fig.add_scatter(
                x=time,
                y=clean_data.get(_property),
                row=n + 1,
                col=k + 1,
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
