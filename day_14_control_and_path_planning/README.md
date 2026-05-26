# Day 14 - Control and Path Planning

Day 14는 서로 성격이 다른 두 주제를 같은 날짜 안에서 분리해 정리한 폴더입니다.

```text
pid_control/      PID 제어, ros2_control, Gazebo 1-DOF arm 실습
path_planning/    Dijkstra, A*, RRT, RRT* 경로 탐색 실습
```

이 폴더는 학습 문서와 실행 명령을 정리합니다. 실제 실행 가능한 코드는 `projects/` 아래에 분리했습니다.

```text
day_14_control_and_path_planning/
├── README.md
├── pid_control/
│   ├── README.md
│   ├── docs/
│   └── commands/
└── path_planning/
    ├── README.md
    ├── docs/
    └── commands/

projects/
├── ros2_pid_arm_lab/
└── path_planning_algorithms_lab/
```

## 빠른 접근

| 목적 | 위치 |
|---|---|
| PID 제어 개념 정리 | [`pid_control/docs/`](pid_control/docs/) |
| Gazebo PID arm 실행 명령 | [`pid_control/commands/`](pid_control/commands/) |
| ROS2 PID arm 실행 코드 | [`../projects/ros2_pid_arm_lab/`](../projects/ros2_pid_arm_lab/) |
| 경로 탐색 개념 정리 | [`path_planning/docs/`](path_planning/docs/) |
| Dijkstra/A*/RRT/RRT* notebook | [`../projects/path_planning_algorithms_lab/`](../projects/path_planning_algorithms_lab/) |
| notebook 실행 명령 | [`path_planning/commands/00_run_notebooks.md`](path_planning/commands/00_run_notebooks.md) |

## 정리 기준

원본 강의 PDF는 포함하지 않고, 직접 정리한 Markdown 문서와 실행 가능한 코드만 남겼다. 특정 로컬 PC 경로에 강하게 묶인 내용과 중복 설명은 제외했다.
