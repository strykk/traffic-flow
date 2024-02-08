import copy


class VehiclesGenerator:
    def __init__(
        self,
        default_vehicle_configs: dict | None = None,
        default_vehicle_starting_properties: dict | None = None,
    ) -> None:

        self._default_vehicle_specification = self._set_default_vehicle_specification(
            default_vehicle_configs, default_vehicle_starting_properties
        )

        self.vehicles_specifications = []

    def _gather_configs(
        self,
        vehicle_configs: dict | None,
        vehicle_starting_properties: dict | None,
    ) -> dict:
        gathered_configs = {}
        if vehicle_configs is not None:
            gathered_configs["vehicle_configs"] = vehicle_configs

        if vehicle_starting_properties is not None:
            gathered_configs["vehicle_starting_properties"] = vehicle_starting_properties
        return gathered_configs

    def _set_default_vehicle_specification(
        self,
        default_vehicle_configs: dict | None,
        default_vehicle_starting_properties: dict | None,
    ) -> dict:

        default_vehicle_specification = self._gather_configs(
            default_vehicle_configs, default_vehicle_starting_properties
        )

        return default_vehicle_specification

    def _copy_specifications(self, vehicle_specifications: dict | None = None):
        if vehicle_specifications is None:
            return copy.deepcopy(self._default_vehicle_specification)
        else:
            return copy.deepcopy(vehicle_specifications)

    def _add_vehicle(self, route, ride_start_time, vehicle_specifications: dict | None = None):
        vehicle_specifications = self._copy_specifications(vehicle_specifications)
        vehicle_specifications["route"] = route
        vehicle_specifications["ride_start_time"] = ride_start_time

        self.vehicles_specifications.append(vehicle_specifications)

    def add_vehicle(self, route, ride_start_time) -> None:
        self._add_vehicle(route, ride_start_time)

    def add_vehicles(self, route, ride_start_times: list[float]) -> None:
        for ride_start_time in ride_start_times:
            self.add_vehicle(route, ride_start_time)

    def add_special_vehicle(
        self, route, ride_start_time, vehicle_configs, vehicle_starting_properties
    ):
        vehicle_specifications = self._gather_configs(vehicle_configs, vehicle_starting_properties)
        self._add_vehicle(route, ride_start_time, vehicle_specifications)
