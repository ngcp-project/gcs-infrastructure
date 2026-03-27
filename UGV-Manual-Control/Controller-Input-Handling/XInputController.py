import ctypes
from ControllerState import ControllerState

ERROR_SUCCESS = 0

XINPUT_GAMEPAD_DPAD_UP        = 0x0001
XINPUT_GAMEPAD_DPAD_DOWN      = 0x0002
XINPUT_GAMEPAD_DPAD_LEFT      = 0x0004
XINPUT_GAMEPAD_DPAD_RIGHT     = 0x0008
XINPUT_GAMEPAD_START          = 0x0010
XINPUT_GAMEPAD_BACK           = 0x0020
XINPUT_GAMEPAD_LEFT_THUMB     = 0x0040
XINPUT_GAMEPAD_RIGHT_THUMB    = 0x0080
XINPUT_GAMEPAD_LEFT_SHOULDER  = 0x0100
XINPUT_GAMEPAD_RIGHT_SHOULDER = 0x0200
XINPUT_GAMEPAD_A              = 0x1000
XINPUT_GAMEPAD_B              = 0x2000
XINPUT_GAMEPAD_X              = 0x4000
XINPUT_GAMEPAD_Y              = 0x8000

#Represents the data types used for all controller values

class XInputGamepad(ctypes.Structure):

    _fields_ = [
        ("wButtons", ctypes.c_ushort),
        ("bLeftTrigger", ctypes.c_ubyte),
        ("bRightTrigger", ctypes.c_ubyte),
        ("sThumbLX", ctypes.c_short),
        ("sThumbLY", ctypes.c_short),
        ("sThumbRX", ctypes.c_short),
        ("sThumbRY", ctypes.c_short),
    ]


#Class representing the ordinal controller frame count and state

class XInputState(ctypes.Structure):

    _fields_ = [
        ("dwPacketNumber", ctypes.c_ulong),
        ("Gamepad", XInputGamepad),
    ]


class XInputController:

    def __init__(self, controllerIndex=0, deadzone=4000, triggerThreshold=20):
        self.controllerIndex = controllerIndex
        self.deadzone = deadzone
        self.triggerThreshold = triggerThreshold
        self.xInput = self.loadXInput()

        #Define GetState method, which will update the values of the gamepad object
        self.XInputGetState = self.xInput.XInputGetState
        self.XInputGetState.argtypes = [ctypes.c_uint, ctypes.POINTER(XInputState)]
        self.XInputGetState.restype = ctypes.c_uint


    def loadXInput(self):

        for dllName in ("xinput1_4.dll", "xinput1_3.dll", "xinput9_1_0.dll"):
            try:
                loadedDLL = ctypes.WinDLL(dllName)
                print(f"loaded {loadedDLL}")
                return loadedDLL
            except OSError:
                pass
        raise OSError("Could not load an XInput DLL.")


    #Applies the object's stick deadzone to account for drift

    def normalizeStick(self, value):
        if abs(value) < self.deadzone:
            return 0.0
        return value / 32767.0 if value >= 0 else value / 32768.0


    #Applies the object's trigger threshold to account for drift
    def normalizeTrigger(self, value):
        if value < self.triggerThreshold:
            return 0.0
        return value / 255.0


    #Compares XinputGamepad values to bitmasks to determine if it is pressed or not
    def buttonPressed(self, buttons, mask):
        return (buttons & mask) != 0


    def read(self):
        state = XInputState()
        result = self.XInputGetState(self.controllerIndex, ctypes.byref(state))

        if result != 0:
            return None  # controller disconnected or unavailable

        gp = state.Gamepad
        buttons = gp.wButtons

        return ControllerState(
            a=self.buttonPressed(buttons, XINPUT_GAMEPAD_A),
            b=self.buttonPressed(buttons, XINPUT_GAMEPAD_B),
            x=self.buttonPressed(buttons, XINPUT_GAMEPAD_X),
            y=self.buttonPressed(buttons, XINPUT_GAMEPAD_Y),
            lb=self.buttonPressed(buttons, XINPUT_GAMEPAD_LEFT_SHOULDER),
            rb=self.buttonPressed(buttons, XINPUT_GAMEPAD_RIGHT_SHOULDER),
            start=self.buttonPressed(buttons, XINPUT_GAMEPAD_START),
            back=self.buttonPressed(buttons, XINPUT_GAMEPAD_BACK),
            dpad_up=self.buttonPressed(buttons, XINPUT_GAMEPAD_DPAD_UP),
            dpad_down=self.buttonPressed(buttons, XINPUT_GAMEPAD_DPAD_DOWN),
            dpad_left=self.buttonPressed(buttons, XINPUT_GAMEPAD_DPAD_LEFT),
            dpad_right=self.buttonPressed(buttons, XINPUT_GAMEPAD_DPAD_RIGHT),
            left_thumb=self.buttonPressed(buttons, XINPUT_GAMEPAD_LEFT_THUMB),
            right_thumb=self.buttonPressed(buttons, XINPUT_GAMEPAD_RIGHT_THUMB),
            lt=self.normalizeTrigger(gp.bLeftTrigger),
            rt=self.normalizeTrigger(gp.bRightTrigger),
            lx=self.normalizeStick(gp.sThumbLX),
            ly=self.normalizeStick(gp.sThumbLY),
            rx=self.normalizeStick(gp.sThumbRX),
            ry=self.normalizeStick(gp.sThumbRY),
            stateFrame=state.dwPacketNumber
    )