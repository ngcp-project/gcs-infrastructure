#Reads ControllerState objects and interprets it's values into commands
import ControllerState
class StateInterpreter:

    #Return a list of command IDs to be queued
    @staticmethod
    def produceCommands(state:ControllerState):
        commands = []
        #Open and close end effector with x
        if state.x:
            commands.append(9) 

        #Control payload movement using right stick
        #Push stick up to raise, push down to lower
        if state.ry > 0:
            commands.append((8, 1))
        elif state.ry < 0:
            commands.append((8, -1))

        #Control forward/backwards movement using triggers
        #lt for reverse, rt for forwards
        if state.lt > 0 and state.rt > 0:
            pass #Do nothing if both triggers are pressed, 
        elif state.lt > 0:
            #movementMagnitude = state.lt*100/255 #Normalize value to 0-100 scale
            commands.append((6, int(-state.lt*100)))
        elif state.rt > 0:
            #movementMagnitude = state.rt*100/255 #Normalize value to 0-100 scale
            commands.append((6, int(state.rt*100)))
        
        #Control wheel steering using the left stick
        #Push left to turn left, right to turn right
        if state.lx != 0:
            #steeringMagnitude = state.lx*100/32767#Normalize value to 0-100 scale
            commands.append((7, int(state.lx*100)))
        
        return commands


