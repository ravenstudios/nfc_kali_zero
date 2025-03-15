import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.i2c import PN532_I2C

# Initialize I2C
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False)

# Get firmware version (to confirm connection)
ic, ver, rev, support = pn532.firmware_version
print(f"Found PN532 with firmware version: {ver}.{rev}")

# Configure PN532 for NFC tag reading
pn532.SAM_configuration()

# Wait for an NFC tag
print("Waiting for an NFC tag...")
while True:
    uid = pn532.read_passive_target(timeout=0.5)
    if uid:
        print(f"Found NFC tag with UID: {uid.hex()}")
        break

# NTAG215 (Amiibo) has 135 blocks, each 4 bytes
total_blocks = 135
dump_data = bytearray()

for block in range(total_blocks):
    data = pn532.ntag2xx_read_block(block)
    if data:
        dump_data.extend(data)
        print(f"Block {block:03}: {data.hex()}")

# Save to a file
filename = input("Enter a filename\n")
with open(f"Backups/{filename}.bin", "wb") as f:
    f.write(dump_data)

print(f"Amiibo data saved to Backups/{filename}.bin!")
