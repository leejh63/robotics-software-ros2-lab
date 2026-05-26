# 03. 실행 상태 확인

controller 상태 확인:

```bash
ros2 control list_controllers
```

토픽 확인:

```bash
ros2 topic list | grep -E 'joint_states|effort_controller'
ros2 topic echo /joint_states --once
ros2 topic echo /effort_controller/commands --once
```

PID 노드 parameter 확인:

```bash
ros2 param list /pid_arm_controller
ros2 param get /pid_arm_controller kp
ros2 param get /pid_arm_controller setpoint
```

노드 확인:

```bash
ros2 node list
```
