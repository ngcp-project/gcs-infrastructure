from XInputController import *
from StateInterpreter import *
import time

controller = XInputController(controllerIndex=0)
interpreter = StateInterpreter()

while True:
        state = controller.read()

        if state is None:
            print("Controller not connected")
            time.sleep(1.0)
        else:
            print(state)
            print(interpreter.produceCommands(state))
            
            time.sleep(0.01)

