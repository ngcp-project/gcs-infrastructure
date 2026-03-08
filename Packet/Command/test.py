from EmergencyStop import EmergencyStop


from UGV_Manual_Control.VelocityControl import VelocityControl

print("Enabling Emergency Stop: ")



input = 0



encoded_data = EmergencyStop.encode_packet(input)



print(f"Expected string: '01 01 0{input}' Actual string: " + " ".join(f"{b:02x}" for b in encoded_data))



decoded_data = EmergencyStop.decode_packet(encoded_data)

print(decoded_data)



print("Testing control command:\n")



input2 = 79


encoded_data2 = VelocityControl.encode_packet(input2)



print(f"Expected Value '01 09 {input2:x}' Actual string: " + " ".join(f"{b:02x}" for b in encoded_data2))



decoded_data2 = VelocityControl.decode_packet(encoded_data2)

print(decoded_data2)