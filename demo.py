"""Run: python demo.py  -> plan a survey, detect new flood + burn scar on synthetic tiles, build the awareness map."""
import numpy as np

from lentus import detect, synthetic
from lentus.awareness import AwarenessMap
from lentus.survey import Camera, area_time_min, plan

p = plan(Camera(), agl_m=80)
print("survey plan @80 m:", p, f"-> 1x1 km in {area_time_min(1000, 1000, p):.0f} min")

before, river = synthetic.landscape()
after, truth_new_water = synthetic.flooded(before, river)
new_water = detect.change(detect.flood_mask(before), detect.flood_mask(after))
iou = (new_water & truth_new_water).sum() / (new_water | truth_new_water).sum()
print(f"flood: new-water IoU {iou:.2f}, affected {new_water.mean():.1%} of tile")

burnt, scar = synthetic.burned(before)
bm = detect.burn_mask(before, burnt)
print(f"burn scar IoU {(bm & scar).sum() / (bm | scar).sum():.2f}")

amap = AwarenessMap(45.40, -75.70, cell_m=100)
amap.add_tile(45.4004, -75.6995, "flood", float(new_water.mean()), conf=round(float(iou), 2))
amap.add_tile(45.4020, -75.6980, "burn", float(bm.mean()), conf=0.8)
print(amap.geojson(only_dirty=True)[:160], "...")
