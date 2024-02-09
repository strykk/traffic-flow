import json
from pathlib import Path

import numpy as np

from traffic_flow import models
from traffic_flow.simulation_helpers.vehicle_generator import VehiclesGenerator


def prepare_scenario(
    street1_green_light_time: float, street2_green_light_time: float
) -> list[dict]:
    in_street1 = models.Road((0, 0), (2000, 0), "Street1")
    in_street2 = models.Road((0, 0), (2000, 0), "Street2")
    out_street = models.Road((0, 0), (2000, 0), "Street3")

    in_street1.add_next_road(out_street)
    in_street2.add_next_road(out_street)

    roadmap = {"Street1": in_street1, "Street2": in_street2, "Street3": out_street}
    route1 = ["Street1", "Street3"]
    route2 = ["Street2", "Street3"]

    traffic_lights = models.TrafficLights(
        [in_street1, in_street2],
        [street1_green_light_time, 2, street2_green_light_time, 2],
        [(True, False), (False, False), (False, True), (False, False)],  # type: ignore
        approaching_speed=5,
        slowing_down_distance=100,
        stopping_distance=30,
    )

    vehicles_generator = VehiclesGenerator({"desired_velocity": 15}, {"velocity": 15})

    street1_cars_start_times = list(np.arange(1, 151) * 5)
    street2_cars_start_times = list(np.arange(1, 76) * 10 + 0.1)

    vehicles_generator.add_vehicles(route1, list(street1_cars_start_times))
    vehicles_generator.add_vehicles(route2, list(street2_cars_start_times))

    vehicles_specifications = vehicles_generator.vehicles_specifications
    simulation = models.TrafficFlow(vehicles_specifications, roadmap, [traffic_lights])
    simulation.total_time = 72000

    simulation.run()

    return simulation.travel_times


def run_simulation():
    cycle_times = list(range(10, 61, 10))
    results = {}
    for street1_green_light in cycle_times:
        for street2_green_light in cycle_times:
            results[f"{street1_green_light}_{street2_green_light}"] = prepare_scenario(
                street1_green_light, street2_green_light
            )

    with open(Path("results", "simulation1.json"), "w") as file:
        json.dump(results, file)
