# 00. Path planning notebook 실행

Dijkstra, A*, RRT, RRT* 실습 notebook은 아래 위치에 있습니다.

```text
projects/path_planning_algorithms_lab/notebooks/
```

## 1. 가상환경 생성

```bash
cd projects/path_planning_algorithms_lab
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 2. Jupyter 실행

```bash
jupyter notebook notebooks
```

또는 JupyterLab을 쓰는 경우:

```bash
python -m pip install jupyterlab
jupyter lab notebooks
```

## 3. 실행 순서

```text
1. 14_03_01_dijkstra.ipynb
2. 14_03_02_astar.ipynb
3. 14_03_03_rrt.ipynb
4. 14_03_04_rrtstar.ipynb
```

Dijkstra와 A*는 같은 grid/costmap 기반 흐름을 비교하고, RRT와 RRT*는 sampling tree 계열 흐름을 비교합니다.
