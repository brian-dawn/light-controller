import math


def current_intensity(
    sunrise: int, sunset: int, seconds_since_midnight: int, transition_seconds: int
) -> float:

    # Sun is at 1 by sunrise.
    start_point = sunrise - transition_seconds

    # Sun is at 0 by sunset
    sunset_start_point = sunset - transition_seconds

    if (
        seconds_since_midnight >= sunrise
        and seconds_since_midnight <= sunset_start_point
    ):
        return 1.0

    # Generate the first half of a sin wave from the start to end.
    # when inner is -pi then it's 0
    if seconds_since_midnight > start_point and seconds_since_midnight < sunrise:
        return (
            math.cos(
                math.pi
                - math.pi * (seconds_since_midnight - start_point) / transition_seconds
            )
            * 0.5
            + 0.5
        )

    if seconds_since_midnight > sunset_start_point and seconds_since_midnight < sunset:
        return (
            math.cos(
                math.pi
                * (seconds_since_midnight - sunset_start_point)
                / transition_seconds
            )
            * 0.5
            + 0.5
        )

    return 0.0
