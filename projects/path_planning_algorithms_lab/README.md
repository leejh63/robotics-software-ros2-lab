# Path Planning Algorithms Lab

This project contains Python notebook demos for path planning algorithms.

It is separated from `day_14_control_and_path_planning/` so the study notes and executable notebooks stay independent.

## Scope

Included notebooks:

```text
notebooks/14_03_01_dijkstra.ipynb
notebooks/14_03_02_astar.ipynb
notebooks/14_03_03_rrt.ipynb
notebooks/14_03_04_rrtstar.ipynb
```

This project does **not** implement a Nav2 planner plugin. It provides Python notebook demos for understanding path planning algorithms used conceptually in navigation systems.

## Setup

```bash
cd projects/path_planning_algorithms_lab
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run

```bash
jupyter notebook notebooks
```

or:

```bash
python -m pip install jupyterlab
jupyter lab notebooks
```

## Recommended order

```text
1. Dijkstra
2. A*
3. RRT
4. RRT*
```

## Related notes

- Day 14 path planning notes: [`../../day_14_control_and_path_planning/path_planning/`](../../day_14_control_and_path_planning/path_planning/)
