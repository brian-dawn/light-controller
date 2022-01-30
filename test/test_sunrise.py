from lightcontroller.sun import current_intensity


def test_sun_intensity():

    assert 0 == current_intensity(
        sunrise=100, sunset=200, seconds_since_midnight=90, transition_seconds=10
    )

    sunrise = current_intensity(
        sunrise=100, sunset=200, seconds_since_midnight=92, transition_seconds=10
    )
    assert sunrise > 0 and sunrise < 1

    assert 1 == current_intensity(
        sunrise=100, sunset=200, seconds_since_midnight=100, transition_seconds=10
    )

    assert 1 == current_intensity(
        sunrise=100, sunset=200, seconds_since_midnight=189, transition_seconds=10
    )

    sunset = current_intensity(
        sunrise=100, sunset=200, seconds_since_midnight=191, transition_seconds=10
    )

    assert sunset > 0 and sunset < 1

    assert 0 == current_intensity(
        sunrise=100, sunset=200, seconds_since_midnight=200, transition_seconds=10
    )

    assert 0 == current_intensity(
        sunrise=100, sunset=200, seconds_since_midnight=202, transition_seconds=10
    )
