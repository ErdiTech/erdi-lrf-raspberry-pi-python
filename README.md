# ERDI laser rangefinder on Raspberry Pi (Python)

Python tools to use an **ERDI 905 nm laser rangefinder module with a Raspberry Pi**: a serial reader, a **CSV data logger**, an **MQTT publisher** and a **MAVLink `DISTANCE_SENSOR` bridge** that feeds the distance to a **Pixhawk / ArduPilot / PX4** flight controller from a companion computer. Works on any Linux board or PC with a UART or USB-TTL adapter (Raspberry Pi 3/4/5/Zero, Jetson, Orange Pi). Built on the protocol codecs of [`erdi-lrf`](https://pypi.org/project/erdi-lrf/) (`pip install erdi-lrf`), which cites every constant to the module manual.

Supported: **LRF22VB, LRF50VB, LRF50H, LRF100H, LRF200H, LRF300H, LRF600H, LRF1500H** (460800 baud `5C` stream) and **LR1000E2 ... LR2000E4, LRF1200A1, LRF3000A1, SPD1200N0/N2/N4** (115200 baud `55 AA` polled).

## Install

```bash
pip install "git+https://github.com/Tommyapi/erdi-lrf-raspberry-pi-python"      # reader + logger
pip install "erdi-lrf-pi[mqtt,mavlink] @ git+https://github.com/Tommyapi/erdi-lrf-raspberry-pi-python"
```

UART wiring and Raspberry Pi serial setup: [docs/raspberry-pi-uart.md](docs/raspberry-pi-uart.md).

## Use

```bash
erdi-lrf-log  --port /dev/serial0 --model LRF22VB --csv log.csv --decimate 20   # CSV, every 20th frame
erdi-lrf-mqtt --port /dev/serial0 --model LRF100H --host 192.168.1.10 --topic erdi_lrf/distance
erdi-lrf-mavlink --port /dev/serial0 --model LRF22VB --mav udpout:127.0.0.1:14550
```

```python
from erdi_lrf_pi.reader import readings
for t, metres in readings("/dev/serial0", "LRF22VB"):
    print(t, "out of range" if metres is None else "%.3f m" % metres)
```

Units are per model (H series centimetres, VB series millimetres, family A metres x 10): always pass the exact model name.

## Pixhawk / ArduPilot companion computer

`erdi-lrf-mavlink` sends `DISTANCE_SENSOR` (centimetres, laser type, downward orientation by default) with the model's published minimum and maximum range. On ArduPilot set `RNGFND1_TYPE=10` (MAVLink), `RNGFND1_ORIENT=25` (downward), and `RNGFND1_MIN` / `RNGFND1_MAX` (metres in current ArduPilot; `RNGFND1_MIN_CM` / `RNGFND1_MAX_CM` in firmware before the rename) to match; see [erdi-lrf-pixhawk-ardupilot](https://github.com/Tommyapi/erdi-lrf-pixhawk-ardupilot) for the direct-to-flight-controller Lua option. Bench-test before flight.

## Tests

```bash
pip install -e ".[test]" && python -m pytest -q
```

The tests run over a pyserial `loop://` virtual port using golden frames from the manuals; they do not need hardware.

## Related projects

- [ErdiTech/erdi-lrf-drivers](https://github.com/ErdiTech/erdi-lrf-drivers): the protocol library and ROS 2 node
- [erdi-lrf-ros2-examples](https://github.com/Tommyapi/erdi-lrf-ros2-examples): ROS 2 launch files and RViz
- [laser-rangefinder-module-database](https://github.com/Tommyapi/laser-rangefinder-module-database): dataset of laser rangefinder specifications

## Support / 打赏

If this project saved you time, you can buy the author a coffee in crypto. Thank you!
如果这个项目帮到了你，欢迎用加密货币打赏支持，谢谢！

| Network | Asset | Address |
|---|---|---|
| TRON (TRC20) | USDT | `TNGdTwE6opH6rmUyoG1JUR7FSyEb4k273R` |
| Ethereum / BNB Chain / Polygon | USDT | `0x59c43144a862b351fa1086ae842d1327c9d91613` |
| Ethereum / Arbitrum / Base | ETH | `0x59c43144a862b351fa1086ae842d1327c9d91613` |
| Bitcoin | BTC | `1RS6tWXHregLfEsiPzVUCUBuhgDg5uTSV` |
| Solana | USDT | `HZguEXfTtLChNdJTxAYCbcGscaqikz8JYrEpUhEyeVd9` |

Please send only the listed asset on the listed network — other tokens or networks may be lost.
请按表中对应的网络转对应的币种，转错币种或网络可能无法找回。

Built by tommyapi.com

## License

MIT — see [LICENSE](LICENSE).
