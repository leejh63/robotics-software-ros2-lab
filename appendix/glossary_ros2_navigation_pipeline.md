# ROS2 Navigation Pipeline 용어집

Day 01~13 정리본에서 반복적으로 등장하는 용어를 간단히 정리한 문서다.

---

## 1. ROS2 기본 용어

| 용어 | 뜻 |
|---|---|
| workspace | ROS2 패키지들을 모아 빌드하는 작업 공간 |
| package | ROS2 기능 단위 묶음. 코드, launch, config, msg 등을 포함 |
| executable | 실행 가능한 프로그램 단위. `ros2 run 패키지 실행파일`에서 실행되는 대상 |
| node | ROS graph에 참여하는 실행 주체 |
| topic | 지속적으로 흘러가는 메시지 통로 |
| service | 요청/응답 구조의 통신 |
| action | 오래 걸리는 목표 작업을 feedback/result와 함께 처리하는 통신 |
| interface | message, service, action 타입 정의 |
| message | topic으로 전달되는 데이터 구조 |
| launch | 여러 node와 설정을 한 번에 실행하는 파일 |
| parameter | node 동작을 바꾸는 설정값 |
| namespace | topic/node/action 이름 앞에 붙는 이름 공간 |
| remap | topic/action/service 이름을 실행 시점에 바꾸는 기능 |
| QoS | ROS2 통신 품질 설정. reliability, durability, depth 등을 포함 |
| executor | callback을 실제로 실행하는 ROS2 실행 구조 |
| callback | topic/service/timer/action 이벤트가 왔을 때 실행되는 함수 |

---

## 2. TF / 좌표계 용어

| 용어 | 뜻 |
|---|---|
| frame | 좌표계 이름 |
| TF | frame 사이의 위치/자세 관계 |
| transform | 부모 frame에서 자식 frame으로의 위치/회전 변환 |
| static TF | 시간이 지나도 변하지 않는 좌표계 관계 |
| dynamic TF | 시간에 따라 변하는 좌표계 관계 |
| `map_robot_ns` | 지도 기준 전역 frame |
| `odom_robot_ns` | odometry 기준 지역 frame |
| `base_footprint` | 로봇 바닥 중심 frame |
| `base_link` | 로봇 본체 frame |
| `base_scan` | LiDAR 센서 frame |
| `camera_link` | 카메라 센서 frame |
| frame_id | 메시지 데이터가 어느 좌표계 기준인지 나타내는 header 필드 |
| child_frame_id | Odometry/TF 등에서 자식 좌표계를 나타내는 필드 |

---

## 3. Gazebo / URDF 용어

| 용어 | 뜻 |
|---|---|
| URDF | 로봇 link/joint/sensor 구조를 XML로 표현하는 형식 |
| XACRO | URDF를 macro/변수로 더 편하게 작성하는 방식 |
| SDF | Gazebo에서 사용하는 simulation description 형식 |
| link | 로봇의 물리적 부품 단위 |
| joint | link 사이의 연결 관계 |
| visual | RViz/Gazebo에서 보이는 형상 |
| collision | 물리 충돌 계산에 쓰는 형상 |
| inertial | 질량/관성 정보 |
| Gazebo plugin | Gazebo와 ROS2 topic/control을 연결하는 플러그인 |
| diff_drive plugin | `/cmd_vel`을 받아 바퀴 구동/odometry를 만드는 plugin |
| robot_state_publisher | URDF joint/link 정보를 바탕으로 TF를 발행하는 node |
| spawn_entity.py | Gazebo world 안에 robot model을 생성하는 도구 |

---

## 4. Sensor / Vision 용어

| 용어 | 뜻 |
|---|---|
| LaserScan | 2D LiDAR 거리 배열 메시지 |
| ranges | LaserScan 안의 거리값 배열 |
| angle_min | ranges[0]이 가리키는 시작 각도 |
| angle_increment | 인접한 range 사이의 각도 간격 |
| Image | ROS2 이미지 메시지 |
| cv_bridge | ROS Image와 OpenCV image를 변환하는 도구 |
| bbox | object detection bounding box |
| confidence | detection 결과의 신뢰도 |
| class id | detection된 객체 종류 id |
| Kalman filter | 예측과 보정을 반복하는 상태 추정 필터 |

---

## 5. SLAM / Mapping 용어

| 용어 | 뜻 |
|---|---|
| SLAM | 위치 추정과 지도 생성을 동시에 수행하는 기술 |
| scan matching | LiDAR scan과 기존 map/scan이 잘 맞는 pose를 찾는 과정 |
| loop closure | 다시 방문한 장소를 인식해 누적 오차를 줄이는 과정 |
| pose graph | pose와 constraint를 graph 형태로 표현한 구조 |
| OccupancyGrid | 셀 단위로 빈 공간/장애물/미확인을 표현하는 지도 |
| resolution | map grid 한 칸이 실제 몇 m인지 나타내는 값 |
| origin | map 좌표계에서 이미지/map의 원점 정보 |
| map_saver_cli | map topic을 `.pgm`/`.yaml`로 저장하는 도구 |
| map_server | 저장된 map을 다시 ROS2 topic으로 발행하는 node |
| lifecycle node | configure/activate/deactivate 같은 상태 전이를 갖는 node |

---

## 6. AMCL / Localization 용어

| 용어 | 뜻 |
|---|---|
| AMCL | Adaptive Monte Carlo Localization |
| MCL | Monte Carlo Localization |
| particle | 로봇 위치 후보 |
| weight | 각 particle이 실제 관측과 얼마나 잘 맞는지 나타내는 값 |
| motion update | odometry 이동에 따라 particle을 이동시키는 단계 |
| sensor update | LiDAR 관측과 map 비교로 particle weight를 갱신하는 단계 |
| resampling | weight가 높은 particle을 중심으로 후보군을 다시 뽑는 단계 |
| initialpose | AMCL에 주는 초기 위치 힌트 |
| covariance | 위치/자세 추정의 불확실성 |
| particle cloud | particle 후보들을 RViz에서 보이게 한 것 |
| likelihood field model | beam endpoint와 가까운 장애물까지의 거리로 관측 확률을 평가하는 방식 |
| beam model | 각 laser beam의 예상 거리와 실제 거리를 비교하는 방식 |

---

## 7. Nav2 용어

| 용어 | 뜻 |
|---|---|
| Nav2 | ROS2 navigation stack |
| NavigateToPose | 목표 pose까지 이동하는 Nav2 action |
| bt_navigator | Behavior Tree로 navigation 흐름을 실행하는 node |
| Behavior Tree | navigation 과정을 조건/행동 노드 트리로 표현하는 방식 |
| planner_server | global path를 만드는 node |
| controller_server | path를 따라가기 위한 velocity command를 만드는 node |
| behavior_server | recovery/behavior 동작을 제공하는 node |
| smoother_server | path smoothing을 담당하는 node |
| global costmap | 전역 경로 계획에 쓰는 비용 지도 |
| local costmap | 로봇 주변 제어에 쓰는 비용 지도 |
| static layer | 저장된 map 기반 costmap layer |
| obstacle layer | 센서로 감지한 장애물 layer |
| inflation layer | 장애물 주변에 안전 여유 비용을 주는 layer |
| NavFn | grid 기반 global planner 중 하나 |
| Smac Planner | Nav2에서 제공하는 planner 계열 |
| DWB | local controller 계열. trajectory를 평가해 cmd_vel 선택 |
| critic | DWB에서 trajectory를 평가하는 기준 함수 |
| goal tolerance | 목표에 도착했다고 판단하는 허용 오차 |
| progress checker | 로봇이 충분히 진행 중인지 확인하는 component |
| velocity command | `/cmd_vel`로 나가는 선속도/각속도 명령 |

---

## 8. rosbag / 디버깅 용어

| 용어 | 뜻 |
|---|---|
| rosbag2 | ROS2 topic 데이터를 기록/재생하는 도구 |
| `--clock` | bag 재생 시 `/clock` topic을 발행하게 하는 옵션 |
| `use_sim_time` | node가 시스템 시간이 아니라 `/clock`을 사용하도록 하는 parameter |
| `tf2_echo` | 두 frame 사이 TF를 터미널에서 확인하는 도구 |
| `view_frames` | TF tree를 PDF 등으로 시각화하는 도구 |
| rqt_graph | node/topic 연결을 그래프로 보는 도구 |
| lifecycle state | lifecycle node의 현재 상태 |
| active | lifecycle node가 실제 기능을 수행하는 상태 |
| inactive | 설정은 됐지만 실제 기능 수행 전 상태 |

---

## 9. 이 정리본에서 특히 조심할 표현

| 표현 | 주의 |
|---|---|
| 구현했다 | 직접 알고리즘을 작성했는지, 패키지를 사용/설정했는지 구분해야 한다 |
| SLAM 완료 | 지도 생성 실습인지, SLAM 알고리즘 구현인지 구분해야 한다 |
| 자율주행 완성 | 현재 범위는 navigation pipeline 실습에 가깝다 |
