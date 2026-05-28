# node 확인
ros2 node list

# topic 확인
ros2 topic list

# service 확인
ros2 service list

# turtlesim 화면 띄우기
ros2 run turtlesim turtlesim_node

# turtle 위치 확인
ros2 topic echo /turtle1/pose

# turtle 직접 이동
ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0}, angular: {z: 1.0}}" --once

# turtle2 생성
ros2 service call /spawn turtlesim/srv/Spawn "{x: 2.0, y: 2.0, theta: 0.0, name: 'turtle2'}"

# turtle2 조종
ros2 run turtlesim turtle_teleop_key --ros-args --remap turtle1/cmd_vel:=turtle2/cmd_vel

# turtle2 위치 확인
ros2 topic echo /turtle2/pose

# turtle2 삭제
ros2 service call /kill turtlesim/srv/Kill "{name: 'turtle2'}"

# 화면 지우기
ros2 service call /clear std_srvs/srv/Empty "{}"

# 초기화
ros2 service call /reset std_srvs/srv/Empty "{}"
