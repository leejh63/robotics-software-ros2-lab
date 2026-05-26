# 04. 재현 절차

PID arm 실습의 실행 코드는 `projects/ros2_pid_arm_lab/` 폴더를 ROS2 workspace root로 사용합니다.

```text
projects/ros2_pid_arm_lab/
└── src/pid_arm_lab/       # 실제 ROS2 패키지
```

아래 명령은 저장소 루트에서 실행한다고 가정합니다.

## 1. 의존성 설치

```bash
cd projects/ros2_pid_arm_lab
source /opt/ros/humble/setup.bash
sudo apt update
sudo apt install -y \
  python3-colcon-common-extensions \
  python3-rosdep \
  python3-setuptools \
  ros-humble-xacro \
  ros-humble-robot-state-publisher \
  ros-humble-gazebo-ros \
  ros-humble-gazebo-ros2-control \
  ros-humble-controller-manager \
  ros-humble-joint-state-broadcaster \
  ros-humble-effort-controllers \
  ros-humble-ros2controlcli
```

`rosdep` 초기화는 PC당 한 번만 하면 됩니다.

```bash
sudo rosdep init 2>/dev/null || true
rosdep update
rosdep install --from-paths src -y --ignore-src
```

## 2. 빌드

```bash
cd projects/ros2_pid_arm_lab
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

정상 빌드 확인:

```bash
ros2 pkg prefix pid_arm_lab
ros2 pkg executables pid_arm_lab
```

## 3. 전체 실행

```bash
ros2 launch pid_arm_lab full.launch.py
```

## 4. 실행 상태 확인

```bash
ros2 control list_controllers
ros2 topic echo /joint_states --once
ros2 topic list | grep effort
ros2 node list
```

정상 controller 상태 예시는 아래와 같습니다.

```text
joint_state_broadcaster active
effort_controller active
```

## 5. PID 튜닝

```bash
ros2 param set /pid_arm_controller kp 15.0
ros2 param set /pid_arm_controller ki 0.0
ros2 param set /pid_arm_controller kd 1.0
ros2 param set /pid_arm_controller setpoint 0.5
```

## 6. 클린 빌드

```bash
cd projects/ros2_pid_arm_lab
rm -rf build install log
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## 7. 재현성 체크 기준

아래가 모두 되면 최소 재현성은 확보된 상태로 볼 수 있습니다.

```text
1. rosdep install이 통과한다.
2. colcon build가 통과한다.
3. ros2 launch pid_arm_lab full.launch.py가 실행된다.
4. ros2 control list_controllers에서 두 controller가 active다.
5. /joint_states가 나오고, /effort_controller/commands가 발행된다.
6. ros2 param set으로 setpoint, kp, kd를 바꿀 수 있다.
```
