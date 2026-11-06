"""Feed an ERDI laser rangefinder to a Pixhawk / ArduPilot / PX4 flight controller as MAVLink DISTANCE_SENSOR.

    erdi-lrf-mavlink --port /dev/serial0 --model LRF22VB --mav udpout:127.0.0.1:14550

On ArduPilot set RNGFND1_TYPE=10 (MAVLink), RNGFND1_ORIENT=25 (down), RNGFND1_MIN and RNGFND1_MAX (metres; older firmware uses *_CM) to the values below.
"""
import argparse
import sys
import time

from erdi_lrf.models import get_model

from .reader import readings

MAV_DISTANCE_SENSOR_LASER = 0


def distance_sensor_args(model: str, metres, orientation: int = 25, sensor_id: int = 1, t_ms: int = 0):
    """Arguments for mav.distance_sensor_send(); distances are centimetres per the MAVLink message."""
    spec = get_model(model)
    min_cm = int(round(spec.min_range_m * 100))
    max_cm = int(round(spec.max_range_m * 100))
    cur_cm = max_cm + 1 if metres is None else int(round(metres * 100))  # above max = "no target"
    return (t_ms, min_cm, max_cm, min(cur_cm, 65535), MAV_DISTANCE_SENSOR_LASER, sensor_id, orientation, 0)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--baud", type=int)
    ap.add_argument("--mav", default="udpout:127.0.0.1:14550", help="pymavlink connection string")
    ap.add_argument("--orientation", type=int, default=25, help="MAV_SENSOR_ORIENTATION, 25 = downward")
    ap.add_argument("--rate", type=float, default=20.0, help="max messages per second")
    a = ap.parse_args(argv)
    from pymavlink import mavutil  # optional dependency: pip install erdi-lrf-pi[mavlink]

    master = mavutil.mavlink_connection(a.mav, source_system=1, source_component=mavutil.mavlink.MAV_COMP_ID_ONBOARD_COMPUTER)
    t0 = time.time()
    last = 0.0
    try:
        for t, d in readings(a.port, a.model, a.baud):
            if t - last < 1.0 / a.rate:
                continue
            last = t
            args = distance_sensor_args(a.model, d, a.orientation, 1, int((t - t0) * 1000) & 0xFFFFFFFF)
            master.mav.distance_sensor_send(*args)
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
