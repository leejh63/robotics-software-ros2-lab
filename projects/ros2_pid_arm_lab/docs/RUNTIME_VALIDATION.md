# ROS2 PID Arm Lab 런타임 검증 체크리스트

이 문서는 `projects/ros2_pid_arm_lab`을 ROS2 Humble + Gazebo Classic 환경에서 검증할 때 사용하는 체크리스트입니다.

---

## 검증 상태

이 문서는 실행 검증 절차를 정리한 체크리스트입니다. 아래 항목은 아직 결과가 확정되지 않은 상태이며, 실제 ROS2 Humble + Gazebo Classic 환경에서 확인한 뒤 갱신합니다.

| 항목 | 상태 | 확인 기준 |
| --- | --- | --- |
| Build | 미확인 | `colcon build --symlink-install` 성공 |
| Gazebo | 미확인 | `full.launch.py` 실행 후 Gazebo 실행 |
| ros2_control controllers | 미확인 | controller 상태가 `active` |
| PID node | 미확인 | `/pid_arm_controller` 노드 실행 |
| Joint motion | 미확인 | setpoint 변경 시 joint 움직임 확인 |

---

## 빌드 확인

```bash
cd projects/ros2_pid_arm_lab
source /opt/ros/humble/setup.bash
rosdep install --from-paths src -y --ignore-src
colcon build --symlink-install
source install/setup.bash
```

---

## 실행 확인

```bash
ros2 launch pid_arm_lab full.launch.py
```

---

## 필수 확인 명령

```bash
ros2 control list_controllers
ros2 topic echo /joint_states --once
ros2 topic echo /effort_controller/commands --once
ros2 node list | grep pid_arm_controller
```

기대 결과:

```text
joint_state_broadcaster: active
effort_controller: active
/joint_states is publishing
/effort_controller/commands is publishing
/pid_arm_controller is running
```

---

## PID 파라미터 확인

```bash
ros2 param get /pid_arm_controller kp
ros2 param get /pid_arm_controller ki
ros2 param get /pid_arm_controller kd
ros2 param get /pid_arm_controller setpoint
```

---

## 런타임 튜닝 예시

```bash
ros2 param set /pid_arm_controller kp 10.0
ros2 param set /pid_arm_controller kd 0.5
ros2 param set /pid_arm_controller setpoint 0.5
```

---

## 검증 완료 기준

아래 항목을 실제 환경에서 모두 확인한 뒤 검증 완료로 표시합니다.

```text
1. colcon build 성공
2. Gazebo 실행 성공
3. joint_state_broadcaster active
4. effort_controller active
5. /pid_arm_controller node 실행
6. /effort_controller/commands publish 확인
7. setpoint 변경 시 joint motion 확인
```
