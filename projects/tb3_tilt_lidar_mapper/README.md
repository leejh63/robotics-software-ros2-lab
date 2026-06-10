# TurtleBot3 Tilt LiDAR Mapper

TurtleBot3에서 녹화한 2D LiDAR(`/scan`)와 IMU(`/imu`) 데이터를 이용해 LiDAR 단면을 `PointCloud2`로 변환하고 RViz2에서 누적 시각화하는 ROS2 실습 프로젝트입니다.

이 프로젝트는 **LaserScan 거리값을 보존한 상태에서 IMU 기울기만 회전행렬로 적용하는 센서 데이터 변환 흐름**을 확인하는 데 초점을 둡니다. odometry 기반 위치 이동, scan matching, loop closure, global map optimization은 포함하지 않습니다.

---

## 핵심 아이디어

LaserScan의 각 거리값 `r`은 그대로 사용합니다.

```text
p_scan = [r cos(theta), r sin(theta), 0]
v_base = R_base_scan * p_scan
p_out  = t_base_scan + R_imu_tilt * v_base
```

- `r` 자체는 스케일링하지 않습니다.
- LiDAR ray 벡터만 회전합니다.
- LiDAR 원점 offset은 별도로 더합니다.
- 기본 설정에서는 IMU yaw를 제거하고 roll/pitch 기울기만 사용합니다.

---

## 프로젝트 구조

```text
projects/tb3_tilt_lidar_mapper/
├── README.md
├── docs/
│   ├── algorithm.md
│   ├── bag_summary.md
│   └── commands.md
├── sample_bags/
│   ├── tb3_tilt_lidar_20260610_120848/
│   └── tb3_tilt_lidar_20260610_121243/
├── scripts/
│   ├── play_sample_bag.sh
│   ├── run_mapper.sh
│   └── check_topics.sh
└── src/
    └── tilt_lidar_mapper/
        ├── launch/
        │   └── tilt_cloud.launch.py
        ├── tilt_lidar_mapper/
        │   └── scan_imu_tilt_cloud.py
        ├── package.xml
        ├── setup.py
        └── setup.cfg
```

---

## 입력/출력 토픽

입력:

```text
/scan       sensor_msgs/msg/LaserScan
/imu        sensor_msgs/msg/Imu
/tf_static  tf2_msgs/msg/TFMessage
```

출력:

```text
/tilted_lidar_slice   현재 LaserScan 1장의 PointCloud2
/tilted_lidar_cloud   누적 PointCloud2
```

---

## 빌드

```bash
cd projects/tb3_tilt_lidar_mapper
source /opt/ros/humble/setup.bash
rosdep install --from-paths src -y --ignore-src
colcon build --symlink-install --packages-select tilt_lidar_mapper
source install/setup.bash
```

---

## 샘플 bag 실행

터미널 1에서 sample bag을 재생합니다.

```bash
cd projects/tb3_tilt_lidar_mapper
./scripts/play_sample_bag.sh 120848
```

반복 재생이 필요하면 `--loop`를 붙입니다.

```bash
./scripts/play_sample_bag.sh 120848 --loop
```

터미널 2에서 변환 노드를 실행합니다.

```bash
cd projects/tb3_tilt_lidar_mapper
source install/setup.bash
./scripts/run_mapper.sh
```

터미널 3에서 RViz2를 실행합니다.

```bash
source /opt/ros/humble/setup.bash
rviz2 --ros-args -p use_sim_time:=true
```

RViz2 설정:

```text
Global Options > Fixed Frame: base_link
Add > PointCloud2 > Topic: /tilted_lidar_cloud
PointCloud2 > Size(m): 0.03 ~ 0.05
PointCloud2 > Style: Flat Squares
```

현재 scan 한 장만 확인하려면 `/tilted_lidar_slice`를 추가합니다.

---

## 직접 명령어로 실행

```bash
ros2 bag play sample_bags/tb3_tilt_lidar_20260610_120848 --clock
```

```bash
ros2 launch tilt_lidar_mapper tilt_cloud.launch.py \
  use_sim_time:=true \
  world_frame:=base_link \
  height_scale:=1.0 \
  preserve_lidar_range:=true \
  fixed_lidar_origin:=true \
  use_roll_pitch_only:=true \
  zero_initial_orientation:=true \
  accumulate:=true \
  max_points:=120000
```

---

## 주요 파라미터

| 파라미터 | 기본값 | 설명 |
|---|---:|---|
| `world_frame` | `base_link` | 출력 PointCloud2의 `frame_id` |
| `base_frame` | `base_link` | LiDAR static transform 기준 프레임 |
| `accumulate` | `true` | scan을 누적할지 여부 |
| `max_points` | `120000` | 누적 point 최대 개수 |
| `point_stride` | `1` | scan point 샘플링 간격 |
| `use_roll_pitch_only` | `true` | yaw를 제거하고 roll/pitch만 사용 |
| `zero_initial_orientation` | `true` | 첫 IMU 자세를 기준 자세로 사용 |
| `height_scale` | `1.0` | z축 시각화 배율. 1.0이 거리 보존 설정 |
| `preserve_lidar_range` | `true` | LiDAR ray 벡터만 회전하여 거리값 유지 |
| `fixed_lidar_origin` | `true` | LiDAR 원점 offset을 회전과 분리 |

---

## 포함된 sample bag

`sample_bags/`에는 TurtleBot3에서 녹화한 작은 rosbag 샘플 2개가 포함되어 있습니다.

```text
/scan
/imu
/tf
/tf_static
```

카메라와 음성 데이터는 포함되어 있지 않습니다. 자세한 내용은 [`docs/bag_summary.md`](docs/bag_summary.md)를 참고합니다.

---

## 범위와 다음 단계

이 프로젝트는 LiDAR와 IMU를 이용한 기울기 기반 PointCloud 변환을 확인하는 실습입니다. 실제 방 구조에 가까운 3D map을 만들려면 다음 단계에서 `/odom` 또는 SLAM pose를 함께 반영해야 합니다.
