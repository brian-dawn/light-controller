#!/usr/bin/env python
# coding=utf-8
import sys
from time import sleep
from lifxlan import LifxLAN, WHITE, BLUE
from lifxlan.msgtypes import LightSetColor
from gpiozero import Button


def main():
    num_lights = None
    if len(sys.argv) != 2:
        print("\nDiscovery will go much faster if you provide the number of lights on your LAN:")
        print("  python {} <number of lights on LAN>\n".format(sys.argv[0]))
    else:
        num_lights = int(sys.argv[1])


    def say_hello():
        print("hello")

    a = Button(17)
    a.when_pressed = say_hello
    b = Button(27)
    c = Button(22)


    # instantiate LifxLAN client, num_lights may be None (unknown).
    # In fact, you don't need to provide LifxLAN with the number of bulbs at all.
    # lifx = LifxLAN() works just as well. Knowing the number of bulbs in advance
    # simply makes initial bulb discovery faster.
    print("Discovering lights...")
    lifx = LifxLAN(num_lights)
    lifx.set_power_all_lights(True)

    hue = 0 # 0 to 65535
    saturation = 0 # 0 to 65535
    brightness = 65535 # 0 to 65535
    temperature = 2500 # 2500 to 9000

    lifx.set_color_all_lights([hue, saturation, brightness, temperature ], 2000, True)





if __name__=="__main__":
    main()
