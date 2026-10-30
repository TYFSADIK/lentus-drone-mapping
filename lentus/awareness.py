"""Live awareness map: aggregate tile detections into a coarse geo-grid with confidence and age.

Small enough to push over a degraded link (a 100 m cell grid of a 5x5 km area is 2500 cells,
and only changed cells are sent).
"""
import json
import math
import time


class AwarenessMap:
    def __init__(self, lat0, lon0, cell_m=100.0):
        self.lat0, self.lon0, self.cell = lat0, lon0, cell_m
        self.cells = {}       # (i, j) -> {kind, frac, conf, t, n}
        self.dirty = set()

    def _ij(self, lat, lon):
        n = math.radians(lat - self.lat0) * 6378137
        e = math.radians(lon - self.lon0) * 6378137 * math.cos(math.radians(self.lat0))
        return int(e // self.cell), int(n // self.cell)

    def add_tile(self, lat, lon, kind, affected_frac, conf, t=None):
        t = t or time.time()
        k = self._ij(lat, lon)
        c = self.cells.get(k)
        if c is None or c["kind"] != kind:
            c = {"kind": kind, "frac": 0.0, "conf": 0.0, "n": 0}
        n = c["n"]
        c.update(frac=(c["frac"] * n + affected_frac) / (n + 1), conf=max(c["conf"], conf), n=n + 1, t=t)
        self.cells[k] = c
        self.dirty.add(k)

    def _corner(self, i, j):
        lat = self.lat0 + math.degrees(j * self.cell / 6378137)
        lon = self.lon0 + math.degrees(i * self.cell / (6378137 * math.cos(math.radians(self.lat0))))
        return lon, lat

    def geojson(self, only_dirty=False, min_frac=0.05):
        keys = self.dirty if only_dirty else self.cells.keys()
        feats = []
        for (i, j) in keys:
            c = self.cells[(i, j)]
            if c["frac"] < min_frac:
                continue
            ring = [self._corner(i, j), self._corner(i + 1, j), self._corner(i + 1, j + 1), self._corner(i, j + 1), self._corner(i, j)]
            feats.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring]},
                          "properties": {**c, "cell": [i, j]}})
        if only_dirty:
            self.dirty.clear()
        return json.dumps({"type": "FeatureCollection", "features": feats})
