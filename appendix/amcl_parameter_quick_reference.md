# AMCL 파라미터 빠른 참조

이 문서는 `lee_robot_description/config/amcl_param.yaml`을 볼 때 빠르게 확인하기 위한 참조표다.

---

## 1. 현재 환경 필수값

```yaml
use_sim_time: true
global_frame_id: map_robot_ns
odom_frame_id: odom_robot_ns
base_frame_id: base_footprint
scan_topic: /robot_ns/scan
tf_broadcast: true
laser_min_range: 0.12
laser_max_range: 3.5
laser_model_type: likelihood_field
```

---

## 2. 파라미터 표

| 파라미터 | 의미 | 먼저 볼 상황 |
|---|---|---|
| `use_sim_time` | Gazebo `/clock` 사용 | 시뮬레이션 시간 안 맞을 때 |
| `global_frame_id` | map 기준 frame | RViz Fixed Frame, `/amcl_pose` frame 문제 |
| `odom_frame_id` | odom frame | `map_robot_ns -> odom_robot_ns` TF 문제 |
| `base_frame_id` | 로봇 base frame | TF chain 연결 문제 |
| `scan_topic` | LiDAR topic | AMCL이 scan 못 받을 때 |
| `tf_broadcast` | AMCL이 map->odom TF 발행 여부 | `map_robot_ns -> odom_robot_ns`가 안 나올 때 |
| `transform_tolerance` | TF 시간 허용 | extrapolation 오류 |
| `min_particles` | 최소 particle 수 | CPU/수렴 안정성 |
| `max_particles` | 최대 particle 수 | global localization, CPU 부담 |
| `pf_err` | KLD 허용 오차 | adaptive particle 조절 |
| `pf_z` | KLD 신뢰도 | adaptive particle 조절 |
| `robot_model_type` | 구동 모델 | 차동/전방향 모델 불일치 |
| `alpha1~5` | odom 노이즈 | 실제 움직임과 odom 차이 |
| `laser_model_type` | 센서 모델 | scan-map 비교 방식 |
| `laser_min_range` | LiDAR 최소 거리 | Gazebo sensor range와 맞추기 |
| `laser_max_range` | LiDAR 최대 거리 | Gazebo sensor range와 맞추기 |
| `laser_likelihood_max_dist` | likelihood field 거리 한계 | 벽 근처 점수 범위 |
| `z_hit` | 정상 hit 가중치 | scan이 map과 잘 맞을 때의 신뢰 |
| `z_rand` | random 측정 가중치 | 잡음/무작위 측정 대응 |
| `z_short` | 짧게 측정된 beam 가중치 | 예상보다 가까운 장애물 |
| `z_max` | 최대 거리 beam 가중치 | max range beam 처리 |
| `sigma_hit` | hit 분포 폭 | 장애물 근처 점수 감소 폭 |
| `lambda_short` | short reading 분포 | 예상보다 짧은 거리 측정 |
| `update_min_d` | 위치 update 최소 이동 거리 | update가 너무 잦거나 느릴 때 |
| `update_min_a` | 위치 update 최소 회전 각도 | 회전 후 갱신 문제 |
| `resample_interval` | resampling 주기 | particle 재선택 빈도 |
| `set_initial_pose` | 초기 pose 자동 설정 여부 | RViz initialpose 대신 YAML 초기값 쓸 때 |
| `always_reset_initial_pose` | 재시작 시 초기 pose 리셋 | 반복 실행 시 초기화 정책 |

---

## 3. 튜닝 전 확인 우선순위

```text
1. world-map 짝
2. topic 이름
3. frame 이름
4. lifecycle active
5. initialpose
6. TF remap
7. RViz display 설정
8. 그 다음 파라미터 튜닝
```

초기 문제의 대부분은 `alpha`나 `z_hit` 튜닝 문제가 아니라 topic/frame/lifecycle/initialpose 문제다.
