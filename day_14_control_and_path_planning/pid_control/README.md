# PID Control

이 폴더는 ROS2 Humble, Gazebo Classic, `ros2_control`을 사용한 1-DOF arm PID 제어 실습을 정리합니다.

```text
docs/       PID 개념, ros2_control 흐름, 튜닝 정리
commands/   설치, 빌드, 실행, 확인, 튜닝 명령
```

실행 가능한 ROS2 workspace는 아래 위치에 분리했습니다.

```text
projects/ros2_pid_arm_lab/
└── src/
    └── pid_arm_lab/
```

## 빠른 실행

```bash
cd projects/ros2_pid_arm_lab
source /opt/ros/humble/setup.bash
rosdep install --from-paths src -y --ignore-src
colcon build --symlink-install
source install/setup.bash
ros2 launch pid_arm_lab full.launch.py
```

명령어만 보고 싶으면 `commands/`를 확인합니다. 개념 흐름은 `docs/`를 확인합니다.
