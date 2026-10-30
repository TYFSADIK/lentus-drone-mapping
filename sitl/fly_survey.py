"""Fly a lawnmower survey in ArduPilot SITL (Copter) with camera triggers by distance.

    sim_vehicle.py -v ArduCopter --console --map     # in one terminal
    python sitl/fly_survey.py --agl 80 --width 400 --length 600
Gazebo (ardupilot_gazebo + a camera plugin) provides images for the detector.
"""
import argparse
import math
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lentus.survey import Camera, plan  # noqa: E402


def main():
    from pymavlink import mavutil
    ap = argparse.ArgumentParser()
    ap.add_argument("--conn", default="udp:127.0.0.1:14550")
    ap.add_argument("--agl", type=float, default=80)
    ap.add_argument("--width", type=float, default=400)
    ap.add_argument("--length", type=float, default=600)
    a = ap.parse_args()
    p = plan(Camera(), a.agl)
    m = mavutil.mavlink_connection(a.conn)
    m.wait_heartbeat()
    pos = m.recv_match(type="GLOBAL_POSITION_INT", blocking=True)
    lat0, lon0 = pos.lat / 1e7, pos.lon / 1e7
    items = [(mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, lat0, lon0, a.agl),
             (mavutil.mavlink.MAV_CMD_DO_SET_CAM_TRIGG_DIST, p["trigger_m"], 0, 1, 0, 0, 0, 0)]
    n_lines = int(a.width // p["line_spacing_m"]) + 1
    for i in range(n_lines):
        e = i * p["line_spacing_m"]
        for nn in ((0, a.length) if i % 2 == 0 else (a.length, 0)):
            lat = lat0 + math.degrees(nn / 6378137)
            lon = lon0 + math.degrees(e / (6378137 * math.cos(math.radians(lat0))))
            items.append((mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, lat, lon, a.agl))
    items += [(mavutil.mavlink.MAV_CMD_DO_SET_CAM_TRIGG_DIST, 0, 0, 0, 0, 0, 0, 0),
              (mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0)]
    m.waypoint_clear_all_send()
    m.waypoint_count_send(len(items) + 1)
    for seq in range(len(items) + 1):
        req = m.recv_match(type=["MISSION_REQUEST", "MISSION_REQUEST_INT"], blocking=True)
        cmd, p1, p2, p3, p4, x, y, z = items[req.seq - 1] if req.seq else (16, 0, 0, 0, 0, lat0, lon0, 0)
        m.mav.mission_item_int_send(m.target_system, m.target_component, req.seq,
                                    mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, cmd, 0, 1,
                                    p1, p2, p3, p4, int(x * 1e7), int(y * 1e7), z)
    print(f"uploaded {len(items)} items: {n_lines} lines, GSD {p['gsd_cm']} cm, trigger every {p['trigger_m']} m")


if __name__ == "__main__":
    main()
