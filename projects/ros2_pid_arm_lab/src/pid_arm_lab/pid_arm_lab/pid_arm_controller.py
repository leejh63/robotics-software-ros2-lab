#!/usr/bin/env python3

import math
from typing import Iterable

import rclpy
from rcl_interfaces.msg import SetParametersResult
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray


class PIDArmController(Node):
    """단일 조인트 팔을 effort 방식으로 제어하는 PID 노드입니다.

    sensor_msgs/JointState에서 현재 조인트 위치를 읽고,
    JointGroupEffortController가 받을 Float64MultiArray effort 명령을 발행합니다.
    """

    def __init__(self) -> None:
        super().__init__('pid_arm_controller')

        self.declare_parameter('kp', 0.0)
        self.declare_parameter('ki', 0.0)
        self.declare_parameter('kd', 0.0)
        self.declare_parameter('setpoint', 0.0)
        self.declare_parameter('dt', 0.01)
        self.declare_parameter('max_effort', 50.0)
        self.declare_parameter('integral_limit', 10.0)
        self.declare_parameter('gravity_gain', 0.0)
        self.declare_parameter('use_actual_dt', True)
        self.declare_parameter('reset_integral_on_setpoint_change', True)
        self.declare_parameter('joint_name', 'arm_joint')
        self.declare_parameter('joint_states_topic', '/joint_states')
        self.declare_parameter('command_topic', '/effort_controller/commands')

        self.kp = self._get_float('kp')
        self.ki = self._get_float('ki')
        self.kd = self._get_float('kd')
        self.setpoint = self._get_float('setpoint')
        self.dt = self._get_float('dt')
        self.max_effort = self._get_float('max_effort')
        self.integral_limit = self._get_float('integral_limit')
        self.gravity_gain = self._get_float('gravity_gain')
        self.use_actual_dt = self._get_bool('use_actual_dt')
        self.reset_integral_on_setpoint_change = self._get_bool(
            'reset_integral_on_setpoint_change'
        )

        self.joint_name = self._get_str('joint_name')
        self.joint_states_topic = self._get_str('joint_states_topic')
        self.command_topic = self._get_str('command_topic')

        self.integral = 0.0
        self.prev_error = 0.0
        self.current_position = 0.0
        self.has_joint_state = False
        self.has_prev_error = False
        self.prev_time = self.get_clock().now()

        self.joint_sub = self.create_subscription(
            JointState,
            self.joint_states_topic,
            self.joint_callback,
            10,
        )

        self.effort_pub = self.create_publisher(
            Float64MultiArray,
            self.command_topic,
            10,
        )

        self.timer = self.create_timer(self.dt, self.control_loop)
        self.add_on_set_parameters_callback(self.param_callback)

        self.get_logger().info(
            'PID arm controller 시작 | '
            f'joint={self.joint_name} | '
            f'state_topic={self.joint_states_topic} | '
            f'command_topic={self.command_topic} | '
            f'kp={self.kp} ki={self.ki} kd={self.kd} | '
            f'setpoint={self.setpoint} rad | '
            f'dt={self.dt} | max_effort={self.max_effort} | '
            f'integral_limit={self.integral_limit} | '
            f'gravity_gain={self.gravity_gain} | '
            f'use_actual_dt={self.use_actual_dt}'
        )

    def _get_float(self, name: str) -> float:
        return float(self.get_parameter(name).value)

    def _get_bool(self, name: str) -> bool:
        value = self.get_parameter(name).value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)

    def _get_str(self, name: str) -> str:
        return str(self.get_parameter(name).value)

    def _validate_float_positive(self, name: str, value: object) -> str:
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            return f'{name} 값은 숫자여야 합니다'
        if parsed <= 0.0:
            return f'{name} 값은 0보다 커야 합니다'
        return ''

    def param_callback(self, params: Iterable[object]) -> SetParametersResult:
        for param in params:
            if param.name in ('dt', 'max_effort'):
                reason = self._validate_float_positive(param.name, param.value)
                if reason:
                    return SetParametersResult(successful=False, reason=reason)

            if param.name == 'integral_limit':
                try:
                    value = float(param.value)
                except (TypeError, ValueError):
                    return SetParametersResult(
                        successful=False,
                        reason='integral_limit 값은 숫자여야 합니다',
                    )
                if value < 0.0:
                    return SetParametersResult(
                        successful=False,
                        reason='integral_limit 값은 0 이상이어야 합니다',
                    )

        for param in params:
            if param.name == 'kp':
                self.kp = float(param.value)
            elif param.name == 'ki':
                self.ki = float(param.value)
            elif param.name == 'kd':
                self.kd = float(param.value)
            elif param.name == 'setpoint':
                self.setpoint = float(param.value)
                self.has_prev_error = False
                if self.reset_integral_on_setpoint_change:
                    self.integral = 0.0
            elif param.name == 'dt':
                new_dt = float(param.value)
                if new_dt != self.dt:
                    self.dt = new_dt
                    self.timer.cancel()
                    self.timer = self.create_timer(self.dt, self.control_loop)
                    self.has_prev_error = False
                    self.prev_time = self.get_clock().now()
            elif param.name == 'max_effort':
                self.max_effort = float(param.value)
            elif param.name == 'integral_limit':
                self.integral_limit = float(param.value)
                self.integral = self._clamp(
                    self.integral,
                    -self.integral_limit,
                    self.integral_limit,
                )
            elif param.name == 'gravity_gain':
                self.gravity_gain = float(param.value)
            elif param.name == 'use_actual_dt':
                self.use_actual_dt = self._coerce_bool(param.value)
            elif param.name == 'reset_integral_on_setpoint_change':
                self.reset_integral_on_setpoint_change = self._coerce_bool(param.value)
            elif param.name == 'joint_name':
                self.joint_name = str(param.value)
                self.has_joint_state = False
                self.has_prev_error = False
                self.integral = 0.0
            elif param.name == 'joint_states_topic':
                self.get_logger().warn(
                    'joint_states_topic이 변경되었지만 현재 subscription은 재생성되지 않습니다. '
                    '토픽 변경을 적용하려면 노드를 재시작하세요.'
                )
            elif param.name == 'command_topic':
                self.get_logger().warn(
                    'command_topic이 변경되었지만 현재 publisher는 재생성되지 않습니다. '
                    '토픽 변경을 적용하려면 노드를 재시작하세요.'
                )

        self.get_logger().info(
            'Parameter 갱신 | '
            f'kp={self.kp} ki={self.ki} kd={self.kd} | '
            f'setpoint={self.setpoint} | dt={self.dt} | '
            f'max_effort={self.max_effort} | '
            f'integral_limit={self.integral_limit} | '
            f'gravity_gain={self.gravity_gain}',
            throttle_duration_sec=1.0,
        )

        return SetParametersResult(successful=True)

    def _coerce_bool(self, value: object) -> bool:
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)

    def joint_callback(self, msg: JointState) -> None:
        if self.joint_name not in msg.name:
            return

        idx = msg.name.index(self.joint_name)
        if idx >= len(msg.position):
            self.get_logger().warn(
                f'{self.joint_name}은 JointState.name에 있지만 '
                'JointState.position에 대응되는 index가 없습니다.',
                throttle_duration_sec=1.0,
            )
            return

        self.current_position = msg.position[idx]
        self.has_joint_state = True

    def control_loop(self) -> None:
        if not self.has_joint_state:
            self.get_logger().warn(
                f'{self.joint_states_topic}에서 {self.joint_name} 수신 대기 중...',
                throttle_duration_sec=1.0,
            )
            self.prev_time = self.get_clock().now()
            return

        actual_dt = self._compute_dt()
        error = self.setpoint - self.current_position

        p_term = self.kp * error

        prev_integral = self.integral
        self.integral += error * actual_dt
        if self.integral_limit > 0.0:
            self.integral = self._clamp(
                self.integral,
                -self.integral_limit,
                self.integral_limit,
            )
        i_term = self.ki * self.integral

        if self.has_prev_error:
            derivative = (error - self.prev_error) / actual_dt
        else:
            derivative = 0.0
            self.has_prev_error = True

        d_term = self.kd * derivative
        self.prev_error = error

        gravity_comp = -self.gravity_gain * math.cos(self.current_position)
        raw_effort = p_term + i_term + d_term + gravity_comp
        effort = self._clamp(raw_effort, -self.max_effort, self.max_effort)

        if effort != raw_effort:
            self.integral = prev_integral
            i_term = self.ki * self.integral

        msg = Float64MultiArray()
        msg.data = [float(effort)]
        self.effort_pub.publish(msg)

        self.get_logger().info(
            f'pos={self.current_position:+.4f} | '
            f'err={error:+.4f} | '
            f'eff={effort:+.3f} | '
            f'P={p_term:+.2f} '
            f'I={i_term:+.2f} '
            f'D={d_term:+.2f} '
            f'G={gravity_comp:+.2f} '
            f'dt={actual_dt:.4f}',
            throttle_duration_sec=0.5,
        )

    def _compute_dt(self) -> float:
        if not self.use_actual_dt:
            return self.dt

        now = self.get_clock().now()
        elapsed = (now - self.prev_time).nanoseconds / 1_000_000_000.0
        self.prev_time = now

        if elapsed <= 0.0:
            return self.dt
        return elapsed

    def publish_zero_effort(self) -> None:
        zero = Float64MultiArray()
        zero.data = [0.0]
        self.effort_pub.publish(zero)

    @staticmethod
    def _clamp(value: float, low: float, high: float) -> float:
        return max(low, min(high, value))


def main(args=None) -> None:
    rclpy.init(args=args)
    node = PIDArmController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.publish_zero_effort()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
