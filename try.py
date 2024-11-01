import numpy as np
import decimal

def convert_to_float8(value):
    """Convert a decimal value to an 8-bit representation."""
    # Example conversion to a float16 for demonstration (not true 8-bit)
    return np.float16(value)

def restore_float8(value):
    """Convert an 8-bit representation back to a decimal."""
    return decimal.Decimal(float(value))  # Convert to float first

# Generate a random decimal value
random_value = decimal.Decimal(np.random.rand())  # Random decimal between 0 and 1

# Memory consumption before conversion
original_size = random_value.__sizeof__()

# Convert to float8 (float16 in this case)
float8_value = convert_to_float8(random_value)
float8_size = float8_value.nbytes

# Restore back to decimal
restored_value = restore_float8(float8_value)
restored_size = restored_value.__sizeof__()

# Display memory consumption
memory_usage = {
    'original_size': original_size,
    'float8_size': float8_size,
    'restored_size': restored_size
}

# Print results
print(f"Original Decimal Value: {random_value} (Memory Size: {original_size} bytes)")
print(f"Converted to Float8: {float8_value} (Memory Size: {float8_size} bytes)")
print(f"Restored Decimal Value: {restored_value} (Memory Size: {restored_size} bytes)")
print("Memory usage:", memory_usage)
