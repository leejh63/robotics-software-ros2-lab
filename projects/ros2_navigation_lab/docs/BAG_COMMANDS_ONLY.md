# Rosbag SLAM/Nav2 Commands Only

> rosbag 원본 데이터는 이 저장소에 포함하지 않습니다. 실행할 때는 사용자가 직접 준비한 bag 디렉토리를 `BAG_DIR=/path/to/rosbag_directory`로 지정합니다.


`$BAG_DIR`는 실제 rosbag 디렉토리 경로로 바꿔서 사용합니다. 개인 PC 경로나 특정 rosbag 이름은 문서에 고정하지 않습니다.

```bash
export BAG_DIR=/path/to/rosbag_directory
```

환경변수는 터미널마다 따로 적용됩니다. launch 터미널과 rosbag replay 터미널을 분리해서 쓴다면, rosbag을 실행하는 터미널에서도 `export BAG_DIR=...`를 한 번 실행합니다.

---

## 1. Build

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select lee_robot_description
source install/setup.bash
```

---

## 2. Rosbag info

```bash
ros2 bag info "$BAG_DIR"
```

---

## 3. SLAM launch

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch lee_robot_description bag_slam.launch.py
```

---

## 4. Rosbag play, recommended `/lee/*` remap mode

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 bag play "$BAG_DIR" \
  --clock \
  --topics /scan /odom /tf /tf_static \
  --remap /scan:=/lee/scan \
          /odom:=/lee/odom \
          /tf:=/lee/tf \
          /tf_static:=/lee/tf_static
```

fallback:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 bag play "$BAG_DIR" \
  --clock \
  --topics /scan /odom /tf /tf_static \
  --ros-args \
  -r /scan:=/lee/scan \
  -r /odom:=/lee/odom \
  -r /tf:=/lee/tf \
  -r /tf_static:=/lee/tf_static
```

느리게 반복 재생하면서 RViz에서 위치를 맞출 때는 아래 명령을 사용합니다.

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 bag play "$BAG_DIR" \
  --clock \
  --loop \
  -r 0.2 \
  --topics /scan /odom /tf /tf_static \
  --remap /scan:=/lee/scan \
          /odom:=/lee/odom \
          /tf:=/lee/tf \
          /tf_static:=/lee/tf_static
```

---

## 5. Save map

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run nav2_map_server map_saver_cli \
  -f src/lee_robot_description/maps/bag_slam_map \
  --ros-args -r /map:=/lee/map
```

---

## 6. Localization with saved map

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch lee_robot_description bag_localization.launch.py
```

rosbag replay:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 bag play "$BAG_DIR" \
  --clock \
  --topics /scan /odom /tf /tf_static \
  --remap /scan:=/lee/scan \
          /odom:=/lee/odom \
          /tf:=/lee/tf \
          /tf_static:=/lee/tf_static
```

initial pose는 RViz의 `2D Pose Estimate`로 지정합니다.

```text
RViz 상단 2D Pose Estimate 선택
→ map 위에서 로봇 위치 클릭
→ 로봇이 바라보는 방향으로 드래그
→ /lee/scan 점들이 /lee/map 벽과 겹치는지 확인
```

명령어로 직접 넣어야 한다면 `x=0.0, y=0.0`을 고정으로 쓰지 말고, RViz의 `Publish Point`와 `/clicked_point`로 좌표를 확인한 뒤 사용합니다.

```bash
ros2 topic echo /clicked_point
```

orientation은 2D yaw 기준으로 `z = sin(yaw / 2)`, `w = cos(yaw / 2)`입니다.


---

## 7. Nav2 costmap with saved map + rosbag scan

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch lee_robot_description bag_nav2.launch.py
```

rosbag replay:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 bag play "$BAG_DIR" \
  --clock \
  --topics /scan /odom /tf /tf_static \
  --remap /scan:=/lee/scan \
          /odom:=/lee/odom \
          /tf:=/lee/tf \
          /tf_static:=/lee/tf_static
```

확인:

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
ros2 topic echo /lee/map --once --qos-durability transient_local
ros2 topic echo /amcl_pose --once
ros2 topic list | sort | grep costmap
ros2 topic echo /lee/global_costmap/costmap --once
ros2 topic echo /lee/local_costmap/costmap --once
ros2 run tf2_ros tf2_echo map_lee odom --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
ros2 run tf2_ros tf2_echo odom base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

---

## 8. Raw topic replay mode

rosbag 원본 topic을 그대로 쓰는 방식입니다.

```bash
ros2 bag play "$BAG_DIR" \
  --clock \
  --topics /scan /odom /tf /tf_static
```

SLAM launch도 root topic을 보게 바꿉니다.

```bash
ros2 launch lee_robot_description bag_slam.launch.py \
  use_rviz:=false \
  scan_topic:=/scan \
  map_topic:=/map \
  map_updates_topic:=/map_updates \
  tf_topic:=/tf \
  tf_static_topic:=/tf_static
```
