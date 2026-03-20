class ControllerState:
    def __init__(
        self,
        a=False, b=False, x=False, y=False,
        lb=False, rb=False,
        start=False, back=False,
        dpad_up=False, dpad_down=False, dpad_left=False, dpad_right=False,
        left_thumb=False, right_thumb=False,
        lt=0.0, rt=0.0,
        lx=0.0, ly=0.0,
        rx=0.0, ry=0.0,
        stateFrame=0
    ):
        self.a = a
        self.b = b
        self.x = x
        self.y = y
        self.lb = lb
        self.rb = rb
        self.start = start
        self.back = back
        self.dpad_up = dpad_up
        self.dpad_down = dpad_down
        self.dpad_left = dpad_left
        self.dpad_right = dpad_right
        self.left_thumb = left_thumb
        self.right_thumb = right_thumb
        self.lt = lt
        self.rt = rt
        self.lx = lx
        self.ly = ly
        self.rx = rx
        self.ry = ry
        self.stateFrame = stateFrame

    def __repr__(self):
        return (
        "Controller State"
        f"\n A={self.a}, B={self.b}, X={self.x}, Y={self.y}, "
        f" Lb={self.lb}, Rb={self.rb}"
        f" Lt={self.lt:.3f}, Rt={self.rt:.3f}"
        f" Back={self.back}, Start={self.start}"
        f" Left Thumb={self.left_thumb}, Right Thumb={self.right_thumb}"
        f" Left Stick X Axis={self.lx:.3f}, Left Stick Y Axis={self.ly:.3f}"
        f" Right Stick X Axis={self.rx:.3f}, Right Stick Y Axis={self.ry:.3f}"

        )