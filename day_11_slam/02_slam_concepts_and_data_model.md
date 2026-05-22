# 02. SLAM 개념과 데이터 모델

## 1. SLAM이란?

SLAM은 `Simultaneous Localization And Mapping`의 약자다.

```text
Localization
  로봇이 지금 어디 있는지 추정하는 것

Mapping
  주변 환경 지도를 만드는 것

SLAM
  위치 추정과 지도 생성을 동시에 하는 것
```

문제는 두 작업이 서로를 필요로 한다는 점이다.

```text
지도가 있어야 위치를 알기 쉽다.
그런데 위치를 알아야 지도를 그릴 수 있다.
```

그래서 SLAM은 매 순간 아래 과정을 반복한다.

```text
1. 오도메트리로 대략 이동량 예측
2. LiDAR scan으로 주변 벽 모양 관찰
3. 이전 지도/스캔과 현재 scan을 비교
4. 로봇 위치를 보정
5. 보정된 위치 기준으로 지도 업데이트
```

---

## 2. 이번 실습에서 쓰는 SLAM 입력

현재 실습에서 SLAM Toolbox가 보는 핵심 입력은 다음이다.

| 입력 | 현재 값 | 메시지/데이터 | 의미 |
|---|---|---|---|
| LiDAR | `/robot_ns/scan` | `sensor_msgs/msg/LaserScan` | 주변 장애물까지 거리 |
| Odometry | `/robot_ns/odom` | `nav_msgs/msg/Odometry` | 바퀴 기준 이동 추정 |
| TF | `/robot_ns/tf`, `/robot_ns/tf_static` | `tf2_msgs/msg/TFMessage` | 좌표계 연결 관계 |
| Parameter | `slam_param.yaml` | YAML | frame 이름, scan topic, map 설정 |

정확히는 SLAM Toolbox가 `/robot_ns/odom` topic을 직접 설정값으로 구독한다기보다, TF tree에서 `odom_frame`, `base_frame`, `scan frame` 관계를 찾는다.  
그래서 `/robot_ns/odom` 메시지가 나온다고 끝이 아니라, `odom_robot_ns -> base_footprint` TF가 실제로 연결되어야 한다.

---

## 3. LaserScan 데이터

`/robot_ns/scan`의 타입은 다음이다.

```text
sensor_msgs/msg/LaserScan
```

주요 필드:

```text
header.frame_id
  이 scan이 어느 센서 좌표계에서 나온 값인지 표시
  현재는 base_scan이어야 함

angle_min
  ranges[0]이 의미하는 시작 각도

angle_increment
  ranges[i]에서 i가 1 증가할 때 각도가 얼마나 변하는지

ranges
  각도별 거리 배열

range_min / range_max
  유효 측정 거리 범위
```

SLAM에서 중요한 점은 `ranges` 값만 보는 것이 아니라, `header.frame_id`를 통해 이 scan이 로봇 어디에서 나온 값인지 알아야 한다는 점이다.

```text
base_footprint
  -> base_link
    -> base_scan
```

이 TF가 없으면 scan을 지도 좌표계에 제대로 배치할 수 없다.

---

## 4. OccupancyGrid 지도

SLAM Toolbox가 발행하는 `/robot_ns/map`은 다음 타입이다.

```text
nav_msgs/msg/OccupancyGrid
```

OccupancyGrid는 2D 격자 지도다.

```text
0    이동 가능한 공간
100  벽 또는 장애물
-1   아직 모르는 공간
```

RViz2에서 보통 이렇게 보인다.

```text
흰색  free
검은색 occupied
회색  unknown
```

지도 해상도는 `slam_param.yaml`의 `resolution`과 저장된 map yaml의 `resolution`으로 확인한다.

현재 기준:

```text
resolution: 0.05
```

의미:

```text
격자 한 칸 = 0.05m = 5cm
```

---

## 5. map yaml과 pgm

`map_saver_cli`로 지도를 저장하면 보통 두 파일이 생긴다.

```text
slam_map.yaml
slam_map.pgm
```

### 5.1 yaml

예시:

```yaml
image: slam_map.pgm
mode: trinary
resolution: 0.05
origin: [-4.98, -4.98, 0]
negate: 0
occupied_thresh: 0.65
free_thresh: 0.25
```

의미:

| 항목 | 의미 |
|---|---|
| `image` | 실제 지도 이미지 파일 이름 |
| `resolution` | 픽셀 하나가 실제 몇 m인지 |
| `origin` | 지도 이미지의 원점이 map frame에서 어디인지 |
| `occupied_thresh` | 이 값 이상이면 occupied로 판단 |
| `free_thresh` | 이 값 이하이면 free로 판단 |

### 5.2 pgm

`.pgm`은 지도 이미지를 담는 파일이다.  
사람 눈에는 흑백 이미지처럼 보이지만, ROS에서는 occupancy grid를 파일로 저장한 결과라고 보면 된다.

---

## 6. Scan Matching

Scan Matching은 현재 LiDAR scan을 이전 scan 또는 지도와 맞춰보는 과정이다.

직관:

```text
오도메트리 기준으로는 로봇이 A 위치에 있다고 생각했다.
그런데 LiDAR로 본 벽 모양을 지도에 맞춰보니 B 위치가 더 자연스럽다.
그러면 SLAM은 로봇 위치를 B 쪽으로 조금 보정한다.
```

이 기능 때문에 단순 오도메트리보다 위치 누적 오차가 줄어든다.

현재 설정:

```yaml
use_scan_matching: true
```

---

## 7. Loop Closure

Loop Closure는 로봇이 이전에 지나갔던 장소에 다시 왔다는 것을 알아차리는 것이다.

예:

```text
시작점 근처를 떠남
  -> 복도/방을 돌아다님
  -> 다시 시작점 근처로 돌아옴
  -> 예전 scan 모양과 현재 scan 모양이 비슷함
  -> SLAM이 “여기가 같은 장소구나”라고 판단
  -> 전체 지도 오차를 다시 조정
```

현재 설정:

```yaml
do_loop_closing: true
```

지도 품질을 좋게 하려면 로봇을 한 방향으로만 보내지 말고, 일부러 이미 지나간 곳으로 다시 돌아오는 주행이 필요하다.

---

## 8. Pose Graph

Pose Graph는 SLAM 내부에서 로봇의 이동 경로와 관계를 그래프로 저장한 것이다.

```text
pose_0 -- pose_1 -- pose_2 -- pose_3
```

각 pose는 특정 시점의 로봇 위치다.  
각 edge는 pose 사이의 관계다.

```text
Odometry edge
  바퀴 기준으로 이만큼 움직였다는 관계

Scan matching edge
  scan을 맞춰보니 이 위치 관계가 자연스럽다는 정보

Loop closure edge
  예전 위치와 현재 위치가 같은 장소라는 정보
```

Loop closure가 생기면 이런 식의 추가 연결이 생긴다.

```text
pose_0 -- pose_1 -- pose_2 -- pose_3
   |___________________________|
          loop closure
```

SLAM back-end는 이 그래프 전체의 오차가 작아지도록 pose들을 다시 조정한다.

---

## 9. `.posegraph`와 `.data`는 map 파일과 다르다

`slam_map.pgm`과 `slam_map.yaml`은 Nav2나 map_server가 쓰기 좋은 **최종 지도 파일**이다.

반면 SLAM Toolbox의 serialize 결과는 다음처럼 나온다.

```text
slam_map_serial.data
slam_map_serial.posegraph
```

이건 단순 지도 이미지가 아니라 SLAM Toolbox가 다시 로드해서 이어서 mapping하거나 내부 pose graph 상태를 복원할 때 쓰는 파일에 가깝다.

정리:

```text
Nav2/AMCL에서 지도 로딩
  -> slam_map.yaml + slam_map.pgm

SLAM Toolbox 내부 상태 저장/복원
  -> .data + .posegraph
```

---

## 10. 초보자 기준 핵심 정리

```text
SLAM = 위치 추정 + 지도 생성을 동시에 하는 문제
/robot_ns/scan = 벽까지의 거리 배열
/robot_ns/tf = scan과 로봇 좌표계를 연결하는 정보
/robot_ns/map = SLAM 결과 지도
map_robot_ns -> odom_robot_ns = SLAM이 오도메트리 오차를 보정하는 transform
OccupancyGrid = 격자 지도
map_saver_cli = /robot_ns/map을 .pgm + .yaml로 저장하는 도구
posegraph = SLAM 내부에서 로봇 경로와 제약조건을 저장한 그래프
```
