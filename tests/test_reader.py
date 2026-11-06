import threading
import time

import pytest

from erdi_lrf import protocol_b as pb
from erdi_lrf.models import get_model

from erdi_lrf_pi.mavlink_bridge import distance_sensor_args
from erdi_lrf_pi.reader import open_port, stream_b


def frame(model, raw):
    return pb.build_data_frame(raw, get_model(model))


def test_stream_over_loopback_vb_is_millimetres():
    ser = open_port("loop://", "LRF22VB")
    ser.write(frame("LRF22VB", 4354) * 3)
    out = [m for _, m in stream_b(ser, "LRF22VB", max_seconds=0.3)]
    assert out[:3] == pytest.approx([4.354] * 3)


def test_stream_over_loopback_h_is_centimetres():
    ser = open_port("loop://", "LRF100H")
    ser.write(b"\x00\x5c" + frame("LRF100H", 4354))
    out = [m for _, m in stream_b(ser, "LRF100H", max_seconds=0.3)]
    assert out and out[0] == pytest.approx(43.54)


def test_out_of_range_is_none():
    ser = open_port("loop://", "LRF22VB")
    ser.write(frame("LRF22VB", 20000))
    out = [m for _, m in stream_b(ser, "LRF22VB", max_seconds=0.3)]
    assert out == [None]


def test_family_a_model_rejected_by_stream_b():
    ser = open_port("loop://", "LRF3000A1")
    with pytest.raises(ValueError):
        next(stream_b(ser, "LRF3000A1"))


def test_mavlink_args_are_centimetres():
    args = distance_sensor_args("LRF22VB", 1.234, orientation=25, t_ms=1000)
    assert args == (1000, 5, 2000, 123, 0, 1, 25, 0)


def test_mavlink_no_target_reports_above_max():
    args = distance_sensor_args("LRF22VB", None)
    assert args[3] == args[2] + 1
