# Topic / Frame / Message / Action 표 읽는 법

appendix에는 topic/frame/message/action 표가 여러 개 있다. 같은 내용을 중복하려는 목적이 아니라, 확인 범위가 다르기 때문에 나눠둔 것이다.

---

## 1. 기본 원칙

```text
전체 기준이 필요하면 master table을 본다.
특정 Day만 빠르게 확인할 때는 Day별 보조표를 본다.
문서끼리 표현이 다르면 master table을 우선한다.
```

---

## 2. 표 역할 구분

| 문서 | 역할 | 우선순위 |
|---|---|---:|
| [topic_frame_message_action_master_table.md](topic_frame_message_action_master_table.md) | Day 06~13 전체 기준표 | 1 |
| [content_consistency_map.md](content_consistency_map.md) | 문서 간 기준 충돌 판단 | 1 |
| [full_topic_frame_message_action_table.md](full_topic_frame_message_action_table.md) | Day 01~13 확장 복습표 | 2 |
| [topic_frame_table.md](topic_frame_table.md) | Day 10 Gazebo/URDF 빠른 참조 | 3 |
| [slam_topic_frame_table.md](slam_topic_frame_table.md) | Day 11 SLAM 빠른 참조 | 3 |
| [amcl_topic_frame_table.md](amcl_topic_frame_table.md) | Day 12 AMCL 빠른 참조 | 3 |
| [nav2_topic_frame_action_table.md](nav2_topic_frame_action_table.md) | Day 13 Nav2 빠른 참조 | 3 |

---

## 3. 자주 헷갈리는 구분

### Topic 이름과 frame 이름은 다르다

```text
/robot_ns/map   = topic name
map_robot_ns    = frame name

/robot_ns/odom  = topic name
odom_robot_ns   = frame name
```

Topic namespace를 바꾼다고 message 내부 `header.frame_id`나 TF frame 이름이 자동으로 바뀌지는 않는다.

### AMCL topic은 namespace에 따라 달라질 수 있다

```text
/amcl
  -> /initialpose, /amcl_pose, /particle_cloud

/robot_ns/amcl
  -> /robot_ns/initialpose, /robot_ns/amcl_pose, /robot_ns/particle_cloud
```

AMCL topic은 고정 이름으로 외우지 말고 실제 node/topic graph를 확인한다.

```bash
ros2 node list | sort | grep amcl
ros2 topic list | sort | grep -E 'initialpose|amcl_pose|particle_cloud'
```

상세 설명은 [amcl_namespace_cases.md](amcl_namespace_cases.md)를 본다.

### `map_robot_ns` / `odom_robot_ns`는 일반 예제의 `map` / `odom`과 같은 역할이다

이 문서에서는 namespace가 섞이는 상황에서 frame 충돌을 줄이기 위해 아래처럼 표기한다.

```text
map  -> map_robot_ns
odom -> odom_robot_ns
```

상세 설명은 [../day_12_amcl_mcl/background/map_odom_namespace_frames.md](../day_12_amcl_mcl/background/map_odom_namespace_frames.md)를 본다.

---

## 4. 충돌이 보일 때 확인 순서

```text
1. 실제 실행 결과는 ros2 node/topic/action list로 먼저 확인한다.
2. 지금 말하는 것이 topic, frame, message type, action 중 무엇인지 분리한다.
3. 전체 기준은 topic_frame_message_action_master_table.md를 본다.
4. 특정 Day의 빠른 확인은 Day별 보조표를 본다.
5. AMCL topic namespace는 amcl_namespace_cases.md를 본다.
6. frame naming 이유는 map_odom_namespace_frames.md를 본다.
```
