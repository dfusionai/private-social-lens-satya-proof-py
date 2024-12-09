import pickle
import base64
import hashlib
from pybloom_live import BloomFilter

def salted_data(value, salt):
    """
    Hash the data with a secret salt and return the Base64-encoded digest.
    """
    combined = f"{value}|{salt}".encode('utf-8')
    sha256_hash = hashlib.sha256(combined).digest()  # Get raw binary hash
    return base64.b64encode(sha256_hash).decode('utf-8')  # Encode to Base64 string

def serialize_bloom_filter_base64(bloom):
    """
    Serialize the Bloom Filter to a Base64 string.
    Args:
        bloom: The Bloom Filter object to serialize.
    Returns:
        Base64 string representation of the Bloom Filter.
    """
    pickled_bloom = pickle.dumps(bloom)  # Serialize with pickle
    return base64.b64encode(pickled_bloom).decode('utf-8')  # Encode to Base64 string

def deserialize_bloom_filter_base64(base64_bloom):
    """
    Deserialize a Bloom Filter from a Base64 string.
    Args:
        base64_bloom: The Base64 string representation of the Bloom Filter.
    Returns:
        The deserialized Bloom Filter object.
    """
    pickled_bloom = base64.b64decode(base64_bloom.encode('utf-8'))  # Decode Base64 to bytes
    return pickle.loads(pickled_bloom)  # Deserialize with pickle

## EXAMPLE USAGE OF BLOOM FILTER
# # Configuration
# capacity = 150  # Set the capacity based on expected number of items
# error_rate = 0.001  # Low false positive rate
# salt = "secret_salt"  # Keep this salt secret

# # Create a Bloom Filter
# bloom = BloomFilter(capacity=capacity, error_rate=error_rate)

# # Example dataset
# dataset = [
#     "user123|sourceA|chat456|message789",
#     "user123|sourceA|chat456|message790",
#     "user123|sourceA|chat456|message791",
# ]

# # Add salted data to the Bloom Filter
# for data in dataset:
#     bloom.add(salted_data(data, salt))

# # Serialize the Bloom Filter to Base64
# serialized_bloom = serialize_bloom_filter_base64(bloom)
# print(f"Serialized Bloom Filter (Base64): {serialized_bloom[:100]}...")  # Truncated for display

# # Deserialize the Bloom Filter from Base64
# deserialized_bloom = deserialize_bloom_filter_base64(serialized_bloom)

# # Verify the deserialized Bloom Filter
# for data in dataset:
#     assert salted_data(data, salt) in deserialized_bloom

# # Test with a non-existent value
# assert salted_data("user123|sourceA|chat456|message999", salt) not in deserialized_bloom

# print("Deserialized Bloom Filter works as expected!")