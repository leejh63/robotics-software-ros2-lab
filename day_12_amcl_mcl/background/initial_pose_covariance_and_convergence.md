# Initial Pose, Covariance, Particle 수렴

AMCL을 처음 보면 `/initialpose`를 왜 줘야 하는지, covariance가 무엇인지 헷갈리기 쉽다.

---

## 1. initialpose의 의미

`/initialpose`는 AMCL에게 주는 초기 힌트다.

```text
로봇은 지도 위 이 위치와 이 방향 근처에 있을 가능성이 높다.
```

AMCL은 이 힌트를 기준으로 particle들을 주변에 뿌린다.

```text
initialpose가 정확함
  particle이 처음부터 실제 위치 근처에 생김
  빠르게 수렴 가능

initialpose가 많이 틀림
  particle이 엉뚱한 곳에서 시작
  수렴 실패 가능
```

---

## 2. covariance의 의미

covariance는 “이 초기 위치를 얼마나 확신하는지”를 나타낸다.

```text
covariance 작음
  나는 이 위치를 꽤 확신한다.
  particle이 좁게 퍼진다.

covariance 큼
  이 위치 근처라고만 대충 안다.
  particle이 넓게 퍼진다.
```

RViz의 2D Pose Estimate는 적절한 covariance를 포함해서 메시지를 발행한다.

CLI로 직접 `/initialpose`를 보낼 때는 covariance도 넣어줘야 한다.

---

## 3. 수렴이란 무엇인가

수렴은 particle들이 실제 위치 주변으로 모이는 현상이다.

```text
초기:
  particle이 넓게 퍼져 있음

scan/map 비교 후:
  그럴듯한 위치의 particle이 살아남음

이동과 관측 반복:
  particle이 실제 위치 주변으로 모임
```

RViz에서는 `/particle_cloud`로 확인한다.

---

## 4. 수렴이 잘 안 되는 경우

```text
1. initialpose 위치가 너무 틀림
2. initialpose 방향이 크게 틀림
3. world와 map이 다른 짝임
4. scan frame과 TF가 맞지 않음
5. odom이 비정상임
6. map 품질이 나쁨
7. 대칭적인 환경이라 여러 위치가 비슷하게 보임
```

특히 방향이 중요하다.

```text
같은 위치라도 로봇이 바라보는 방향이 틀리면 LiDAR scan 모양이 달라진다.
```

---

## 5. particle이 많이 퍼졌다고 항상 나쁜 것은 아니다

초기에는 퍼지는 것이 정상이다. 위치가 불확실하기 때문이다.

문제는 시간이 지나도 계속 수렴하지 않는 경우다.

```text
정상 가능성:
  initialpose 직후 잠깐 퍼짐
  이동하면서 점점 모임

문제 가능성:
  계속 전체 지도에 퍼짐
  엉뚱한 벽 주변으로 모임
  로봇 이동과 함께 particle이 튐
```

---

## 6. 현재 환경에서의 확인 순서

```bash
ros2 topic echo /initialpose --once
ros2 topic echo /particle_cloud --once
ros2 topic echo /amcl_pose --once
```

TF 확인:

```bash
ros2 run tf2_ros tf2_echo map_robot_ns odom_robot_ns \
  --ros-args \
  -r /tf:=/robot_ns/tf \
  -r /tf_static:=/robot_ns/tf_static
```

RViz 확인:

```text
Fixed Frame: map_robot_ns
Map: /robot_ns/map
LaserScan: /robot_ns/scan
ParticleCloud: /particle_cloud
```
