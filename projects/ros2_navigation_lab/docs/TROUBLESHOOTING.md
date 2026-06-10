# Troubleshooting

이 문서는 `projects/ros2_navigation_lab` 실행 중 자주 확인해야 하는 문제를 정리합니다.

---

## `/lee/scan`이 보이지 않을 때

Gazebo가 로봇을 정상적으로 spawn했는지 확인합니다.

```bash
ros2 launch lee_robot_description gazebo.launch.py use_avoidance:=false
ros2 topic list | sort
```

`/lee/scan`이 없다면 `urdf/turtlebot_gaze.xacro`와 Gazebo sensor plugin namespace를 확인합니다.

---

## `odom_lee -> base_footprint` TF가 없을 때

odometry topic과 TF 출력을 확인합니다.

```bash
ros2 topic echo /lee/odom --once
ros2 run tf2_ros tf2_echo odom_lee base_footprint --ros-args -r /tf:=/lee/tf -r /tf_static:=/lee/tf_static
```

이 패키지는 TF를 `/lee/tf`, `/lee/tf_static`으로 publish합니다. remap 없이 `tf2_echo`를 실행하면 `/tf`, `/tf_static`을 보기 때문에 TF가 없는 것처럼 보일 수 있습니다.

odometry는 나오는데 TF가 없다면 URDF/Xacro의 differential drive plugin frame 설정을 확인합니다.

---

## AMCL pose가 publish되지 않을 때

AMCL에는 map, scan, TF, initial pose가 필요합니다.

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
ros2 topic echo /lee/map --once --qos-durability transient_local
ros2 topic echo /lee/scan --once
ros2 topic echo /amcl_pose --once
ros2 topic echo /particle_cloud --once
```

RViz 또는 `docs/RUNTIME_WORKFLOW.md`의 CLI 명령으로 `/initialpose`를 publish한 뒤, teleop으로 로봇을 조금 움직여 update를 유도합니다.

---

## Nav2 node가 `/lee` 아래에 뜨지 않을 때

node 이름을 확인합니다.

```bash
ros2 node list | sort | grep controller_server
ros2 node list | sort | grep planner_server
ros2 node list | sort | grep bt_navigator
```

정상 예시:

```text
/lee/controller_server
/lee/planner_server
/lee/bt_navigator
```

문제 예시:

```text
/controller_server
/lee/lee/controller_server
```

`PushRosNamespace`와 `nav2_bringup`의 namespace 인자를 동시에 바꿀 때는 runtime node 이름을 다시 확인해야 합니다.

---

## Nav2에서 DWB critic 관련 오류가 날 때

`FollowPath.critics` parameter가 제대로 들어갔는지 확인합니다.

```bash
ros2 param get /lee/controller_server controller_plugins
ros2 param get /lee/controller_server goal_checker_plugins
ros2 param get /lee/controller_server progress_checker_plugin
```

다음 파일을 확인합니다.

```text
src/lee_robot_description/config/nav2_params.yaml
```

`FollowPath.critics`는 `FollowPath` controller plugin 설정 아래에 있어야 합니다.

---

## Nav2나 teleop 없이 로봇이 움직일 때

선택 기능인 wall follower가 `/lee/cmd_vel`에 직접 publish할 수 있습니다. Nav2나 teleop 테스트 중에는 끄는 것이 안전합니다.

```bash
ros2 launch lee_robot_description gazebo.launch.py use_avoidance:=false
```

wall follower를 테스트할 때만 명시적으로 켭니다.

```bash
ros2 launch lee_robot_description gazebo.launch.py use_avoidance:=true
```
