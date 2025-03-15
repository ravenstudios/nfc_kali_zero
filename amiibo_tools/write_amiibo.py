import board
import busio
import hashlib
import argparse
from digitalio import DigitalInOut
from adafruit_pn532.i2c import PN532_I2C


parser = argparse.ArgumentParser(description="Writes bin file to a nfc card.")
parser.add_argument("-f", type=str,required=True,  help="Choose bin file to be cloned.")
args = parser.parse_args()


# Initialize I2C
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False)

# Get firmware version (to confirm connection)
ic, ver, rev, support = pn532.firmware_version
print(f"Found PN532 with firmware version: {ver}.{rev}")

# Configure PN532 for NFC tag reading
pn532.SAM_configuration()

# Function to compute hash of a file
def compute_hash(data):
    trimed_data = data[16:]
    return hashlib.sha256(trimed_data).hexdigest()
# Read Amiibo dump file
with open(args.f, "rb") as f:
    amiibo_data = f.read()

original_hash = compute_hash(amiibo_data)
print(f"Original SHA-256 Hash: {original_hash}")

# Wait for an NFC tag
print("Waiting for an NFC tag...")
while True:
    uid = pn532.read_passive_target(timeout=0.5)
    if uid:
        print(f"Found NFC tag with UID: {uid.hex()}")
        
        # Write Amiibo data to NFC tag
        for block in range(135):
            chunk = amiibo_data[block*4:(block+1)*4]
            pn532.ntag2xx_write_block(block, chunk)
            print(f"Wrote Block {block:03}: {chunk.hex()}")
        
        # Read back from the tag
        print("Reading back written data...")
        read_data = bytearray()
        for block in range(135):
            block_data = pn532.ntag2xx_read_block(block)
            if block_data:
                read_data.extend(block_data)
        
        # Compute hash of read data
        read_hash = compute_hash(read_data)
        print(f"Readback SHA-256 Hash: {read_hash}")

        # Compare hashes
        if original_hash == read_hash:
            print("✅ Write verification successful! Data is identical.")
        else:
            print("❌ Verification failed! Data mismatch.")
        
        break
