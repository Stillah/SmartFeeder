import serial
import numpy as np

class WeightsMock:
    START_BYTE = 0x80
    END_BYTE = 0x81
    SCALE_MULT = 1000.0

    def __init__(self, port: str, baud_rate: int, timeout: float = 0.1):
        pass

    def get_weight(self) -> float | None:
        return np.random.uniform(0.0, 10.0)


class Weights:
    START_BYTE = 0x80
    END_BYTE = 0x81
    SCALE_MULT = 1000.0

    def __init__(self, port: str, baud_rate: int, timeout: float = 0.1):
        self.ser = serial.Serial(port, baud_rate,timeout=timeout)

    def _read_packet(self):
        b = self.ser.read(1)

        if not b:
            return None

        if b[0] == self.START_BYTE:
            data = self.ser.read(7)

            if len(data) != 7:
                return

            if data[6] != self.END_BYTE:
                return

            return data[:6]

    def _decode_int42(self, data_bytes: bytes) -> int:

        value = 0

        for b in data_bytes:
            value = (value << 7) | (b & 0x7F)

        
        if value & (1 << 41):
            value -= (1 << 42)

        return value

    def get_weight(self) -> float | None:
        packet = self._read_packet()

        if packet is None:
            return None

        raw = self._decode_int42(packet)
        weight = raw / self.SCALE_MULT

        return weight