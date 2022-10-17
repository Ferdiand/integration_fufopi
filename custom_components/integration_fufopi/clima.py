import datetime
import pigpio
import asyncio
from pigpio_dht import DHT22, _debug


class TuneDHT22(DHT22):
    """bla"""

    def _read(self):
        """
        One-Shot read implementation.
        _read() monitors the read rate self._max)read_rate_secs and will pause between successive calls.
        :return: Sensor data like {'temp_c': 20, 'temp_f': 68.0, 'humidity': 35, 'valid': True}
        :rtype: Dictionary
        """

        # Throttle reads so we are not reading more than once per self._max_read_rate_secs
        if self._last_read_time:
            elapsed_since_last_read = (
                datetime.now() - self._last_read_time
            ).microseconds / 1000000

            if elapsed_since_last_read < self._max_read_rate_secs:
                pause_secs = self._max_read_rate_secs - elapsed_since_last_read
                _debug("Pausing for secs", pause_secs)
                await asyncio.sleep(pause_secs)
                sleep(pause_secs)

        self._edge_count = 0
        self._bit_count = 0
        self.read_success = False
        self.sensor_responded = False
        self.data = []
        self._last_tick = self._pi.get_current_tick()
        self._last_read_time = datetime.now()
        self._c0 = self._last_tick

        self._edge_callback_fn = self._pi.callback(
            self.gpio, pigpio.EITHER_EDGE, self._edge_callback
        )

        self._pi.set_mode(self.gpio, pigpio.OUTPUT)
        self._pi.write(self.gpio, pigpio.LOW)
        sleep(0.018)  # 18ms pause as per datasheet
        # No! self._pi.write(self.gpio, pigpio.HIGH)
        self._pi.set_mode(self.gpio, pigpio.INPUT)

        # Sleep while __edge_callback is called.
        timer = 0
        while timer < self.timeout_secs:
            timer += 0.01
            sleep(0.01)

        self._edge_callback_fn.cancel()

        if DEBUG:
            elapsed_secs = (self._c1 - self._c0) / 1000000
            _debug("Edge Count", self._edge_count)
            _debug("Data Length", len(self.data))
            _debug("Round Trip Secs:", elapsed_secs)
            _debug("Sensor Response?", self.sensor_responded)
            _debug("Read Success?", self.read_success)

        if not self.sensor_responded:
            raise TimeoutError(
                "{} sensor on GPIO {} has not responded in {} seconds. Check sensor connection.".format(
                    self.__class__.__name__, self.gpio, self.timeout_secs
                )
            )
        elif not self.read_success:
            # note: self._edge_count == DHTXX.SUCCESS_EDGE_COUNT when self.read_success == True
            raise TimeoutError(
                "{} sensor on GPIO {} responded but the response was invalid. Check sensor connection or try increasing timeout (currently {} seconds).".format(
                    self.__class__.__name__, self.gpio, self.timeout_secs
                )
            )

        return self._parse_data()
