# 00. Source Overview

이 폴더는 TurtleBot3 Burger 기반 Gazebo, Cartographer SLAM, AMCL, Navigation2 실습을 문서 중심으로 정리한 것이다.

실습 코드는 이 저장소에 별도로 추가하지 않는다.  
재현에 필요한 패키지는 문서의 명령어를 통해 ROS2 패키지 또는 공식 TurtleBot3 저장소에서 내려받아 사용한다.

## 포함하는 것

```text
환경 설정 기준
Gazebo 실행 흐름
Cartographer SLAM 실행 및 지도 저장
pbstream -> pgm/yaml 변환
map_server 확인
AMCL 위치 추정
Navigation2 실행
slam_toolbox + Explore Lite 자동 탐색 확장 흐름
실행 명령어
문제 해결 기록
```

## 포함하지 않는 것

```text
빌드 산출물
rosbag 원본 데이터
생성된 map 파일
개인 워크스페이스 경로
실습 중 임시 로그
```

## 경로 표기 원칙

문서에서는 개인 경로를 직접 쓰지 않고 아래 변수로 워크스페이스를 표현한다.

```bash
export TB3_WS=~/turtlebot3_ws
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
```

지도 파일은 다음 위치를 기준으로 설명한다.

```bash
$TB3_WS/maps/tb3_map.yaml
$TB3_WS/maps/tb3_map.pbstream
$TB3_WS/maps/tb3_map.pgm
```

## 재현 방식

이 폴더의 문서를 순서대로 보면 Git에서 저장소를 받은 뒤에도 별도 실습 코드 없이 동일 흐름을 재현할 수 있다.

권장 순서:

```text
README.md
01_environment_setup.md
02_cartographer_slam_map_save.md
03_amcl_localization.md
04_navigation2_run.md
05_runtime_notes.md
06_auto_exploration_explore_lite.md
commands/turtlebot3_day15_commands.md
troubleshooting/turtlebot3_day15_troubleshooting.md
```
