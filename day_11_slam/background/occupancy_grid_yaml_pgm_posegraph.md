# Background - OccupancyGrid, YAML, PGM, PoseGraph

## 1. OccupancyGrid

ROS2에서 2D 지도는 보통 `nav_msgs/msg/OccupancyGrid`로 표현된다.

```text
2D 공간을 작은 격자 cell로 나누고,
각 cell이 비어 있는지, 막혀 있는지, 아직 모르는지 표시한다.
```

값의 의미:

```text
0    free
100  occupied
-1   unknown
```

---

## 2. resolution

예:

```yaml
resolution: 0.05
```

의미:

```text
지도 이미지의 픽셀 1개가 실제 공간 0.05m를 의미한다.
```

즉, 100픽셀은 다음과 같다.

```text
100 * 0.05m = 5m
```

---

## 3. origin

예:

```yaml
origin: [-4.98, -4.98, 0]
```

의미:

```text
지도 이미지의 원점이 map frame 기준으로 어디에 놓이는지 나타낸다.
```

OccupancyGrid는 단순 이미지가 아니라 실제 좌표계 위에 올라가는 지도이기 때문에 origin이 필요하다.

---

## 4. PGM

`.pgm`은 Portable GrayMap 이미지 파일이다.  
SLAM 지도에서는 occupancy 정보를 흑백 이미지로 저장한 결과라고 보면 된다.

```text
검은색 계열   장애물
흰색 계열     이동 가능 영역
회색 계열     unknown
```

---

## 5. YAML

`.yaml`은 PGM 파일을 ROS map으로 해석하기 위한 메타데이터다.

```yaml
image: slam_map.pgm
mode: trinary
resolution: 0.05
origin: [-4.98, -4.98, 0]
negate: 0
occupied_thresh: 0.65
free_thresh: 0.25
```

YAML만 있어도 안 되고, PGM만 있어도 부족하다.  
둘이 함께 있어야 map_server가 지도를 제대로 로딩할 수 있다.

---

## 6. PoseGraph

PoseGraph는 최종 지도 이미지가 아니라 SLAM 내부 상태에 가깝다.

```text
로봇이 지나간 pose들
pose 사이의 odometry 관계
scan matching 관계
loop closure 관계
```

SLAM Toolbox에서 serialize하면 다음 파일이 생길 수 있다.

```text
slam_map_serial.data
slam_map_serial.posegraph
```

정리:

```text
AMCL/Nav2 지도 사용:
  .yaml + .pgm

SLAM Toolbox 내부 상태 저장/복원:
  .data + .posegraph
```
