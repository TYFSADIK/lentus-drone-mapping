"""Photogrammetry survey planning: GSD, footprint, overlap -> line spacing and trigger distance."""
from dataclasses import dataclass
import math


@dataclass
class Camera:
    sensor_w_mm: float = 6.17     # 1/2.3" sensor (Pi HQ / small action cams; check yours)
    sensor_h_mm: float = 4.55
    focal_mm: float = 4.5
    img_w_px: int = 4056
    img_h_px: int = 3040


def gsd_cm(cam: Camera, agl_m: float) -> float:
    return cam.sensor_w_mm * agl_m * 100 / (cam.focal_mm * cam.img_w_px)


def footprint_m(cam: Camera, agl_m: float):
    return cam.sensor_w_mm * agl_m / cam.focal_mm, cam.sensor_h_mm * agl_m / cam.focal_mm


def plan(cam: Camera, agl_m: float, front_overlap=0.75, side_overlap=0.65, speed_ms=8.0):
    w, h = footprint_m(cam, agl_m)
    trigger = h * (1 - front_overlap)          # camera long side across-track
    spacing = w * (1 - side_overlap)
    return {"gsd_cm": round(gsd_cm(cam, agl_m), 2), "footprint_m": (round(w, 1), round(h, 1)),
            "line_spacing_m": round(spacing, 1), "trigger_m": round(trigger, 1),
            "trigger_s": round(trigger / speed_ms, 2), "max_speed_ms_for_2s_interval": round(trigger / 2.0, 1)}


def area_time_min(width_m, length_m, p, speed_ms=8.0, turn_s=8.0):
    lines = math.ceil(width_m / p["line_spacing_m"]) + 1
    return (lines * length_m / speed_ms + lines * turn_s) / 60
