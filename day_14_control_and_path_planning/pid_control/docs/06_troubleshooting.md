# 06. 트러블슈팅

## 1. launch에서 `robot_description` YAML 파싱 에러가 나는 경우

증상:

```text
Unable to parse the value of parameter robot_description as yaml
```

원인:

```text
robot_description을 일반 문자열로 넘기지 않아서 launch_ros가 YAML처럼 해석하려고 할 때 발생한다.
```

이 정리본의 launch 파일에서는 `ParameterValue(..., value_type=str)`을 사용한다. 그래도 에러가 나면 오래된 install 결과를 실행 중일 가능성이 높다.

```bash
cd projects/ros2_pid_arm_lab
rm -rf build install log
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## 2. controller가 active가 안 되는 경우

확인:

```bash
ros2 control list_controllers
```

정상 상태:

```text
joint_state_broadcaster active
effort_controller active
```

안 뜨면 아래를 확인한다.

```bash
ros2 service list | grep controller_manager
ros2 param list /controller_manager
```

주요 원인:

```text
- gazebo_ros2_control 패키지가 설치되지 않음
- xacro의 ros2_control joint name과 controller yaml의 joints 항목이 다름
- robot_state_publisher가 robot_description을 제대로 제공하지 않음
- Gazebo spawn이 실패함
```

## 3. PID 노드가 `Waiting for arm_joint`만 출력하는 경우

증상:

```text
Waiting for arm_joint from /joint_states...
```

확인:

```bash
ros2 topic echo /joint_states --once
```

`name` 배열에 `arm_joint`가 있어야 합니다.

없으면 아래를 확인한다.

```text
- joint_state_broadcaster가 active인지 확인
- xacro의 joint name 확인
- pid parameter joint_name 확인
```

## 4. effort 명령은 나오는데 팔이 안 움직이는 경우

확인:

```bash
ros2 topic echo /effort_controller/commands
ros2 control list_controllers
```

가능한 원인:

```text
- effort_controller가 inactive
- max_effort가 너무 작음
- kp가 너무 작음
- payload_mass가 너무 큼
- 조인트 damping/friction이 커서 작은 effort로 움직이지 않음
```

## 5. 팔이 과하게 튀거나 발산하는 경우

대응:

```bash
ros2 param set /pid_arm_controller kp 5.0
ros2 param set /pid_arm_controller kd 0.5
ros2 param set /pid_arm_controller max_effort 20.0
```

그리고 다시 천천히 올린다.

## 6. launch argument를 바꿨는데 반영이 안 되는 경우

빌드/소싱 상태를 먼저 확인한다.

```bash
which ros2
ros2 pkg prefix pid_arm_lab
source install/setup.bash
```

`--symlink-install`로 빌드하면 Python/launch 파일 수정은 재빌드 없이 반영되는 경우가 많지만, `package.xml`, `setup.py`, `data_files`가 바뀐 경우에는 재빌드가 안전합니다.

## 7. 다른 워크스페이스와 섞이는 경우

이전에 다른 workspace를 source한 터미널에서는 overlay가 섞일 수 있습니다. 가장 깔끔한 방법은 새 터미널을 열고 아래 순서만 실행하는 것이다.

```bash
cd projects/ros2_pid_arm_lab
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 pkg prefix pid_arm_lab
```

`ros2 pkg prefix pid_arm_lab` 결과가 현재 폴더의 `install/pid_arm_lab`를 가리켜야 한다.
