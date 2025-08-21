from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import base64

# Generate EC private key
private_key = ec.generate_private_key(ec.SECP256R1())

# Get public key from private key
public_key = private_key.public_key()

# Serialize public key to bytes (uncompressed point format)
public_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint
)

# Serialize private key to bytes (PKCS8 format)
private_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Encode both keys in Base64
public_key_b64 = base64.urlsafe_b64encode(public_bytes).decode('utf-8')
private_key_b64 = base64.urlsafe_b64encode(private_bytes).decode('utf-8')

print("Public Key:", public_key_b64)
print("Private Key:", private_key_b64)
