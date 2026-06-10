# 경로 탐색 알고리즘 실습

이 프로젝트는 Dijkstra, A*, RRT, RRT* 경로 탐색 알고리즘을 Python notebook으로 확인하기 위한 실습 코드입니다.

`day_14_control_and_path_planning/`은 개념 정리 문서이고, 이 폴더는 직접 실행할 수 있는 notebook 예제로 분리했습니다.

## 범위

포함된 notebook은 다음과 같습니다.

```text
notebooks/14_03_01_dijkstra.ipynb
notebooks/14_03_02_astar.ipynb
notebooks/14_03_03_rrt.ipynb
notebooks/14_03_04_rrtstar.ipynb
```

이 프로젝트는 Nav2 planner plugin을 구현하지 않습니다. Navigation 시스템에서 사용하는 경로 탐색 개념을 Python 예제로 이해하기 위한 실습입니다.

## 실행 준비

```bash
cd projects/path_planning_algorithms_lab
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 실행

```bash
jupyter notebook notebooks
```

또는 다음처럼 JupyterLab으로 실행할 수 있습니다.

```bash
python -m pip install jupyterlab
jupyter lab notebooks
```

## 추천 실행 순서

```text
1. Dijkstra
2. A*
3. RRT
4. RRT*
```

## 관련 문서

- Day 14 경로 탐색 정리: [`../../day_14_control_and_path_planning/path_planning/`](../../day_14_control_and_path_planning/path_planning/)
