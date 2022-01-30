# %%
import math
import matplotlib.pyplot as plt

from sun import current_intensity

sun_max_temp = 4500
sun_min_temp = 2500

sunrise = 21600
sunset = 79200

seconds_per_day = 86400

# How long is the sunrise?
transition_seconds = 15000

xs = range(0, 86400, 100)
ys = [current_intensity(sunrise, sunset, x, transition_seconds) for x in xs]

plt.scatter(xs, ys)
plt.scatter(
    [sunrise - transition_seconds, sunset - transition_seconds, sunrise, sunset],
    [0, 1, 1, 0],
    color="red",
)
plt.show()

# %%
