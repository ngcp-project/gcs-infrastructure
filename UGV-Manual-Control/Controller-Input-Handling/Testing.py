from XInputController import *
from StateInterpreter import *
import time

controller = XInputController(controllerIndex=0)
interpreter = StateInterpreter()
prevState = None
while True:
        state = controller.read()

        if state is None or state.stateFrame == prevState:
            continue
        else:
            if prevState != state.stateFrame:
                print(state)
                print(StateInterpreter.produceCommands(state))
                prevState = state.stateFrame
            
            time.sleep(1)

