class Vehicle:
    """Single agent in a simulation

    A vehicle is defined by a set of parameters required by the model
    (references will be placed in README).
    """

    def __init__(self) -> None:
        # For now, the vehicle params are hardcoded. The values are
        # from the original paper. In the comment, the symbol and the unit.
        self.length = 5  # l, m
        self.desired_velocity = 33.333  # v0, m/s
        self.maximum_acceleration = 0.73  # a, m/s²
        self.desired_deceleration = 1.67  # b, m/s²,
        self.mininimal_desired_distance = 2  # s0, m
        self.acceleration_exponent = 4  # delta
        self.driver_reaction_time = 1.6  # T, s
