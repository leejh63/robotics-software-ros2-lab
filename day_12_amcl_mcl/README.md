# Day 12 AMCL / MCL 학습 정리

Day 12의 목적은 Day 11에서 만든 지도를 다시 불러와서, 로봇이 그 지도 위에서 **현재 어디에 있는지 추정하는 흐름**을 이해하는 것이다.

핵심은 아래 한 줄이다.

```text
Day 11 SLAM: 로봇이 움직이면서 지도를 만든다.
Day 12 AMCL: 이미 만든 지도 위에서 현재 로봇 위치를 추정한다.
```

이 문서는 AMCL 실습을 다시 볼 때 아래 질문에 답할 수 있도록 정리한 학습 노트이다.

```text
AMCL은 어떤 입력을 필요로 하는가?
AMCL은 어떤 출력을 만드는가?
particle은 무엇인가?
/initialpose는 왜 필요한가?
/amcl_pose와 map_lee -> odom_lee TF는 무엇이 다른가?
amcl_param.yaml의 값들은 MCL의 어느 단계와 연결되는가?
예시 환경에서 어떤 명령어로 확인해야 하는가?
```

---

## 1. 현재 예시 환경 기준

```text
워크스페이스       projects/ros2_navigation_lab
패키지             lee_robot_description
분리 실행 런치      lee_robot_description/launch/gazebo.launch.py
통합 실행 런치      lee_robot_description/launch/localization.launch.py
AMCL 파라미터      lee_robot_description/config/amcl_param.yaml
RViz 설정          lee_robot_description/rviz/amcl.rviz
기본 world         lee_robot_description/worlds/slam.world
기본 map           lee_robot_description/maps/slam_map.yaml
작은 방 world      lee_robot_description/worlds/lee_world.world
작은 방 map        lee_robot_description/maps/room_map.yaml
map topic          /lee/map
scan topic         /lee/scan
cmd_vel topic      /lee/cmd_vel
TF topic           /lee/tf, /lee/tf_static
map frame          map_lee
odom frame         odom_lee
base frame         base_footprint
LiDAR frame        base_scan
```

일반 예제와 가장 많이 다른 부분은 namespace와 frame 이름이다.

```text
/map      -> /lee/map
/scan     -> /lee/scan
/cmd_vel  -> /lee/cmd_vel
/tf       -> /lee/tf
/tf_static -> /lee/tf_static
map       -> map_lee
odom      -> odom_lee
base_link -> base_footprint
```

여기서 `map_lee`, `odom_lee`는 일반 예제의 `map`, `odom`과 역할은 같지만, 현재 robot namespace와 맞춰 둔 frame 이름이다. 자세한 설명은 [`background/map_odom_namespace_frames.md`](background/map_odom_namespace_frames.md)를 참고한다.

---

## 2. 읽는 순서

```text
00_source_overview.md
  실제 사용한 Day 12 파일, launch, config, 노트북, 명령어 문서 위치

01_overview_flow.md
  Day 11 SLAM 결과물이 Day 12 AMCL 입력으로 이어지는 전체 흐름

02_mcl_particle_filter_concepts.md
  MCL, particle, motion update, sensor update, resampling 개념

03_amcl_data_flow_and_tf.md
  map_server, AMCL, /initialpose, /amcl_pose, /particle_cloud, map_lee -> odom_lee TF 관계

04_amcl_parameters_and_tuning.md
  amcl_param.yaml 주요 파라미터를 MCL 단계별로 해석

05_execution_split_and_integrated_launch.md
  분리 실행과 localization.launch.py 통합 실행의 차이

06_rviz_initialpose_and_validation.md
  RViz 설정, 2D Pose Estimate, 수렴 확인 기준

07_execution_notes.md
  예시 환경 기준 실행 순서와 주의점

08_runtime_notes.md
  실행 중 헷갈리기 쉬운 관찰 사항과 확인 기준

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
  일반 예제의 map/odom과 현재 문서의 map_lee/odom_lee 차이
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
