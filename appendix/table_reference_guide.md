# Topic / Frame / Message / Action Table Reference Guide

이 문서는 appendix 안에 있는 topic/frame/message/action 표들의 역할을 정리한다.

표가 여러 개 있는 이유는 같은 정보를 중복해서 보관하려는 목적이 아니라, 학습 단계별로 필요한 확인 범위가 다르기 때문이다.

---

## 1. 기준표

| 문서 | 역할 | 충돌 시 기준 여부 |
|---|---|---|
| [`topic_frame_message_action_master_table.md`](topic_frame_message_action_master_table.md) | Day 06~13 전체 topic, frame, message, action 기준표 | 기준 |
| [`content_consistency_map.md`](content_consistency_map.md) | 여러 문서가 다르게 보일 때 어떤 문서를 우선할지 판단 | 기준 |

`topic_frame_message_action_master_table.md`가 가장 최신 기준표다. 다른 표와 표현이 다르면 master table을 우선한다.

---

## 2. 보조표

| 문서 | 용도 | 읽는 상황 |
|---|---|---|
| [`topic_frame_table.md`](topic_frame_table.md) | Day 10 Gazebo/URDF 이후의 기본 topic-frame 빠른 참조 | sensor topic, `/cmd_vel`, `/tf`를 처음 정리할 때 |
| [`slam_topic_frame_table.md`](slam_topic_frame_table.md) | Day 11 SLAM 기준 topic/TF 빠른 참조 | SLAM Toolbox 입력/출력과 `map_robot_ns -> odom_robot_ns`를 확인할 때 |
| [`amcl_topic_frame_table.md`](amcl_topic_frame_table.md) | Day 12 AMCL 기준 topic/TF 빠른 참조 | `/initialpose`, `/amcl_pose`, `/particle_cloud` namespace case를 확인할 때 |
| [`nav2_topic_frame_action_table.md`](nav2_topic_frame_action_table.md) | Day 13 Nav2 기준 topic/frame/action 빠른 참조 | planner/controller/action/costmap topic을 확인할 때 |
| [`full_topic_frame_message_action_table.md`](full_topic_frame_message_action_table.md) | 넓은 범위의 확장 표 | Day 01~13 전체를 한 번에 훑을 때 |

보조표는 특정 Day나 특정 기능을 빠르게 보기 위한 표다. 최신 통합 기준은 항상 master table이다.

---

## 3. 표를 읽을 때 헷갈리기 쉬운 규칙

### Topic 이름과 frame 이름은 다르다

```text
/robot_ns/map   = topic name
map_robot_ns    = frame name

/robot_ns/odom  = topic name
odom_robot_ns   = frame name
```

Topic namespace를 바꾼다고 message 내부 `header.frame_id`나 TF frame 이름이 자동으로 바뀌지는 않는다.

### AMCL topic은 namespace case에 따라 달라질 수 있다

```text
/amcl
  -> /initialpose, /amcl_pose, /particle_cloud

/robot_ns/amcl
  -> /robot_ns/initialpose, /robot_ns/amcl_pose, /robot_ns/particle_cloud
```

AMCL topic은 고정 이름으로 외우지 말고 실제 node/topic graph를 먼저 확인한다.

```bash
ros2 node list | sort | grep amcl
ros2 topic list | sort | grep -E 'initialpose|amcl_pose|particle_cloud'
```

상세 설명은 [`amcl_namespace_cases.md`](amcl_namespace_cases.md)를 본다.

### `map_robot_ns` / `odom_robot_ns`는 일반 예제의 `map` / `odom`과 같은 역할이다

이 문서에서는 namespace가 섞이는 상황에서 frame 충돌을 줄이기 위해 아래처럼 표기한다.

```text
map  -> map_robot_ns
odom -> odom_robot_ns
```

상세 설명은 [`../day_12_amcl_mcl/background/map_odom_namespace_frames.md`](../day_12_amcl_mcl/background/map_odom_namespace_frames.md)를 본다.

---

## 4. 충돌이 보이면 적용할 순서

```text
1. 실제 실행 topic/node 이름은 ros2 node/topic/action list로 확인한다.
2. topic, frame, message type, action 이름 중 무엇을 말하는지 분리한다.
3. 전체 기준은 topic_frame_message_action_master_table.md를 본다.
4. 특정 단계의 빠른 확인은 Day별 보조표를 본다.
5. AMCL topic namespace는 amcl_namespace_cases.md를 본다.
6. frame naming 이유는 map_odom_namespace_frames.md를 본다.
```
