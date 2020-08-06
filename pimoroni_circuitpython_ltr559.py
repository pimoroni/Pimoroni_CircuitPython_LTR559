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

LTR559_INTERRUPT_MODE_OFF = const(0b00)
LTR559_INTERRUPT_MODE_PS = const(0b01)
LTR559_INTERRUPT_MODE_ALS = const(0b10)

LTR559_LED_FREQ_30KHZ = const(0b000)
LTR559_LED_FREQ_40KHZ = const(0b001)
LTR559_LED_FREQ_50KHZ = const(0b010)
LTR559_LED_FREQ_60KHZ = const(0b011)
LTR559_LED_FREQ_70KHZ = const(0b100)
LTR559_LED_FREQ_80KHZ = const(0b100)
LTR559_LED_FREQ_90KHZ = const(0b110)
LTR559_LED_FREQ_100KHZ = const(0b111)

LTR559_LED_DUTY_25 = const(0b00)
LTR559_LED_DUTY_50 = const(0b01)
LTR559_LED_DUTY_75 = const(0b10)
LTR559_LED_DUTY_100 = const(0b11)

LTR559_LED_CURRENT_5MA = const(0b000)
LTR559_LED_CURRENT_10MA = const(0b001)
LTR559_LED_CURRENT_20MA = const(0b010)
LTR559_LED_CURRENT_50MA = const(0b011)
LTR559_LED_CURRENT_100MA = const(0b100)

LTR559_PS_INTEGRATION_TIME_100MS = const(0b000)
LTR559_PS_INTEGRATION_TIME_50MS = const(0b001)
LTR559_PS_INTEGRATION_TIME_200MS = const(0b010)
LTR559_PS_INTEGRATION_TIME_400MS = const(0b011)
LTR559_PS_INTEGRATION_TIME_150MS = const(0b100)
LTR559_PS_INTEGRATION_TIME_250MS = const(0b101)
LTR559_PS_INTEGRATION_TIME_300MS = const(0b110)
LTR559_PS_INTEGRATION_TIME_350MS = const(0b111)

LTR559_PS_RATE_50MS = const(0b000)
LTR559_PS_RATE_100MS = const(0b001)
LTR559_PS_RATE_200MS = const(0b010)
LTR559_PS_RATE_500MS = const(0b011)
LTR559_PS_RATE_1000MS = const(0b100)
LTR559_PS_RATE_2000MS = const(0b101)

LTR559_ALS_GAIN_1X = const(0b000)
LTR559_ALS_GAIN_2X = const(0b001)
LTR559_ALS_GAIN_4X = const(0b010)
LTR559_ALS_GAIN_8X = const(0b011)
LTR559_ALS_GAIN_48X = const(0b110)
LTR559_ALS_GAIN_96X = const(0b111)

LTR559_ALS_RATE_50MS = const(0b000)
LTR559_ALS_RATE_100MS = const(0b001)
LTR559_ALS_RATE_200MS = const(0b010)
LTR559_ALS_RATE_500MS = const(0b011)
LTR559_ALS_RATE_1000MS = const(0b100)
LTR559_ALS_RATE_2000MS = const(0b101)

LTR559_ALS_INTEGRATION_TIME_100MS = const(0b000)
LTR559_ALS_INTEGRATION_TIME_50MS = const(0b001)
LTR559_ALS_INTEGRATION_TIME_200MS = const(0b010)
LTR559_ALS_INTEGRATION_TIME_400MS = const(0b011)
LTR559_ALS_INTEGRATION_TIME_150MS = const(0b100)
LTR559_ALS_INTEGRATION_TIME_250MS = const(0b101)
LTR559_ALS_INTEGRATION_TIME_300MS = const(0b110)
LTR559_ALS_INTEGRATION_TIME_350MS = const(0b111)


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

    led_pulse_count = RWBits(4, _LTR559_REG_PS_N_PULSES, 0)

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

    def __init__(self, i2c, address=_LTR559_I2C_ADDR, enable_interrupts=False, interrupt_pin_polarity=1, timeout=5):
        """Initialize the sensor."""
        self._device = I2CDevice(i2c, address)
        self.settings = DeviceControl(self._device)

        self._als0 = 0
        self._als1 = 0
        self._ps0 = 0
        self._lux = 0
        self._ratio = 100

        # Non default
        self._gain = 4  # 4x gain = 0.25 to 16k lux
        self._integration_time = 50

        self._ch0_c = (17743, 42785, 5926, 0)
        self._ch1_c = (-11059, 19548, -1185, 0)

        if (self.settings.part_number, self.settings.revision) != (_LTR559_PART_ID, _LTR559_REVISION_ID):
            raise RuntimeError("LTR559 not found")

        self.settings.sw_reset = 1

        t_start = time.monotonic()
        while time.monotonic() - t_start < timeout:
            if self.settings.sw_reset == 0:
                break
            time.sleep(0.05)

        if self.settings.sw_reset:
            raise RuntimeError("Timeout waiting for software reset.")

        # Interrupt regfister must be set before device is switched to active mode
        # see datasheet page 12/40, note #2
        if enable_interrupts:
            self.settings.interrupt_mode = LTR559_INTERRUPT_MODE_PS | LTR559_INTERRUPT_MODE_ALS
            self.settings.interrupt_polarity = interrupt_pin_polarity

        # FIXME use datasheet defaults or document
        # No need to run the proximity LED at 100mA, so we pick 50 instead.
        # Tests suggest this works pretty well.
        self.settings.led_current_ma = LTR559_LED_CURRENT_50MA
        self.settings.led_duty_cycle = LTR559_LED_DUTY_100
        self.settings.led_pulse_freq_khz = LTR559_LED_FREQ_30KHZ

        # 1 pulse is the default value
        self.settings.led_pulse_count = 1

        self.settings.ps_active = 1
        self.settings.ps_saturation_indicator_enable = 1

        self.settings.ps_rate_ms = LTR559_PS_RATE_50MS
        self.settings.als_repeat_rate_ms = LTR559_ALS_RATE_50MS
        self.settings.als_integration_time_ms = LTR559_ALS_INTEGRATION_TIME_50MS

        self.settings.als_threshold_lower = 0x0000
        self.settings.als_threshold_upper = 0xffff

        self.settings.ps_threshold_lower = 0x0000
        self.settings.ps_threshold_upper = 0xffff

        self.settings.ps_offset = 0
    
