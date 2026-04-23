import serial

class Motor:
    """Spin physical motor."""

    def __init__(self, port: str, baud_rate: int = 115200, timeout: float = 0.1):
        """
        Port COM6 for Windows
        /dev/ttyUSB0 for Linux
        """
        self.ser = serial.Serial(port, baud_rate, timeout=timeout)

    def spin(self) -> None:
        """Spin physical motor for 1 second. Wait at least 1 second between spins."""
        self.ser.write(b"pulse\n")

