# Quick Start

이 문서는 GitHub에서 저장소를 처음 열었을 때 어디부터 보면 되는지 정리한 빠른 시작 문서다.

---

## 1. 이 저장소를 보는 기준

이 저장소는 완성 프로젝트가 아니라 ROS2 Navigation 학습 노트다.

```text
목표:
  Gazebo, SLAM, AMCL, Nav2 실습을 topic, frame, message, action 기준으로 다시 설명할 수 있게 정리한다.

아닌 것:
  완성형 자율주행 프로젝트
  실제 로봇 배포용 패키지
  공식 Nav2 튜토리얼 대체 문서
```

---

## 2. 10분 안에 전체 구조만 보기

아래 순서만 보면 저장소의 큰 흐름을 잡을 수 있다.

```text
README.md
→ MASTER_INDEX.md
→ appendix/learning_flow_one_page.md
→ appendix/full_pipeline_reference.md
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

## 3. 하루치 학습 흐름대로 보기

날짜별 문서는 실습 흐름을 따라가기 좋다.

| 순서 | 폴더 | 핵심 |
|---:|---|---|
| 1 | [day_01_05_python_opencv_foundation/](day_01_05_python_opencv_foundation/) | Python, OpenCV, sensor data 기본기 |
| 2 | [day_06_09_ros2_foundation/](day_06_09_ros2_foundation/) | ROS2 node/topic/service/action/launch/TF/rosbag |
| 3 | [day_10_gazebo_urdf/](day_10_gazebo_urdf/) | URDF, Xacro, Gazebo, RViz |
| 4 | [day_11_slam/](day_11_slam/) | SLAM Toolbox와 map 생성 |
| 5 | [day_12_amcl_mcl/](day_12_amcl_mcl/) | AMCL, particle filter, localization |
| 6 | [day_13_nav2/](day_13_nav2/) | Nav2 stack, planner, controller, goal, cmd_vel |

---

## 4. 개념만 빠르게 정리하기

개념이 헷갈릴 때는 날짜별 문서보다 아래 문서를 먼저 본다.

| 질문 | 문서 |
|---|---|
| TF, topic, namespace, frame_id가 헷갈릴 때 | [10_selected_deep_dives/01_tf_topic_namespace_frame_id.md](10_selected_deep_dives/01_tf_topic_namespace_frame_id.md) |
| LaserScan, odom, TF가 SLAM에 어떻게 들어가는지 볼 때 | [10_selected_deep_dives/02_laserscan_odom_tf_to_slam.md](10_selected_deep_dives/02_laserscan_odom_tf_to_slam.md) |
| SLAM과 AMCL 차이가 헷갈릴 때 | [10_selected_deep_dives/03_slam_vs_amcl.md](10_selected_deep_dives/03_slam_vs_amcl.md) |
| Nav2 goal이 /cmd_vel로 바뀌는 흐름을 볼 때 | [10_selected_deep_dives/05_nav2_goal_to_cmd_vel.md](10_selected_deep_dives/05_nav2_goal_to_cmd_vel.md) |

---

## 5. 명령어를 실행하기 전에 보기

명령어 문서는 placeholder를 포함한다. 그대로 복사하기 전에 아래 문서를 먼저 확인한다.

```text
appendix/command_execution_conventions.md
appendix/full_command_quick_reference.md
appendix/validation_sequence_gazebo_slam_amcl_nav2.md
```

특히 아래 네 가지를 구분한다.

```text
package name  예: lee_robot_description
namespace     예: robot_ns
topic name    예: /robot_ns/scan
frame name    예: map_robot_ns
```

---

## 6. 문제가 생겼을 때 보기

문제가 발생하면 바로 긴 문서로 들어가지 말고 빠른 진단표를 먼저 본다.

```text
appendix/troubleshooting_quick_diagnosis.md
→ appendix/troubleshooting_index.md
→ day별 troubleshooting 문서
→ 11_navigation_debug_deep_dives/
```

대표적으로 확인할 순서는 다음이다.

```text
1. node가 떠 있는가?
2. topic이 publish 되는가?
3. message의 header.frame_id가 기대한 frame인가?
4. TF tree가 연결되어 있는가?
5. lifecycle node가 active 상태인가?
6. path는 생기는데 /cmd_vel만 안 나오는가?
7. Behavior Tree의 어느 단계에서 실패하는가?
```

---

## 7. GitHub 업로드 전 보기

업로드 전에는 아래 세 문서를 확인한다.

```text
GITHUB_UPLOAD_GUIDE.md
FINAL_UPLOAD_AUDIT.md
MODIFICATION_LOG.md
```

최소 확인 항목:

```text
[ ] build/, install/, log/, rosbag DB 파일이 포함되지 않았는가?
[ ] 실제 사용자명, IP, hostname, 홈 경로가 남아 있지 않은가?
[ ] README.md와 MASTER_INDEX.md 링크가 깨지지 않는가?
[ ] 이 저장소가 학습 노트라는 점이 README 상단에서 바로 보이는가?
```
