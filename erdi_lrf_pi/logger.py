"""Log distances to CSV:  erdi-lrf-log --port /dev/serial0 --model LRF22VB --csv log.csv"""
import argparse
import csv
import datetime as dt
import sys

from .reader import readings


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--baud", type=int)
    ap.add_argument("--hz", type=float, default=5.0, help="poll rate for family A models")
    ap.add_argument("--csv", default="-", help="output file, '-' for stdout")
    ap.add_argument("--seconds", type=float, help="stop after N seconds")
    ap.add_argument("--decimate", type=int, default=1, help="keep every Nth reading (family B streams at up to 1 kHz)")
    a = ap.parse_args(argv)
    out = sys.stdout if a.csv == "-" else open(a.csv, "a", newline="")
    w = csv.writer(out)
    w.writerow(["utc", "distance_m"])
    n = 0
    try:
        for t, d in readings(a.port, a.model, a.baud, a.hz, a.seconds):
            n += 1
            if n % a.decimate:
                continue
            w.writerow([dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat(timespec="milliseconds"),
                        "" if d is None else "%.3f" % d])
            out.flush()
    except KeyboardInterrupt:
        pass
    finally:
        if out is not sys.stdout:
            out.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
