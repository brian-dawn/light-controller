#!/usr/bin/env python
# coding=utf-8


from datetime import datetime
import sys
import math
import random
from time import sleep, time
from lifxlan import LifxLAN, WHITE, BLUE
from lifxlan.msgtypes import LightSetColor
from gpiozero import Button


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


transition_seconds = 60 * 60  # 60 minutes

# When a user presses a button we will stop doing sun updates.
cooldown_time_in_seconds = 60 * 60  # one hour

sun_max_temp = 4500
sun_min_temp = 2500


def seconds_since_midnight() -> int:

    now = datetime.now()
    seconds_since_midnight = (
        now - now.replace(hour=0, minute=0, second=0, microsecond=0)
    ).total_seconds()
    return seconds_since_midnight


lifx = LifxLAN()
print("Discovering lights...")
lifx.set_power_all_lights(True)

# If a button toggle is pressed on or off it will put the sunrise/sunset on cooldown
hue = 0  # 0 to 65535
saturation = 0  # 0 to 65535
brightness = 0  # 0 to 65535
temperature = 2500  # 2500 to 9000


# Whenever a user presses a button we won't apply sunrise/sunset.
last_button_press_time = 0

party_start_time = 0


def any_button_press():
    """
    Reset state
    """
    global party_start_time
    party_start_time = 0


def light_toggle():
    global brightness, saturation, hue, temperature, last_button_press_time

    any_button_press()

    last_button_press_time = time()
    if brightness == 0:
        brightness = 65535
        saturation = 0
        temperature = int(temp_over_time(seconds_since_midnight(), sunrise, sunset))
    else:
        brightness = 0

    lifx.set_color_all_lights([hue, saturation, brightness, temperature], 500, True)


def party_mode():
    global party_start_time
    global brightness, saturation, hue, temperature, last_button_press_time

    any_button_press()

    party_start_time = time()
    last_button_press_time = time()
    # hue = random.randint(0, 65535)  # 0 to 65535
    # saturation = 65535  # 0 to 65535
    # brightness = 65535  # 0 to 65535

    # lifx.set_color_all_lights([hue, saturation, brightness, temperature], 500, True)


def sunrise_temperature_over_time(seconds_since_midnight, sunrise_time):

    inner = (seconds_since_midnight - sunrise_time) / (
        transition_seconds / (2 * math.pi)
    )

    if inner < -math.pi:
        return sun_min_temp

    if inner > 0:
        return sun_max_temp

    v = (sun_max_temp - sun_min_temp) * math.cos(inner) + sun_min_temp

    return max(sun_min_temp, min(v, sun_max_temp))


def sunset_temperature_over_time(seconds_since_midnight, sunset_seconds):

    return (
        sun_max_temp
        - sunrise_temperature_over_time(seconds_since_midnight, sunset_seconds)
        + sun_min_temp
    )


def temp_over_time(seconds_since_midnight, sunrise_seconds, sunset_seconds):
    return min(
        sunrise_temperature_over_time(seconds_since_midnight, sunrise_seconds*2),
        sunset_temperature_over_time(seconds_since_midnight, sunset_seconds*2),
    )


def brightness_over_time(seconds_since_midnight, sunrise_seconds, sunset_seconds):

    return 65535 * (
        (
            temp_over_time(seconds_since_midnight, sunrise_seconds, sunset_seconds)
            - sun_min_temp
        )
        / (sun_max_temp - sun_min_temp)
    )


def main():

    # instantiate LifxLAN client, num_lights may be None (unknown).
    # In fact, you don't need to provide LifxLAN with the number of bulbs at all.
    # lifx = LifxLAN() works just as well. Knowing the number of bulbs in advance
    # simply makes initial bulb discovery faster.

    a = Button(17, pull_up=False)
    b = Button(27, pull_up=False)
    c = Button(22, pull_up=False)

    c.when_pressed = light_toggle
    # b.when_pressed = lights_on
    a.when_pressed = party_mode

    # lifx.set_color_all_lights([hue, saturation, brightness, temperature ], 2000, True)

    while True:
        sleep(1)

        # Party mode only lasts for an hour
        if time() - party_start_time < 60 * 60:
            print("party time")

            hue = int(time() * 4000 % 65535)
            saturation = 65535
            brightness = 65535
            temperature = 0

            lifx.set_color_all_lights(
                [hue, saturation, brightness, temperature], 1000, True
            )
            continue

        # If we pressed a button and the cooldown time hasn't passed then we won't
        # update the sunlight.
        if time() - last_button_press_time < cooldown_time_in_seconds:

            continue

        # Handle sunrise/sunset.
        current_time = seconds_since_midnight()
        # current_time = (current_time * 1000 ) % 86400

        hue = 0
        saturation = 0
        brightness = int(brightness_over_time(current_time, sunrise, sunset))
        temperature = int(temp_over_time(current_time, sunrise, sunset))
        print(temperature, brightness)

        lifx.set_color_all_lights(
            [hue, saturation, brightness, temperature], 1000, True
        )


if __name__ == "__main__":
    main()
