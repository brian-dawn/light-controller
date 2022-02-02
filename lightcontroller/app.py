#!/usr/bin/env python
# coding=utf-8


from dataclasses import dataclass
from datetime import datetime
from re import S
import sys
import math
import random
from time import sleep, time
from lifxlan import LifxLAN, WHITE, BLUE
from lifxlan.msgtypes import LightSetColor
from gpiozero import Button


from lightcontroller import sun


def parse_time(s: str) -> int:
    """
    Given a date string e.g. 8:30pm 3:00am return the seconds
    into the day for that given time.

    NOTE: I know this incorrectly reports 12:00am, this code
    will not allow extreme daylight hours for my own sanity
    both IRL and in the code ;)
    """
    offset_hours = 0
    if "pm" in s:
        offset_hours = 12

    s = s.replace("pm", "").replace("am", "")
    [hour, minute] = [int(x) for x in s.split(":")]

    seconds_from_hour = (hour + offset_hours) * 60 * 60
    seconds_from_minute = minute * 60

    return seconds_from_hour + seconds_from_minute


# Important constants for setting sunrise/sunset.
sunrise = parse_time("6:00am")
sunset = parse_time("10:00pm")

print("sunrise: " + str(sunrise))
print("sunset: " + str(sunset))


transition_seconds = 60 * 30  # 30 minutes
orange_duration = 60 * 60 * 2  # 2 hours, we turn orange at night to prepare for sleep.

# When a user presses a button we will stop doing sun updates.
cooldown_time_in_seconds = 60 * 60  # one hour

sun_max_temp = 4500
sun_min_temp = 2500
max_value = 65535

# Brightness of turning on the light past sundown.
dim_brightness = 10000

temps_for_toggling = [
    2500,
    3500,
    5500,
    7500,
    9000,
]


def seconds_since_midnight() -> int:

    now = datetime.now()
    seconds_since_midnight = (
        now - now.replace(hour=0, minute=0, second=0, microsecond=0)
    ).total_seconds()
    return seconds_since_midnight


lifx = LifxLAN()
print("Discovering lights...")
lifx.set_power_all_lights(True)


@dataclass
class State:

    # If a button toggle is pressed on or off it will put the sunrise/sunset on cooldown
    hue = 0  # 0 to max_value
    saturation = 0  # 0 to max_value
    brightness = 0  # 0 to max_value
    temperature = 2500  # 2500 to 9000

    # Whenever a user presses a button we won't apply sunrise/sunset.
    last_button_press_time = 0

    party_mode = False

    temp_toggle_index = 0


state = State()


def set_color(
    hue: int, saturation: int, brightness: int, temperature: int, duration: int
):

    try:
        lifx.set_color_all_lights(
            [hue, saturation, brightness, temperature], duration, True
        )
    except Exception as e:
        # We might have lost connection, maybe retry?
        print(e)


def any_button_press():
    """
    Reset state
    """
    global state
    state.party_mode = False


def toggle_temp():
    global state

    any_button_press()

    # Add to cooldown.
    state.last_button_press_time = time()

    state.brightness = max_value
    state.saturation = 0
    state.hue = 0
    state.temperature = temps_for_toggling[state.temp_toggle_index]
    state.temp_toggle_index = (state.temp_toggle_index + 1) % len(temps_for_toggling)

    # Try multiple times in case failure, button presses are important.
    for _ in range(3):
        set_color(
            hue=state.hue,
            saturation=state.saturation,
            brightness=state.brightness,
            temperature=state.temperature,
            duration=500,
        )
        sleep(0.003)


def light_toggle():
    global state

    any_button_press()

    # Add to cooldown.
    state.last_button_press_time = time()

    sun_temperature = temp_over_time(seconds_since_midnight(), transition_seconds)
    if state.brightness == 0:
        # If it's at night turn it down just a tad.
        state.brightness = max(
            dim_brightness,
            brightness_over_time(seconds_since_midnight(), transition_seconds),
        )
        state.saturation = 0
        state.temperature = sun_temperature
    else:
        state.brightness = 0
        state.saturation = 0
        state.temperature = sun_temperature

    # Try multiple times in case failure, button presses are important.
    for _ in range(3):
        set_color(
            hue=state.hue,
            saturation=state.saturation,
            brightness=state.brightness,
            temperature=state.temperature,
            duration=500,
        )
        sleep(0.003)


def party_mode():

    global state

    any_button_press()

    state.party_mode = True
    state.last_button_press_time = time()


def temp_over_time(seconds_since_midnight: int, transition_seconds: int) -> int:

    # 0 to 1.
    intensity = sun.current_intensity(
        sunrise, sunset - orange_duration, seconds_since_midnight, transition_seconds
    )

    return int(sun_min_temp + (sun_max_temp - sun_min_temp) * intensity)


def brightness_over_time(seconds_since_midnight: int, transition_seconds: int) -> int:

    # 0 to 1.
    intensity = sun.current_intensity(
        sunrise,
        sunset,
        seconds_since_midnight,
        transition_seconds,
    )

    return int(max_value * intensity)


def main():
    global state

    # instantiate LifxLAN client, num_lights may be None (unknown).
    # In fact, you don't need to provide LifxLAN with the number of bulbs at all.
    # lifx = LifxLAN() works just as well. Knowing the number of bulbs in advance
    # simply makes initial bulb discovery faster.

    a = Button(17, pull_up=False)
    b = Button(27, pull_up=False)
    c = Button(22, pull_up=False)

    c.when_pressed = light_toggle
    b.when_pressed = toggle_temp
    a.when_pressed = party_mode

    # lifx.set_color_all_lights([hue, saturation, brightness, temperature ], 2000, True)

    while True:

        sleep(1)

        # Party mode only lasts for an hour
        while state.party_mode:
            print("party time")

            state.hue = int(time() * 1000 % max_value)
            state.saturation = max_value
            state.brightness = max_value
            state.temperature = 0

            set_color(
                hue=state.hue,
                saturation=state.saturation,
                brightness=state.brightness,
                temperature=state.temperature,
                duration=150,
            )
            sleep(0.150)

        # If we are past sunrise and before sunset begins we will disable sunrise/sunset.
        if (
            seconds_since_midnight() > sunrise + 5
            and seconds_since_midnight() < sunset - transition_seconds
        ):
            continue

        # If we pressed a button and the cooldown time hasn't passed then we won't
        # update the sunlight.
        if time() - state.last_button_press_time < cooldown_time_in_seconds:

            continue

        # Handle sunrise/sunset.
        current_time = seconds_since_midnight()
        # current_time = (current_time * 1000 ) % 86400

        state.hue = 0
        state.saturation = 0
        state.brightness = int(brightness_over_time(current_time, transition_seconds))
        state.temperature = int(temp_over_time(current_time, transition_seconds))
        print(state.temperature, state.brightness)

        set_color(
            hue=state.hue,
            saturation=state.saturation,
            brightness=state.brightness,
            temperature=state.temperature,
            duration=1000,
        )


if __name__ == "__main__":
    main()
