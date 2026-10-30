"""Edge detection of affected areas on orthorectified tiles.

Flood:    water is dark, smooth, and low in saturation; with RGB only, use a
          normalised blue-green index  (G - R)/(G + R)  plus Otsu thresholding.
          With a NIR channel switch to NDWI = (G - NIR)/(G + NIR) (McFeeters 1996).
Wildfire: burn scar = large drop in a vegetation index between before/after
          tiles (dNBR if SWIR exists; with RGB, use excess-green change).
Active fire: thermal hotspots (reuse the thermal-sar-drone detector).
All outputs are masks + polygons-as-cells; the human analyst confirms.
"""
import numpy as np


def otsu(values, bins=256):
    """Otsu's threshold on a 1-D array (no skimage dependency)."""
    v = values[np.isfinite(values)]
    hist, edges = np.histogram(v, bins=bins)
    p = hist / hist.sum()
    omega = np.cumsum(p)
    mu = np.cumsum(p * (edges[:-1] + edges[1:]) / 2)
    mu_t = mu[-1]
    with np.errstate(divide="ignore", invalid="ignore"):
        sigma_b = (mu_t * omega - mu) ** 2 / (omega * (1 - omega))
    sigma_b = np.nan_to_num(sigma_b)
    # Every threshold inside an empty gap between modes is equally optimal: take the plateau's middle.
    best = np.flatnonzero(sigma_b >= sigma_b.max() * (1 - 1e-9))
    k = best[len(best) // 2]
    return edges[k + 1]


def box_mean(x, k=5):
    """k x k mean filter via summed-area table (denoise before per-pixel thresholds)."""
    r = k // 2
    p = np.pad(x, r, mode="edge")
    s = np.zeros((p.shape[0] + 1, p.shape[1] + 1))
    s[1:, 1:] = p.cumsum(0).cumsum(1)
    h, w = x.shape
    return (s[k:k + h, k:k + w] - s[:h, k:k + w] - s[k:k + h, :w] + s[:h, :w]) / (k * k)


def water_index(rgb, nir=None):
    r, g = rgb[..., 0].astype(float), rgb[..., 1].astype(float)
    if nir is not None:
        return (g - nir) / (g + nir + 1e-6)
    b = rgb[..., 2].astype(float)
    return (b + g - 2 * r) / (b + g + 2 * r + 1e-6)


def excess_green(rgb):
    s = rgb.astype(float).sum(-1) + 1e-6
    r, g, b = (rgb[..., i] / s for i in range(3))
    return 2 * g - r - b


def flood_mask(rgb, nir=None, min_index=0.0, smooth=5):
    wi = box_mean(water_index(rgb, nir), smooth) if smooth else water_index(rgb, nir)
    t = max(otsu(wi.ravel()), min_index)
    return wi > t


def burn_mask(before_rgb, after_rgb, min_drop=0.08, smooth=5):
    d = excess_green(before_rgb) - excess_green(after_rgb)
    d = box_mean(d, smooth) if smooth else d
    t = max(otsu(d.ravel()), min_drop)
    return d > t


def change(before_mask, after_mask):
    """New water / new burn: present after, absent before (removes rivers and lakes that were always there)."""
    return after_mask & ~before_mask
