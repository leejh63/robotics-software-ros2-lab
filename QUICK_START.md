# Quick Start

이 문서는 저장소를 처음 열었을 때 어디부터 보면 되는지 정리한 빠른 시작 문서입니다.

---

## 1. 이 저장소의 기준

이 저장소는 ROS2 Navigation 실습을 학습 흐름에 맞게 정리한 노트입니다. 핵심은 Gazebo, SLAM, AMCL, Nav2를 `topic`, `frame`, `message`, `action` 기준으로 설명할 수 있게 만드는 것입니다.

```text
목표:
  Gazebo, SLAM, AMCL, Nav2 실습을 topic, frame, message, action 기준으로 다시 설명한다.

범위:
  학습 노트
  실행 흐름 정리
  주요 명령어와 디버깅 기준
  ROS2/Nav2 패키지 활용 구조
```

---

## 2. 10분 안에 전체 구조 보기

```text
README.md
→ MASTER_INDEX.md
→ appendix/learning_flow_one_page.md
→ appendix/full_pipeline_reference.md
→ appendix/table_reference_guide.md
→ appendix/topic_frame_message_action_master_table.md
```

확인할 질문:

```text
1. SLAM은 어떤 데이터를 받아 map을 만드는가?
2. AMCL은 map과 scan을 사용해 무엇을 추정하는가?
3. Nav2는 goal을 받아 어떤 과정을 거쳐 /cmd_vel을 내보내는가?
4. topic 이름과 frame 이름은 어떻게 다른가?
```

---

## 3. 날짜별 학습 흐름

| 순서 | 폴더 | 핵심 |
|---:|---|---|
| 1 | [day_01_05_python_opencv_foundation/](day_01_05_python_opencv_foundation/) | Python, OpenCV, sensor data 기본기 |
| 2 | [day_06_09_ros2_foundation/](day_06_09_ros2_foundation/) | ROS2 node/topic/service/action/launch/TF/rosbag |
| 3 | [day_10_gazebo_urdf/](day_10_gazebo_urdf/) | URDF, Xacro, Gazebo, RViz |
| 4 | [day_11_slam/](day_11_slam/) | SLAM Toolbox와 map 생성 |
| 5 | [day_12_amcl_mcl/](day_12_amcl_mcl/) | AMCL, particle filter, localization |
| 6 | [day_13_nav2/](day_13_nav2/) | Nav2 stack, planner, controller, goal, cmd_vel |
| 7 | [day_14_control_and_path_planning/](day_14_control_and_path_planning/) | PID 제어, ros2_control, Dijkstra/A*/RRT/RRT* |

---

## 4. 실행 코드부터 확인하고 싶을 때

실행 코드와 설정 파일은 `projects/` 아래에 분리되어 있습니다.

### ROS2 Navigation Lab

```bash
cd projects/ros2_navigation_lab
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select lee_robot_description
source install/setup.bash
ros2 launch lee_robot_description nav2.launch.py use_rviz:=false
```

### ROS2 PID Arm Lab

```bash
cd projects/ros2_pid_arm_lab
source /opt/ros/humble/setup.bash
rosdep install --from-paths src -y --ignore-src
colcon build --symlink-install --packages-select pid_arm_lab
source install/setup.bash
ros2 launch pid_arm_lab full.launch.py
```

### Path Planning Algorithms Lab

```bash
cd projects/path_planning_algorithms_lab
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
jupyter notebook notebooks
```

---

## 5. 개념만 빠르게 보기

| 질문 | 문서 |
|---|---|
| TF, topic, namespace, frame_id가 헷갈릴 때 | [10_selected_deep_dives/01_tf_topic_namespace_frame_id.md](10_selected_deep_dives/01_tf_topic_namespace_frame_id.md) |
| LaserScan, odom, TF가 SLAM에 어떻게 들어가는지 볼 때 | [10_selected_deep_dives/02_laserscan_odom_tf_to_slam.md](10_selected_deep_dives/02_laserscan_odom_tf_to_slam.md) |
| SLAM과 AMCL 차이가 헷갈릴 때 | [10_selected_deep_dives/03_slam_vs_amcl.md](10_selected_deep_dives/03_slam_vs_amcl.md) |
| Nav2 goal이 /cmd_vel로 바뀌는 흐름을 볼 때 | [10_selected_deep_dives/05_nav2_goal_to_cmd_vel.md](10_selected_deep_dives/05_nav2_goal_to_cmd_vel.md) |

---

## 6. 명령어 실행 전 확인

```text
appendix/command_execution_conventions.md
appendix/full_command_quick_reference.md
appendix/validation_sequence_gazebo_slam_amcl_nav2.md
```

특히 아래 네 가지를 구분합니다.

```text
package name  예: lee_robot_description
namespace     예: robot_ns
topic name    예: /robot_ns/scan
frame name    예: map_robot_ns
```

---

## 7. 문제가 생겼을 때

```text
appendix/troubleshooting_quick_diagnosis.md
→ appendix/troubleshooting_index.md
→ day별 troubleshooting 문서
→ 11_navigation_debug_deep_dives/
```

대표 확인 순서:

```text
1. node가 떠 있는가?
2. topic이 publish 되는가?
3. message의 header.frame_id가 기대한 frame인가?
4. TF tree가 연결되어 있는가?
5. lifecycle node가 active 상태인가?
6. path는 생기는데 /cmd_vel만 안 나오는가?
7. Behavior Tree의 어느 단계에서 실패하는가?
```
