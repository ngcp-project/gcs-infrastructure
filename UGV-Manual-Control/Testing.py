from XInputController import *
import time

controller = XInputController(controllerIndex=0)

while True:
        state = controller.read()

        if state is None:
            print("Controller not connected")
            time.sleep(1.0)
        else:
            print(state)
            time.sleep(0.01)

