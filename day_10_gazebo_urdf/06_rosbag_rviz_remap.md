# 06. rosbag2 / RViz2 / remap 정리

## 1. Day 10에서 rosbag을 본 이유

Day 10의 중심은 Gazebo/URDF지만, rosbag2와 RViz2도 같이 다뤘다. 이유는 이후 SLAM/AMCL/Nav2에서 같은 센서 데이터를 반복 재생하며 디버깅해야 하기 때문이다.

```text
센서 topic 기록
        ↓
같은 데이터를 반복 재생
        ↓
RViz2 / SLAM / AMCL / Nav2 설정 검증
```

rosbag은 단순 녹화 파일이 아니라 **재현 가능한 실험 입력**이다.

---

## 2. 기본 흐름

```text
ros2 bag record
        ↓
bag 폴더 생성
        ↓
ros2 bag info로 포함 topic 확인
        ↓
ros2 bag play로 재생
        ↓
RViz2나 SLAM 노드가 topic 구독
```

---

## 3. remap이 필요한 경우

bag 안의 topic 이름과 현재 실습에서 사용하는 topic 이름이 다를 수 있다.

예를 들어 bag에는 `/scan`이 있는데, 현재 RViz 설정이나 노드는 `/user_ns/scan`을 기대할 수 있다.

```text
/scan -> /user_ns/scan
/odom -> /user_ns/odom
/imu  -> /user_ns/imu
```

이럴 때 `ros2 bag play`에 remap을 붙인다.

---

## 4. 여러 remap 작성 방식

환경에 따라 `--remap`을 여러 번 붙였을 때 마지막 규칙만 적용되는 것처럼 보였던 기록이 있다. 학습 문서에서는 아래처럼 한 번의 `--remap` 뒤에 여러 규칙을 나열하는 방식을 권장한다.

```bash
ros2 bag play "$BAG_DIR" --loop -r 0.1 --clock \
  --remap \
  /image_raw/compressed:=/user_ns/image_raw/compressed \
  /odom:=/user_ns/odom \
  /imu:=/user_ns/imu \
  /cmd_vel:=/user_ns/cmd_vel \
  /scan:=/user_ns/scan
```

---

## 5. /tf와 /tf_static remap은 신중하게

일반 topic은 namespace로 바꿔도 비교적 단순하다. 하지만 TF는 여러 도구가 기본 `/tf`, `/tf_static`을 전제로 동작하는 경우가 많다.

가능한 선택지는 두 가지다.

### 선택 A: TF는 기본 이름 유지

```text
/scan, /odom 등만 remap
/tf, /tf_static은 그대로 둠
```

장점:

```text
RViz2, tf2_tools, SLAM/AMCL/Nav2 기본 설정과 맞추기 쉽다.
```

### 선택 B: TF도 namespace로 remap

```text
/tf -> /lee/tf
/tf_static -> /lee/tf_static
```

이 경우 모든 관련 도구도 같은 remap을 받아야 한다.

```bash
rviz2 --ros-args \
  -p use_sim_time:=true \
  --remap /tf:=/lee/tf \
  --remap /tf_static:=/lee/tf_static
```

---

## 6. RViz2가 실제로 보는 것

RViz2는 Gazebo나 bag 파일을 직접 보는 것이 아니다. ROS2 topic을 구독해서 그린다.

| RViz Display | 필요한 데이터 |
|---|---|
| RobotModel | `robot_description`, TF |
| TF | `/tf`, `/tf_static` 또는 remap된 TF topic |
| LaserScan | `/scan`, `/lee/scan`, `/user_ns/scan` 등 |
| Odometry | `/odom`, `/lee/odom` 등 |
| Image | `/image_raw`, compressed image republish 결과 등 |

---

## 7. QoS 문제

LaserScan 같은 센서 topic은 `best_effort` QoS를 쓰는 경우가 많다. 그래서 기본 `ros2 topic echo`로 안 보일 수 있다.

확인:

```bash
ros2 topic echo /lee/scan --qos-reliability best_effort --once
ros2 topic hz /lee/scan --qos-reliability best_effort
```

RViz2에서도 LaserScan display의 Reliability Policy를 `Best Effort`로 바꿔야 보일 수 있다.

---

## 8. compressed image 확인

bag에 `/image_raw/compressed`만 있으면 RViz2 Image display에서 바로 보기 애매할 수 있다. 이때 `image_transport republish`를 쓴다.

```bash
ros2 run image_transport republish compressed raw \
  --ros-args \
  --remap in/compressed:=/user_ns/image_raw/compressed \
  --remap out:=/user_ns/image_raw
```

그 다음 RViz2에서는 `/user_ns/image_raw`를 보면 된다.

---

## 9. 핵심 결론

```text
rosbag2는 같은 센서 입력을 반복 재생해 디버깅과 학습을 가능하게 한다.
RViz2는 topic과 TF를 시각화한다.
remap은 topic 이름을 맞추는 도구지만, TF와 use_sim_time은 특히 신중하게 맞춰야 한다.
```
