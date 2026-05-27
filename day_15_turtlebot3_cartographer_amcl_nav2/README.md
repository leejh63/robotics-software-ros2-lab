# TurtleBot3 Day 15 문서 묶음

이 문서 묶음은 TurtleBot3 Burger 실습에서 진행한 내용을 역할별로 나누어 정리한 것이다.

기준 워크스페이스:

```bash
$TB3_WS
```

지도 저장 경로:

```bash
$TB3_WS/maps
```

현재 정리 기준은 다음과 같다.

1. `~/.bashrc`에 TurtleBot3 워크스페이스를 직접 고정하지 않는다.
2. 각 터미널에서 `source ~/envs/tb3_humble.bash`로 필요한 환경만 적용한다.
3. 지도 저장 경로는 `maps/`로 통일한다.
4. Cartographer 지도 저장은 `.pbstream` 저장 후 `.pgm + .yaml` 변환 방식을 기준으로 한다.
5. AMCL/Nav2 단계에서는 임시 `static_transform_publisher map odom`을 사용하지 않는다.
6. `map -> odom`은 AMCL이 초기 위치를 받은 뒤 추정해서 발행한다.
7. `navigation2.launch.py`를 사용할 때는 개별 `map_server`, `amcl`, `lifecycle_manager`와 중복 실행하지 않는다.


## 경로 표기 기준

문서에서는 개인 경로를 직접 쓰지 않고 아래 변수로 워크스페이스를 표현한다.

```bash
# 예시: 사용자의 실제 TurtleBot3 워크스페이스 경로로 지정한다.
export TB3_WS=~/turtlebot3_ws
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
```

## 문서 구성

| 파일 | 역할 |
|---|---|
| `00_source_overview.md` | 문서 범위, 코드 미포함 기준, 재현 방식 |
| `01_environment_setup.md` | 환경 설정, 워크스페이스, 환경 파일 사용 기준 |
| `02_cartographer_slam_map_save.md` | Gazebo + Cartographer SLAM, 지도 저장, pbstream 변환 |
| `03_amcl_localization.md` | 저장된 지도 기반 AMCL 위치 추정 |
| `04_navigation2_run.md` | 저장된 지도 기반 Navigation2 실행 |
| `05_runtime_notes.md` | 실행 중 확인한 판단 기준과 주의사항 |
| `06_auto_exploration_explore_lite.md` | slam_toolbox + Nav2 + Explore Lite 자동 탐색 확장 흐름 |
| `commands/turtlebot3_day15_commands.md` | 실제 실행 명령어만 모은 문서 |
| `troubleshooting/turtlebot3_day15_troubleshooting.md` | 이번 실습 중 겪은 문제와 해결 |

## 전체 흐름

Day 15는 목적이 다른 두 흐름을 분리해서 정리한다.

### 흐름 A — 저장 지도 기반 Navigation2

```text
환경 준비
→ Gazebo 실행
→ Cartographer SLAM 실행
→ Teleop 주행
→ /write_state로 pbstream 저장
→ pbstream_to_ros_map으로 pgm/yaml 변환
→ map_server + AMCL 실행
→ /initialpose로 초기 위치 설정
→ Navigation2 실행
```

이 흐름은 먼저 지도를 만들고, 저장된 지도에서 AMCL로 위치를 추정한 뒤 Nav2 목표 주행을 확인하는 방식이다.

### 흐름 B — Explore Lite 자동 탐색

```text
Gazebo
→ slam_toolbox online SLAM
→ nav2_bringup navigation_launch.py
→ explore_lite frontier exploration
→ 탐색 후 map_saver_cli로 지도 저장
```

이 흐름은 저장된 지도를 먼저 쓰지 않는다. SLAM으로 지도를 만드는 동시에 `explore_lite`가 frontier를 찾아 Nav2 목표를 보내는 방식이다.

두 흐름은 `map -> odom`을 담당하는 노드가 다르므로 섞어 실행하지 않는다.

| 흐름 | `map -> odom` 담당 | 사용하지 않는 것 |
|---|---|---|
| Cartographer 저장 지도 + AMCL + Nav2 | AMCL | 임시 `static_transform_publisher map odom` |
| slam_toolbox + Nav2 + Explore Lite | slam_toolbox | AMCL, 저장 지도용 map_server, 임시 `static_transform_publisher map odom` |

Explore Lite 상세 흐름은 [`06_auto_exploration_explore_lite.md`](06_auto_exploration_explore_lite.md)를 기준으로 본다.
