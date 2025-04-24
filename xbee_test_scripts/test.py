import os  # I think it's better to use subprocess for this. but quick code for example

status = os.system('systemctl is-active --quiet service-name')
print(status)