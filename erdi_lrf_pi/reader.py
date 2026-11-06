"""Serial reading on top of the pure codecs of the `erdi-lrf` package."""
import time
from typing import Iterator, Optional, Tuple

import serial
from erdi_lrf import protocol_a as pa
from erdi_lrf import protocol_b as pb
from erdi_lrf.models import get_model

Reading = Tuple[float, Optional[float]]  # (unix time, metres or None when out of range / no echo)


def open_port(port: str, model: str, baud: Optional[int] = None, timeout: float = 0.2):
    """Open a serial port (a /dev path, or a pyserial URL such as loop://) at the model's baud."""
    spec = get_model(model)
    b = baud or spec.default_baud
    return serial.serial_for_url(port, baudrate=b, timeout=timeout)


def stream_b(ser, model: str, max_seconds: Optional[float] = None) -> Iterator[Reading]:
    """Family B (5C stream): yield every valid frame as (timestamp, metres)."""
    spec = get_model(model)
    if spec.family != "B":
        raise ValueError("%s is not a family B (5C stream) model" % model)
    buf = bytearray()
    t_end = time.time() + max_seconds if max_seconds else None
    while t_end is None or time.time() < t_end:
        chunk = ser.read(256)
        if chunk:
            buf += chunk
        last = 0
        for off, frame in pb.iter_data_frames(bytes(buf), spec):
            m = pb.parse_data_frame(frame, spec)
            yield time.time(), (None if m.out_of_range else m.metres)
            last = off + spec.frame_len
        if last:
            del buf[:last]
        elif len(buf) > 512:
            del buf[:-spec.frame_len]
        if not chunk and t_end is not None and time.time() >= t_end:
            break


def poll_a(ser, model: str, hz: float = 5.0, max_seconds: Optional[float] = None) -> Iterator[Reading]:
    """Family A (55 AA): send a single-shot request at `hz` and yield the reply."""
    spec = get_model(model)
    if spec.family != "A":
        raise ValueError("%s is not a family A (55 AA) model" % model)
    t_end = time.time() + max_seconds if max_seconds else None
    period = 1.0 / hz
    while t_end is None or time.time() < t_end:
        t0 = time.time()
        ser.reset_input_buffer()
        ser.write(pa.single_shot())
        reply = ser.read(8)
        if len(reply) == 8:
            try:
                m = pa.parse_measurement(reply, spec)
                yield time.time(), (m.metres if m.ok else None)
            except Exception:
                pass
        time.sleep(max(0.0, period - (time.time() - t0)))


def readings(port: str, model: str, baud: Optional[int] = None, hz: float = 5.0,
             max_seconds: Optional[float] = None) -> Iterator[Reading]:
    """Open `port` and yield readings for any supported model."""
    ser = open_port(port, model, baud)
    try:
        if get_model(model).family == "B":
            yield from stream_b(ser, model, max_seconds)
        else:
            yield from poll_a(ser, model, hz, max_seconds)
    finally:
        ser.close()
