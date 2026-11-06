# Raspberry Pi UART setup for a laser rangefinder module

1. Wire TX to the Pi RX pin (GPIO15, header pin 10), RX to the Pi TX pin (GPIO14, pin 8), GND to GND. Pi GPIO is **3.3 V logic**: confirm your module's UART level first and use a level shifter if it is 5 V. Power the module from its own supply as the model manual says.
2. Enable the serial hardware and disable the login shell: `sudo raspi-config` -> Interface Options -> Serial Port -> login shell **No**, serial port hardware **Yes**. The primary UART appears as `/dev/serial0`.
3. 460800 baud modules (LRF22VB, LRF50VB, H series): the Pi's mini UART derives its clock from the core frequency and can drift. Prefer the full PL011 UART (for example the `disable-bt` overlay on models with Bluetooth, or an additional UART overlay) or use a USB-TTL adapter (`/dev/ttyUSB0`). Check the current Raspberry Pi documentation for your board: <https://www.raspberrypi.com/documentation/computers/configuration.html#configure-uarts>.
4. Add your user to the `dialout` group: `sudo usermod -aG dialout $USER`, then log out and in.
5. Test: `erdi-lrf-log --port /dev/serial0 --model LRF22VB --seconds 5`.

## Run as a service

`systemd/erdi-lrf-mqtt.service` publishes to MQTT at boot. Edit the model, port and broker, then:

```bash
sudo cp systemd/erdi-lrf-mqtt.service /etc/systemd/system/
sudo systemctl enable --now erdi-lrf-mqtt
```
