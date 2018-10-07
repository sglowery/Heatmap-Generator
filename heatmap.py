# heatmap written by Stephen Lowery
# Github: sglowery
# Email: stephen.g.lowery@gmail.com


import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter
import csv


DUMMY_DATA = "dummy_data.csv"

DEFAULT_MAX_SCORE = 30
DEFAULT_SIGMA = 1.2
DEFAULT_COLORMAP = plt.get_cmap("jet")


# This method generates a list of randomized data meant to look like coordinate pairs representing two grades from two
# tests by one student each
def rand_data(file=DUMMY_DATA, num=10**3, xrange=(0, 101), yrange=(0, 101)):
    with open(file, mode="w") as f:
        result = ""
        for i in range(num):
            result += "{0},{1}\n".format(np.random.randint(*xrange), np.random.randint(*yrange))
        f.write(result)


def gen_heatmap(file=DUMMY_DATA, max_score=DEFAULT_MAX_SCORE, sigma=DEFAULT_SIGMA, colormap=DEFAULT_COLORMAP):
    x, y = [], []
    with open(file) as data:
        if ".csv" in file:
            for line in csv.reader(data):
                x.append(int(line[0]))
                y.append(int(line[1]))
        else:
            for line in data:
                scores = line.split(",")
                x.append(int(scores[0]))
                y.append(int(scores[1]))

    max_score = max(max_score, *x, *y)
    heatmap, xedges, yedges = np.histogram2d(x, y, bins=(max_score+1, max_score+1))
    # the +1 makes the bin number inclusive since scores at 0 and at the max are allowed in the interval
    extent = [0, max_score, 0, max_score]

    heatmap = gaussian_filter(heatmap, sigma=sigma)

    plt.clf()
    plt.imshow(heatmap.T, extent=extent, origin='lower', cmap=colormap)
    plt.show()
