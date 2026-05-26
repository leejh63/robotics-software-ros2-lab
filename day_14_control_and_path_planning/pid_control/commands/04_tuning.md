# 04. PID 튜닝 명령어

P 제어부터 시작합니다.

```bash
ros2 param set /pid_arm_controller ki 0.0
ros2 param set /pid_arm_controller kd 0.0
ros2 param set /pid_arm_controller kp 10.0
ros2 param set /pid_arm_controller setpoint 0.5
```

흔들림이 크면 D항을 조금씩 추가합니다.

```bash
ros2 param set /pid_arm_controller kd 0.5
ros2 param set /pid_arm_controller kd 1.0
```

목표 근처 offset이 계속 남으면 I항을 아주 작게 추가합니다.

```bash
ros2 param set /pid_arm_controller ki 0.05
ros2 param set /pid_arm_controller ki 0.1
```

출력이 너무 크면 제한값을 낮춥니다.

```bash
ros2 param set /pid_arm_controller max_effort 30.0
```

중력 때문에 팔이 처지면 중력 보상값을 실험합니다.

```bash
ros2 param set /pid_arm_controller gravity_gain 1.0
ros2 param set /pid_arm_controller gravity_gain -1.0
```

현재 설정 확인:

```bash
ros2 param get /pid_arm_controller kp
ros2 param get /pid_arm_controller ki
ros2 param get /pid_arm_controller kd
ros2 param get /pid_arm_controller setpoint
```
