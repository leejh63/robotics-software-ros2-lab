# Commands

## 1. Build

```bash
cd projects/tb3_tilt_lidar_mapper
source /opt/ros/humble/setup.bash
rosdep install --from-paths src -y --ignore-src
colcon build --symlink-install --packages-select tilt_lidar_mapper
source install/setup.bash
```

## 2. Play sample rosbag

```bash
cd projects/tb3_tilt_lidar_mapper
./scripts/play_sample_bag.sh 120848
```

Loop playback:

```bash
./scripts/play_sample_bag.sh 120848 --loop
```

Second sample:

```bash
./scripts/play_sample_bag.sh 121243
```

## 3. Run mapper

```bash
cd projects/tb3_tilt_lidar_mapper
source install/setup.bash
./scripts/run_mapper.sh
```

Equivalent direct command:

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

## 4. RViz2

```bash
source /opt/ros/humble/setup.bash
rviz2 --ros-args -p use_sim_time:=true
```

RViz2 settings:

```text
Fixed Frame: base_link
PointCloud2 Topic: /tilted_lidar_cloud
Size(m): 0.03 ~ 0.05
Style: Flat Squares
```

## 5. Topic checks

```bash
./scripts/check_topics.sh
```

Manual checks:

```bash
ros2 topic list | grep tilted
ros2 topic echo /tilted_lidar_cloud --once --field width
ros2 topic hz /tilted_lidar_cloud
```

## 6. Record new TurtleBot3 sensor data

TurtleBot3 bringup 후 `/scan`, `/imu`, `/tf`, `/tf_static`이 publish되는 상태에서 실행합니다.

```bash
mkdir -p ~/bags
ros2 bag record -o ~/bags/tb3_tilt_lidar_$(date +%Y%m%d_%H%M%S) \
  /scan \
  /imu \
  /tf \
  /tf_static
```

녹화 종료는 `Ctrl+C`로 합니다. 종료 후에는 `ros2 bag info`로 metadata가 정상 작성되었는지 확인합니다.
