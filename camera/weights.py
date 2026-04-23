import struct
from serial import Serial


class Weights:

    def __init__(
        self, port: str, baudrate: int, timeout: float = 0.1, bytes_in_data: int = 4
    ):
        return
        self.ser = Serial(port=port, baudrate=baudrate, timeout=timeout)
        self.BYTES_IN_DATA = bytes_in_data

    def get_weight(self) -> float | None:
        return 1.0
        if self.ser.in_waiting > self.BYTES_IN_DATA:
            ready_to_get = self.ser.read(1)

            if (
                ready_to_get == b"\xaa"
            ):  # Byte that detemines that next 4 bytes are weight value
                raw_data = self.ser.read(self.BYTES_IN_DATA)

                if len(raw_data) == self.BYTES_IN_DATA:
                    weight = struct.unpack(">f", raw_data)[0]
                    return weight
        return None
