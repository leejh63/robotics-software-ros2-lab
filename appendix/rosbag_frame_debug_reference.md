# Rosbag Frame 디버깅 참조

rosbag replay 문제를 빠르게 확인하기 위한 참조 문서다.

## 핵심 원칙

```text
--remap은 topic 이름만 바꾼다.
header.frame_id와 child_frame_id는 자동으로 바뀌지 않는다.
```

## 최소 확인 순서

```bash
ros2 bag info rosbag2_xxx
ros2 topic list | sort
ros2 topic echo /robot_ns/scan --once --field header.frame_id
ros2 topic echo /robot_ns/odom --once --field header.frame_id
ros2 topic echo /robot_ns/odom --once --field child_frame_id
ros2 run tf2_tools view_frames
```

## 예시 환경 기준 기대값

```text
scan topic: /robot_ns/scan
scan frame: base_scan
odom topic: /robot_ns/odom
odom frame: odom_robot_ns
base frame: base_footprint
TF topic: /robot_ns/tf, /robot_ns/tf_static
```

## namespace 없는 bag 재생 예시

```bash
ros2 bag play rosbag2_2026_05_13-16_27_44 \
  --clock \
  --remap /scan:=/robot_ns/scan \
  --remap /odom:=/robot_ns/odom \
  --remap /tf:=/robot_ns/tf \
  --remap /tf_static:=/robot_ns/tf_static
```

단, 이 명령은 frame 이름을 바꾸지 않는다. 재생 후 반드시 frame_id를 확인한다.
