# Troubleshooting Quick Diagnosis

이 문서는 SLAM, AMCL, Nav2 문제가 생겼을 때 가장 먼저 볼 빠른 진단표다.

목표는 바로 파라미터를 바꾸는 것이 아니라, 문제가 어느 층에서 끊겼는지 먼저 분리하는 것이다.

```text
실행 환경
→ node 존재 여부
→ topic 존재 여부
→ message 발행 여부
→ frame_id / TF chain
→ lifecycle active 여부
→ parameter 적용 여부
→ RViz 표시 설정
```

---

## 1. 빠른 증상별 진단표

| 증상 | 먼저 볼 것 | 확인 명령 | 다음 문서 |
|---|---|---|---|
| package를 못 찾음 | 빌드/source 문제 | `ros2 pkg list \| grep lee_robot_description` | `appendix/command_execution_conventions.md` |
| topic은 있는데 데이터가 없음 | publish 여부 | `ros2 topic echo /robot_ns/scan --once` | `appendix/ros2_navigation_debug_order.md` |
| RViz에 map/scan이 안 보임 | CLI 정상 여부와 RViz 설정 분리 | `ros2 topic echo /robot_ns/map --once` | `appendix/troubleshooting_index.md` |
| SLAM map이 안 생김 | scan, odom, TF | `ros2 topic echo /robot_ns/scan --once` | `day_11_slam/troubleshooting/slam_day11_troubleshooting.md` |
| AMCL particle이 안 모임 | initialpose, map/world, TF | `ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns` | `day_12_amcl_mcl/troubleshooting/amcl_day12_troubleshooting.md` |
| Nav2 action server가 없음 | launch, namespace, lifecycle | `ros2 action list \| grep navigate` | `day_13_nav2/troubleshooting/nav2_day13_troubleshooting.md` |
| path는 나오는데 로봇이 안 움직임 | controller/DWB/cmd_vel | `ros2 topic echo /robot_ns/cmd_vel` | `11_navigation_debug_deep_dives/02_dwb_local_controller_practical.md` |
| rosbag remap 후에도 TF 오류 | topic 이름과 frame_id 분리 | `ros2 topic echo /robot_ns/scan --once \| grep frame_id` | `11_navigation_debug_deep_dives/01_rosbag_topic_remap_vs_frame_id.md` |

---

## 2. 판단 순서

문제가 생기면 아래 순서로 확인한다.

```bash
ros2 node list | sort
ros2 topic list | sort
ros2 action list | sort
ros2 lifecycle nodes
```

그다음 데이터가 실제로 흐르는지 확인한다.

```bash
ros2 topic echo /robot_ns/scan --once
ros2 topic echo /robot_ns/odom --once
ros2 topic echo /robot_ns/map --once
```

마지막으로 frame과 lifecycle을 확인한다.

```bash
ros2 run tf2_ros tf2_echo odom_robot_ns base_footprint
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns
ros2 lifecycle get /robot_ns/controller_server
```

---

## 3. 바로 고치지 말아야 할 것

아래 항목은 문제 원인이 확정되기 전에는 먼저 바꾸지 않는다.

```text
- AMCL noise parameter
- DWB critic weight
- costmap inflation radius
- planner/controller plugin 이름
- frame 이름
- namespace 구조
```

이 값들은 원인을 찾은 뒤 조정해야 한다. 원인 분리 없이 바꾸면 문제가 사라지는 것이 아니라 더 추적하기 어려워질 수 있다.

---

## 4. 기록할 정보

나중에 다시 분석하려면 최소한 아래 정보를 남긴다.

```text
1. 실행한 launch 명령어
2. 사용한 map/world/bag 이름
3. ros2 node list 결과
4. ros2 topic list 결과
5. 관련 topic echo 결과
6. TF 오류 메시지
7. lifecycle 상태
8. RViz Fixed Frame과 display topic 설정
```
