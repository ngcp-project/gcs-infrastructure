from EmergencyStop import EmergencyStop

ES = EmergencyStop()

print("Enabling Emergency Stop: ")

input = 0

encoded_data = ES.encode_data(input)

print(f"Expected string: '01 01 0{input}' Actual string: " + " ".join(f"{b:02x}" for b in encoded_data))

decoded_data = ES.decode_data(encoded_data)

print(decoded_data)