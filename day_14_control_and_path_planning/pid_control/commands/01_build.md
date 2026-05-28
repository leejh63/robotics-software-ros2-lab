# 01. 빌드

`projects/ros2_pid_arm_lab` 폴더가 ROS2 workspace root입니다. `~/ros2_ws` 같은 별도 폴더를 따로 만들지 않습니다.

```bash
cd projects/ros2_pid_arm_lab
source /opt/ros/humble/setup.bash
rosdep install --from-paths src -y --ignore-src
colcon build --symlink-install
source install/setup.bash
```

정상 빌드 확인:

```bash
ros2 pkg prefix pid_arm_lab
ros2 pkg executables pid_arm_lab
```

클린 빌드가 필요할 때:

```bash
rm -rf build install log
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```
