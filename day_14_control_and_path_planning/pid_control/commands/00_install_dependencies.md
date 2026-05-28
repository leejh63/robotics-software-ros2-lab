# 00. 의존성 설치

`projects/ros2_pid_arm_lab` 폴더가 ROS2 workspace root입니다. 별도의 외부 workspace를 만들지 않습니다.

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

`rosdep install`은 `src/` 아래의 `package.xml`을 보고 필요한 시스템 패키지를 설치합니다. `build/`, `install/`, `log/` 폴더를 직접 건드리는 명령은 아닙니다.
