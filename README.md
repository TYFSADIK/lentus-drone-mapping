# LENTUS-Style Disaster Response Drone Mapping (simulation first)

Private research repo. Simulated drone flights in ArduPilot SITL and Gazebo map floods or wildfires. Edge computer vision detects affected areas and feeds a live awareness map. Inspired by Operation LENTUS, the CAF's framework for supporting civil authorities.

Full write-up: [`docs/project-page.md`](docs/project-page.md)

## What's here

| File | Purpose |
|---|---|
| `lentus/survey.py` | GSD, footprint, line spacing and trigger distance from overlap, area flight time |
| `lentus/detect.py` | Water index (RGB, or **NDWI** with NIR), excess-green burn scar, **Otsu** thresholds, before/after change (ignores rivers that were always there) |
| `lentus/awareness.py` | 100 m awareness grid with confidence and age. Sends only changed cells as GeoJSON, which suits degraded links |
| `lentus/synthetic.py` | Synthetic tiles (river, flood, burn scar) with ground truth for IoU |
| `sitl/fly_survey.py` | Uploads a lawnmower mission with distance-based camera triggers to ArduPilot SITL (pymavlink) |

## Quickstart

```bash
pip install numpy
python demo.py && python -m unittest -v
```

## Next steps
- [ ] Gazebo world with a flood plane and a burn texture, and the camera plugin publishing images, so detections run in the loop
- [ ] Orthorectify each frame with pose (reuse `thermal-sar-drone/sar/georef.py` for footprints), or batch-process with OpenDroneMap
- [ ] Jetson or Hailo segmentation model (U-Net on FloodNet or similar) as the ML upgrade, keeping Otsu as a baseline to compare
- [ ] Send `geojson(only_dirty=True)` through the `ddil-proof-devops` outbox to a TAK or web map
- [ ] Score IoU against hand-labelled masks from a public flood dataset
