# Path Planning

이 폴더는 Dijkstra, A*, RRT, RRT* 경로 탐색 알고리즘을 정리합니다.

```text
docs/       알고리즘 개념과 navigation 관점의 연결 정리
commands/   notebook 실행 명령
```

실행 가능한 notebook은 아래 위치에 분리했습니다.

```text
projects/path_planning_algorithms_lab/notebooks/
├── 14_03_01_dijkstra.ipynb
├── 14_03_02_astar.ipynb
├── 14_03_03_rrt.ipynb
└── 14_03_04_rrtstar.ipynb
```

이 코드는 Nav2 planner plugin 구현이 아니라, 경로 탐색 알고리즘을 이해하기 위한 Python notebook 실습입니다.

## 빠른 실행

```bash
cd projects/path_planning_algorithms_lab
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
jupyter notebook notebooks
```

개념 흐름은 `docs/`를 확인합니다. 실행 명령은 `commands/`를 확인합니다.
