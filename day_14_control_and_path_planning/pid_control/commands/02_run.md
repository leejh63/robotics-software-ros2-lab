# 02. 실행

현재 폴더에서 빌드한 뒤 실행합니다.

```bash
cd projects/ros2_pid_arm_lab
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch pid_arm_lab full.launch.py
```

시뮬레이션만 실행:

```bash
ros2 launch pid_arm_lab sim.launch.py
```

시뮬레이션이 이미 떠 있을 때 PID 노드만 별도 실행:

```bash
ros2 launch pid_arm_lab pid.launch.py
```

로봇 이름과 payload 질량을 바꿔 실행:

```bash
ros2 launch pid_arm_lab full.launch.py \
  robot_name:=demo_arm \
  entity_name:=demo_arm \
  payload_mass:=2.0
```

처음부터 gain을 넣고 실행:

```bash
ros2 launch pid_arm_lab full.launch.py \
  kp:=15.0 \
  ki:=0.0 \
  kd:=1.0 \
  setpoint:=0.5
```
