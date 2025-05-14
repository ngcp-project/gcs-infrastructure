from EmergencyStop import encode_emergency_stop, decode_emergency_stop

# ES = EmergencyStop()

print("Enabling Emergency Stop: ")

input = 1

encoded_data = encode_emergency_stop(input)

print(f"Expected string: '01 01 0{input}' Actual string: " + " ".join(f"{b:02x}" for b in encoded_data))

decoded_data = decode_emergency_stop(encoded_data)

print(decoded_data)