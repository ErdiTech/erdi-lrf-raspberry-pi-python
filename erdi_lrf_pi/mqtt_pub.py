"""Publish distances to MQTT:  erdi-lrf-mqtt --port /dev/serial0 --model LRF22VB --host 192.168.1.10 --topic lrf/distance"""
import argparse
import json
import sys
import time

from .reader import readings


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--baud", type=int)
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--mqtt-port", type=int, default=1883)
    ap.add_argument("--topic", default="erdi_lrf/distance")
    ap.add_argument("--rate", type=float, default=2.0, help="max publishes per second")
    a = ap.parse_args(argv)
    import paho.mqtt.client as mqtt  # optional dependency: pip install erdi-lrf-pi[mqtt]

    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # paho-mqtt >= 2
    except AttributeError:
        client = mqtt.Client()
    client.connect(a.host, a.mqtt_port)
    client.loop_start()
    last = 0.0
    try:
        for t, d in readings(a.port, a.model, a.baud):
            if t - last < 1.0 / a.rate:
                continue
            last = t
            client.publish(a.topic, json.dumps({"t": round(t, 3), "distance_m": d}), qos=0)
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()
    return 0


if __name__ == "__main__":
    sys.exit(main())
