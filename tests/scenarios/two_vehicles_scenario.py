import numpy as np
from plotly.subplots import make_subplots

from traffic_flow import models


def run_scenario() -> list[dict]:
    highway = models.Road((0, 0), (4_000, 0), "A4")
    route = [highway]
    vehicle2 = models.Vehicle(route)
    vehicle1 = models.Vehicle(route)

    vehicle2.position = 400
    vehicle2.desired_velocity = 25

    two_vehicles_simulation = models.TrafficFlow()
    two_vehicles_simulation.total_time = 180
    two_vehicles_simulation.add_vehicle(vehicle2)
    two_vehicles_simulation.add_vehicle(vehicle1)

    two_vehicles_simulation.run()
    return two_vehicles_simulation.simulation_evolution


def plot_result(data):
    properties = ["position", "velocity", "acceleration"]
    car_names = ["Maluch", "Merol"]

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
            )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Time (s)",
    )
    fig.show()


if __name__ == "__main__":
    simulation_evolution = run_scenario()

    plot_result(simulation_evolution)
