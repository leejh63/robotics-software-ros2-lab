# TF2 / Sensor / Rosbag Commands

## 1. TF tree demo

```bash
ros2 launch tf_pkg_example tf_tree_demo_launch.py
ros2 launch tf_pkg_example tf_tree_demo_launch.py use_listener:=true
ros2 launch tf_pkg_example tf_tree_demo_launch.py use_listener:=true use_rqt_tree:=true
```

확인:

```bash
ros2 run tf2_ros tf2_echo odom_robot_ns base_link_robot_ns
ros2 run tf2_ros tf2_echo odom_robot_ns m_lee
ros2 run tf2_tools view_frames
ros2 run rqt_tf_tree rqt_tf_tree
```

---

## 2. YOLO TF launch

```bash
ros2 launch tf_pkg_example lee_yolo_launch.py
ros2 launch tf_pkg_example lee_yolo_launch.py use_listener:=true use_rqt_tree:=true
ros2 launch tf_pkg_example lee_yolo_launch.py class_filter:=person object_depth:=1.5 use_listener:=true
```

확인:

```bash
ros2 topic info /image_raw0
ros2 topic info /img_yolo1
ros2 topic echo /img_yolo1 --once
ros2 run tf2_ros tf2_echo camera_frame object_person_0
ros2 run tf2_ros tf2_echo odom_robot_ns object_person_0
```

---

## 3. TF topic 확인

```bash
ros2 topic echo /tf
ros2 topic echo /tf_static
ros2 topic info /tf
ros2 topic info /tf_static
```

---

## 4. rosbag record/play

카메라/YOLO 관련 topic 기록:

```bash
ros2 bag record /image_raw0 /image_yolo1 /img_yolo1 /tf /tf_static
```

재생:

```bash
ros2 bag play <bag_dir>
```

반복 재생:

```bash
ros2 bag play <bag_dir> --loop
```

느리게 재생:

```bash
ros2 bag play <bag_dir> -r 0.5
```

---

## 5. Day 10~13용 rosbag 기록 관점

SLAM/AMCL/Nav2 재현용으로는 단순히 센서 하나만 기록하면 부족할 수 있다.

```bash
ros2 bag record /scan /odom /tf /tf_static /clock
```

namespace가 있으면 실제 이름에 맞춘다.

```bash
ros2 bag record /robot_ns/scan /robot_ns/odom /tf /tf_static /clock
```

확인:

```bash
ros2 bag info <bag_dir>
```

---

## 6. sensor header 확인

```bash
ros2 topic echo /image_raw0 --once
ros2 topic echo /img_yolo1 --once
```

확인할 필드:

```text
header.stamp
header.frame_id
```

header.frame_id가 TF tree에 연결되지 않으면 RViz/알고리즘에서 공간적으로 해석하기 어렵다.
