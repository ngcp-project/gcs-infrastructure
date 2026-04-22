def clamp(v, lo, high):
    return max(lo, min(v, high))

class ArmController:
    def __init__(self, num_joints=2, inc_dec_val=5.0,
                 joint0_limits=(0.0, 170.0),
                 joint1_limits=(75.0, 225.0)):
        self.num_joints = num_joints
        self.inc_dec_val = inc_dec_val
        self.joint0_lo, self.joint0_hi = joint0_limits
        self.joint1_lo, self.joint1_hi = joint1_limits
        self.joint_positions = [0.0, self.joint1_lo]

    def get_positions(self):
        return self.joint_positions.copy()

    def set_positions(self, positions):
        if len(positions) != self.num_joints:
            raise ValueError(f"Expected {self.num_joints} joint positions, got {len(positions)}")
        self.joint_positions = positions.copy()

    def reset(self):
        self.joint_positions = [0.0, self.joint1_lo]

    def update_joint(self, joint_index, delta, min_limit, max_limit):
        if not (0 <= joint_index < self.num_joints):
            raise ValueError(f"Joint index {joint_index} out of range")
        self.joint_positions[joint_index] += delta
        self.joint_positions[joint_index] = clamp(self.joint_positions[joint_index], min_limit, max_limit)

    def process_arm_control(self, dt, ud_pad, lr_pad):
        """LT held: D-pad left/right controls joint 0, D-pad up/down controls joint 1."""
        step = self.inc_dec_val * dt
        self.update_joint(0, -float(lr_pad) * step, self.joint0_lo, self.joint0_hi)
        self.update_joint(1, float(ud_pad) * step, self.joint1_lo, self.joint1_hi)

    def get_joint_status(self):
        return f"Arm Joints: [{self.joint_positions[0]:.1f}, {self.joint_positions[1]:.1f}]"
