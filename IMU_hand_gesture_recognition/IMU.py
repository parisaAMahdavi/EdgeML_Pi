import board
import busio
import adafruit_adxl34x

class GY85_IMUSensor:
    ITG3205_ADDR = 0x68   # ITG3205 I2C address
    ADXL345_ADDR = 0x53   # ADXL345 I2C address

    # Registers
    PWR_MGMT_REG = 0x3E
    GYRO_XOUT_H = 0x1D
    GYRO_YOUT_H = 0x1F
    GYRO_ZOUT_H = 0x21
    DLPF_FS = 0x16  # Digital Low Pass Filter and Full Scale Register

    # Sensitivity Scale Factor (LSB to °/s)
    GYRO_SENSITIVITY = 14.375  # 1 LSB = 1/14.375 °/s

    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.init_ITG3205()
        self.accelerometer = adafruit_adxl34x.ADXL345(self.i2c)
    def init_ITG3205(self):
        """Initialize the ITG-3205 gyroscope."""
        # Wake up the sensor (ITG3205)
        self.i2c.writeto(self.ITG3205_ADDR, bytes([self.PWR_MGMT_REG, 0x00]))  
        # Set full-scale range to ±2000°/s (Digital Low Pass Filter and Full Scale Register)
        self.i2c.writeto(self.ITG3205_ADDR, bytes([self.DLPF_FS, 0x18]))  
    
    def read_word(self, register):
        """Read a 16-bit signed word from two consecutive registers."""
        self.i2c.writeto_then_readfrom(self.ITG3205_ADDR, bytes([register]), buffer := bytearray(2))
        value = (buffer[0] << 8) | buffer[1]
        if value >= 0x8000:
            value = -((65535 - value) + 1)
        return value
    def get_gyro_data(self):
        """Retrieve gyroscope data in °/s."""
        gx = self.read_word(self.GYRO_XOUT_H) / self.GYRO_SENSITIVITY
        gy = self.read_word(self.GYRO_YOUT_H) / self.GYRO_SENSITIVITY
        gz = self.read_word(self.GYRO_ZOUT_H) / self.GYRO_SENSITIVITY
        return gx, gy, gz

    def get_accel_data(self):
        """Retrieve accelerometer data in m/s²."""
        x, y, z = self.accelerometer.acceleration  
        return x, y, z
    