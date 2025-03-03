import smbus
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
        self.bus = smbus.SMBus(1) #initialize the i2c bus
        self.init_ITG3205()

        # Initialize ADXL345 Accelerometer
        i2c = busio.I2C(board.SCL, board.SDA)
        self.accelerometer = adafruit_adxl34x.ADXL345(i2c)

    def init_ITG3205(self):
        """Initialize the ITG-3205 gyroscope."""
        self.bus.write_byte_data(self.ITG3205_ADDR, self.PWR_MGMT_REG, 0x00) # Wake up sensor
        self.bus.write_byte_data(self.ITG3205_ADDR, self.DLPF_FS, 0x18) # Set full-scale range to ±2000°/s
    
    def read_word(self, adr):
        """Read a word from the specified register (big-endian to little-endian conversion)."""
        high = self.bus.read_byte_data(self.ITG3205_ADDR, adr)
        low = self.bus.read_byte_data(self.ITG3205_ADDR, adr + 1)
        value = (high << 8) + low
        if value >= 0x8000:  # Convert to signed
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
