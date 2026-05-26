# 04. Gazebo Plugin과 ROS2 Topic 흐름

## 1. Gazebo plugin이 하는 일

URDF/Xacro로 link와 joint를 만들었다고 해서 로봇이 자동으로 움직이거나 센서값을 발행하지는 않는다.

Gazebo plugin은 아래 경계를 연결한다.

```text
Gazebo 시뮬레이션 세계
  물리 계산, 바퀴 회전, ray sensor, camera, imu
        ↓ plugin
ROS2 topic 세계
  /lee/cmd_vel, /lee/odom, /lee/scan, /lee/imu, /lee/image_raw
```

즉 plugin은 “Gazebo 내부 데이터”를 “ROS2 메시지”로 바꾸거나, 반대로 ROS2 명령을 Gazebo 동작으로 바꾸는 어댑터다.

---

## 2. 현재 plugin 요약

`urdf/turtlebot_gaze.xacro`에 들어 있는 핵심 plugin은 다음이다.

| plugin | 역할 | 주요 topic |
|---|---|---|
| `libgazebo_ros_diff_drive.so` | `/lee/cmd_vel`을 받아 바퀴를 구동하고 odom 발행 | `/lee/cmd_vel`, `/lee/odom` |
| `libgazebo_ros_joint_state_publisher.so` | 바퀴 joint 상태 발행 | `/lee/joint_states` |
| `libgazebo_ros_ray_sensor.so` | Gazebo ray sensor를 LaserScan으로 발행 | `/lee/scan` |
| `libgazebo_ros_imu_sensor.so` | IMU 센서값 발행 | `/lee/imu` |
| `libgazebo_ros_camera.so` | 카메라 이미지와 camera info 발행 | `/lee/image_raw`, `/lee/camera_info` |

---

## 3. Diff Drive plugin

Diff Drive plugin은 로봇 이동의 핵심이다.

현재 설정의 핵심:

```xml
<namespace>/lee</namespace>
<left_joint>wheel_left_joint</left_joint>
<right_joint>wheel_right_joint</right_joint>
<command_topic>cmd_vel</command_topic>
<odometry_topic>odom</odometry_topic>
<odometry_frame>odom_lee</odometry_frame>
<robot_base_frame>base_footprint</robot_base_frame>
```

`namespace`가 `/lee`이므로 상대 topic인 `cmd_vel`, `odom`은 실제로 다음처럼 해석된다.

```text
cmd_vel -> /lee/cmd_vel
odom    -> /lee/odom
```

흐름:

```text
teleop 또는 회피 노드
        ↓ Twist
/lee/cmd_vel
        ↓
Gazebo diff_drive plugin
        ↓
wheel_left_joint / wheel_right_joint 회전
        ↓
/lee/odom 발행
        ↓
odom_lee -> base_footprint 관계 갱신
```

주의할 점:

```text
left_joint/right_joint 이름이 turtlebot.xacro의 joint 이름과 일치해야 한다.
wheel_separation, wheel_diameter 값이 실제 모델 크기와 맞아야 odom이 자연스럽다.
```

---

## 4. Joint State plugin

바퀴 joint가 움직이면 현재 joint 상태가 필요하다.

```text
Gazebo wheel joint 상태
        ↓
libgazebo_ros_joint_state_publisher.so
        ↓
/lee/joint_states
        ↓
robot_state_publisher
        ↓
/lee/tf
```

`robot_state_publisher`는 이 값을 받아 바퀴 link의 동적 TF를 계산할 수 있다.

---

## 5. LiDAR plugin

LiDAR는 Day 11 SLAM과 Day 12 AMCL에서 가장 중요한 입력이다.

현재 설정의 핵심:

```xml
<gazebo reference="base_scan">
  <sensor name="laser" type="ray">
    <samples>360</samples>
    <min_angle>-3.14159</min_angle>
    <max_angle>3.14159</max_angle>
    <min>0.12</min>
    <max>3.5</max>
    <plugin filename="libgazebo_ros_ray_sensor.so">
      <namespace>/lee</namespace>
      <remapping>~/out:=scan</remapping>
      <output_type>sensor_msgs/LaserScan</output_type>
      <frame_name>base_scan</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

흐름:

```text
Gazebo ray sensor
        ↓
거리 배열 계산
        ↓
libgazebo_ros_ray_sensor.so
        ↓
/lee/scan
        ↓
RViz2 / lidar_wall_follower.py / SLAM Toolbox / AMCL
```

중요한 점:

```text
/lee/scan은 topic 이름이다.
base_scan은 LaserScan 메시지의 frame_id다.
```

---

## 6. IMU plugin

IMU plugin은 `imu_link`에 붙어 있다.

```text
Gazebo IMU sensor
        ↓
libgazebo_ros_imu_sensor.so
        ↓
/lee/imu
```

현재 실습의 핵심은 SLAM/Nav2에서 IMU를 깊게 쓰는 것보다, Gazebo sensor plugin이 ROS2 `sensor_msgs/msg/Imu`를 만들 수 있다는 점을 확인하는 것이다.

---

## 7. Camera plugin

Camera plugin은 `camera_link`에 붙어 있다.

현재 설정은 camera plugin 기본 topic을 remap해서 다음 topic을 만들도록 되어 있다.

```text
/lee/image_raw
/lee/camera_info
```

흐름:

```text
Gazebo camera sensor
        ↓
libgazebo_ros_camera.so
        ↓
/lee/image_raw
/lee/camera_info
        ↓
RViz2 또는 OpenCV/YOLO 노드로 연결 가능
```

Day 06~09의 `camera_pkg`에서 다룬 OpenCV/YOLO 흐름과 연결할 수 있지만, Day 10 자체의 핵심은 camera plugin이 image topic을 만들어준다는 점이다.

---

## 8. 전체 topic 흐름

```text
[Command]
teleop_twist_keyboard or lidar_wall_follower.py
        └── /lee/cmd_vel
                ↓
        Gazebo diff_drive plugin
                ├── /lee/odom
                └── wheel joint motion

[Joint]
Gazebo joint state plugin
        └── /lee/joint_states
                ↓
        robot_state_publisher
                ├── /lee/tf
                └── /lee/tf_static

[Sensors]
Gazebo ray sensor
        └── /lee/scan

Gazebo imu sensor
        └── /lee/imu

Gazebo camera sensor
        ├── /lee/image_raw
        └── /lee/camera_info
```

---

## 9. 핵심 결론

```text
URDF/Xacro는 구조를 만든다.
Gazebo plugin은 그 구조에 실제 시뮬레이션 동작과 ROS2 topic을 붙인다.
```

Day 10에서 plugin 흐름을 정확히 이해해야 Day 11에서 `/lee/scan`과 `/lee/odom`이 왜 SLAM의 입력이 되는지 이해할 수 있다.
