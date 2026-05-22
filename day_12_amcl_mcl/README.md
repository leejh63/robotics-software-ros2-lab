# Day 12 AMCL / MCL 학습 정리

Day 12의 목적은 Day 11에서 만든 지도를 다시 불러와서, 로봇이 그 지도 위에서 **현재 어디에 있는지 추정하는 흐름**을 이해하는 것이다.

핵심은 아래 한 줄이다.

```text
Day 11 SLAM: 로봇이 움직이면서 지도를 만든다.
Day 12 AMCL: 이미 만든 지도 위에서 현재 로봇 위치를 추정한다.
```

이 문서는 포트폴리오용 설명이 아니라 학습 정리본이다. 따라서 “무엇을 완성했다”보다 아래 질문에 답하는 데 집중한다.

```text
AMCL은 어떤 입력을 필요로 하는가?
AMCL은 어떤 출력을 만드는가?
particle은 무엇인가?
/initialpose는 왜 필요한가?
/amcl_pose와 map_robot_ns -> odom_robot_ns TF는 무엇이 다른가?
amcl_param.yaml의 값들은 MCL의 어느 단계와 연결되는가?
내 환경에서 어떤 명령어로 확인해야 하는가?
```

---

## 1. 현재 내 환경 기준

```text
워크스페이스       $ROS2_WS
패키지             lee_robot_description
분리 실행 런치      lee_robot_description/launch/amcl.launch.py
통합 실행 런치      lee_robot_description/launch/amcl_full.launch.py
AMCL 파라미터      lee_robot_description/config/amcl_param.yaml
RViz 설정          lee_robot_description/rviz/amcl.rviz
기본 world         lee_robot_description/worlds/slam.world
기본 map           $ROS2_WS/slam_map.yaml
작은 방 world      lee_robot_description/worlds/robot_ns_world.world
작은 방 map        $ROS2_WS/room_map.yaml
map topic          /robot_ns/map
scan topic         /robot_ns/scan
cmd_vel topic      /robot_ns/cmd_vel
TF topic           /robot_ns/tf, /robot_ns/tf_static
map frame          map_robot_ns
odom frame         odom_robot_ns
base frame         base_footprint
LiDAR frame        base_scan
```

일반 예제와 가장 많이 다른 부분은 namespace와 frame 이름이다.

```text
/map      -> /robot_ns/map
/scan     -> /robot_ns/scan
/cmd_vel  -> /robot_ns/cmd_vel
/tf       -> /robot_ns/tf
/tf_static -> /robot_ns/tf_static
map       -> map_robot_ns
odom      -> odom_robot_ns
base_link -> base_footprint
```

여기서 `map_robot_ns`, `odom_robot_ns`는 일반 예제의 `map`, `odom`과 역할은 같지만, 여러 robot namespace나 rosbag replay 상황에서 TF frame 충돌을 줄이기 위해 더 구체적으로 붙인 이름이다. 자세한 설명은 [`background/map_odom_namespace_frames.md`](background/map_odom_namespace_frames.md)를 참고한다.

---

## 2. 읽는 순서

```text
00_source_file_map.md
  실제 사용한 Day 12 파일, launch, config, 노트북, 명령어 문서 위치

01_overview_flow.md
  Day 11 SLAM 결과물이 Day 12 AMCL 입력으로 이어지는 전체 흐름

02_mcl_particle_filter_concepts.md
  MCL, particle, motion update, sensor update, resampling 개념

03_amcl_data_flow_and_tf.md
  map_server, AMCL, /initialpose, /amcl_pose, /particle_cloud, map_robot_ns -> odom_robot_ns TF 관계

04_amcl_parameters_and_tuning.md
  amcl_param.yaml 주요 파라미터를 MCL 단계별로 해석

05_execution_split_and_integrated_launch.md
  분리 실행과 amcl_full.launch.py 통합 실행의 차이

06_rviz_initialpose_and_validation.md
  RViz 설정, 2D Pose Estimate, 수렴 확인 기준

07_my_environment_execution_notes.md
  내 환경 기준 실행 순서와 주의점

08_runtime_observations_without_code_changes.md
  코드 수정 없이 기록해둔 실행상 관찰/주의사항

09_day12_review_questions.md
  Day 12 복습 질문
```

---

## 3. 이 단계에서 새로 보강한 배경지식

```text
background/particle_filter_math_minimum.md
  파티클 필터의 확률적 의미를 최소 수식으로 정리

background/likelihood_field_vs_beam_model.md
  AMCL 센서 모델인 beam model과 likelihood field model 차이

background/initial_pose_covariance_and_convergence.md
  initialpose, covariance, particle 수렴의 관계

background/lifecycle_map_server_amcl.md
  map_server와 amcl이 lifecycle node인 이유

background/map_odom_namespace_frames.md
  일반 예제의 map/odom과 현재 문서의 map_robot_ns/odom_robot_ns 차이
```

---

## 4. Day 12에서 반드시 구분해야 하는 것

### SLAM과 AMCL

```text
SLAM
  지도 생성과 위치 추정을 동시에 한다.
  Day 11의 핵심이다.

AMCL
  이미 만들어진 지도를 입력으로 받아 위치만 추정한다.
  Day 12의 핵심이다.
```

### /amcl_pose와 TF

```text
/amcl_pose
  사람이 확인하기 좋은 위치 추정 결과 토픽이다.

map_robot_ns -> odom_robot_ns TF
  RViz, Nav2, costmap이 실제로 좌표계를 이어서 쓰는 핵심 변환이다.
```

따라서 `/amcl_pose`가 한 번 보이는 것보다 아래 TF chain이 이어지는지가 더 중요하다.

```text
map_robot_ns -> odom_robot_ns -> base_footprint -> base_scan
```

### topic remap과 frame_id

```text
-r /map:=/robot_ns/map
```

이런 remap은 topic 이름만 바꾼다. 메시지 안의 `header.frame_id`나 TF frame 이름은 자동으로 바뀌지 않는다. 그래서 AMCL 파라미터의 `global_frame_id`, `odom_frame_id`, `base_frame_id`도 별도로 맞아야 한다.

---

## 5. 코드 수정 여부

이번 문서 정리에서도 코드 수정은 하지 않았다.

```text
코드 수정 없음
패키지 구조 변경 없음
런치 파일 변경 없음
파라미터 파일 변경 없음
문서 정리, 배경지식 보강, 내 환경 기준 실행 메모 추가만 진행
```
