# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2020 Philip Howard, written for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT
"""
`pimoroni_circuitpython_ltr559`
================================================================================

Library for the LTR559 Proximity/Presence/Light Sensor


* Author(s): Philip Howard

Implementation Notes
--------------------

**Hardware:**

.. todo:: Add links to any specific hardware product page(s), or category page(s). Use unordered list & hyperlink rST
   inline format: "* `Link Text <url>`_"

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

.. todo:: Uncomment or remove the Bus Device and/or the Register library dependencies based on the library's use of either.

# * Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
# * Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""
import time
from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_register.i2c_struct import Struct
from adafruit_register.i2c_bits import RWBits, ROBits
from adafruit_register.i2c_bit import RWBit
from micropython import const

__version__ = "0.0.1"
__repo__ = "https://github.com/pimoroni/Pimoroni_CircuitPython_LTR559.git"


_LTR559_I2C_ADDR = const(0x23)
_LTR559_PART_ID = const(0x09)
_LTR559_REVISION_ID = const(0x02)

_LTR559_REG_ALS_CONTROL = const(0x80)
_LTR559_REG_PS_CONTROL = const(0x81)
_LTR559_REG_PS_LED = const(0x82)
_LTR559_REG_PS_N_PULSES = const(0x83)
_LTR559_REG_PS_MEAS_RATE = const(0x84)
_LTR559_REG_ALS_MEAS_RATE = const(0x85)
_LTR559_REG_PART_ID = const(0x86)
_LTR559_REG_MANUFACTURER_ID = const(0x87)
_LTR559_REG_ALS_DATA_CH0 = const(0x88)
_LTR559_REG_ALS_DATA_CH1 = const(0x89)
_LTR559_REG_ALS_PS_STATUS = const(0x8c)
_LTR559_REG_PS_DATA_CH0 = const(0x8d)
_LTR559_REG_PS_DATA_SAT = const(0x8e)
_LTR559_REG_INTERRUPT = const(0x8f)
_LTR559_REG_PS_THRESHOLD_UPPER = const(0x90)
_LTR559_REG_PS_THRESHOLD_LOWER = const(0x92)
_LTR559_REG_PS_OFFSET = const(0x94)
_LTR559_REG_ALS_THRESHOLD_UPPER = const(0x97)
_LTR559_REG_ALS_THRESHOLD_LOWER = const(0x99)
_LTR559_REG_INTERRUPT_PERSIST = const(0x9e)


class RW12BitAdapter(RWBits):
    pass


class DeviceControl:  # pylint: disable-msg=too-few-public-methods
    def __init__(self, i2c):
        self.i2c_device = i2c  # self.i2c_device required by RWBit class

    als_gain = RWBits(3, _LTR559_REG_ALS_CONTROL, 2)
    sw_reset = RWBit(_LTR559_REG_ALS_CONTROL, 1)
    als_mode = RWBit(_LTR559_REG_ALS_CONTROL, 0)

    ps_saturation_indicator_enable = RWBit(_LTR559_REG_PS_CONTROL, 5)
    ps_active = RWBits(2, _LTR559_REG_PS_CONTROL, 0)

    led_pulse_freq_khz = RWBits(3, _LTR559_REG_PS_LED, 5)
    led_duty_cycle = RWBits(2, _LTR559_REG_PS_LED, 3)
    led_current_ma = RWBits(3, _LTR559_REG_PS_LED, 0)

    pulse_count = RWBits(4, _LTR559_REG_PS_N_PULSES, 0)

    ps_rate_ms = RWBits(4, _LTR559_REG_PS_MEAS_RATE, 0)

    als_integration_time_ms = RWBits(3, _LTR559_REG_ALS_MEAS_RATE, 3)

    als_repeat_rate_ms = RWBits(3, _LTR559_REG_ALS_MEAS_RATE, 0)

    part_number = RWBits(4, _LTR559_REG_PART_ID, 4)
    revision = RWBits(4, _LTR559_REG_PART_ID, 0)

    manufacturer_id = ROBits(8, _LTR559_REG_MANUFACTURER_ID, 0)

    als_data_ch0 = RWBits(8, _LTR559_REG_ALS_DATA_CH0, 0)
    als_data_ch1 = RWBits(8, _LTR559_REG_ALS_DATA_CH1, 0)

    als_data_valid = RWBit(_LTR559_REG_ALS_PS_STATUS, 7)
    als_data_gain = RWBits(3, _LTR559_REG_ALS_PS_STATUS, 4)

    ps_data_ch0 = RW12BitAdapter(16, _LTR559_REG_PS_DATA_CH0, 0, register_width=2)
    ps_saturation = RWBit(_LTR559_REG_PS_DATA_SAT, 7)

    interrupt_polarity = RWBit(_LTR559_REG_INTERRUPT, 2)
    interrupt_mode = RWBits(2, _LTR559_REG_INTERRUPT, 0)

    ps_threshold_lower = RW12BitAdapter(16, _LTR559_REG_PS_THRESHOLD_LOWER, 0, register_width=2)
    ps_threshold_upper = RW12BitAdapter(16, _LTR559_REG_PS_THRESHOLD_UPPER, 0, register_width=2)

    ps_offset = RWBits(10, _LTR559_REG_PS_OFFSET, 0, register_width=2)

    als_threshold_lower = RWBits(16, _LTR559_REG_ALS_THRESHOLD_LOWER, 0, register_width=2)
    als_threshold_upper = RWBits(16, _LTR559_REG_ALS_THRESHOLD_UPPER, 0, register_width=2)

    ps_interrupt_persist = RWBits(4, _LTR559_REG_INTERRUPT_PERSIST, 0)
    als_interrupt_persist = RWBits(4, _LTR559_REG_INTERRUPT_PERSIST, 4)


class Pimoroni_LTR559:
    """
    A driver for the LTR559 Proximity/Distance/Light sensor.
    """

    def __init__(self, i2c, address=_LTR559_I2C_ADDR):
      """Initialize the sensor."""
      self._device = I2CDevice(i2c, address)
      self._settings = DeviceControl(self._device)
