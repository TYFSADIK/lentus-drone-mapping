"""Synthetic RGB tiles: fields + a river, then a flood (river widens) or a burn scar."""
import numpy as np


def landscape(h=200, w=200, rng=None):
    rng = rng or np.random.default_rng(0)
    img = np.zeros((h, w, 3))
    img[...] = (0.30, 0.45, 0.20)                       # vegetation
    img += rng.normal(0, 0.03, img.shape)
    yy, xx = np.mgrid[0:h, 0:w]
    river = np.abs(xx - (w / 2 + 15 * np.sin(yy / 25))) < 6
    img[river] = (0.15, 0.25, 0.35)
    return np.clip(img, 0, 1), river


def flooded(img, river, extra_px=25):
    h, w, _ = img.shape
    yy, xx = np.mgrid[0:h, 0:w]
    centre = w / 2 + 15 * np.sin(yy / 25)
    flood = (np.abs(xx - centre) < 6 + extra_px) & (yy > h * 0.3)
    out = img.copy()
    out[flood] = (0.20, 0.27, 0.33)                     # muddy floodwater
    return out, flood & ~river


def burned(img, centre=(60, 60), r=35):
    h, w, _ = img.shape
    yy, xx = np.mgrid[0:h, 0:w]
    scar = np.hypot(yy - centre[0], xx - centre[1]) < r
    out = img.copy()
    out[scar] = (0.22, 0.20, 0.18)
    return out, scar
