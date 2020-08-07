# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
import time
from board import SCL, SDA
from busio import I2C
from pimoroni_circuitpython_ltr559 import Pimoroni_LTR559

bus = I2C(SCL, SDA)
ltr559 = Pimoroni_LTR559(bus)

while True:
    print(ltr559.lux)   # Get Lux value from light sensor
    print(ltr559.prox)  # Get Proximity value from proximity sensor
    time.sleep(1.0)