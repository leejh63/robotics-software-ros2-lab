# 09. Day 10 복습 질문

이 문서는 Day 10을 제대로 이해했는지 확인하기 위한 질문 모음이다.

---

## 1. URDF / Xacro

1. URDF에서 `link`와 `joint`의 차이는 무엇인가?
2. `visual`, `collision`, `inertial`은 각각 어디에 쓰이는가?
3. RViz2에서 로봇이 보이는데 Gazebo에서 물리 동작이 이상할 수 있는 이유는 무엇인가?
4. Xacro의 `macro`, `property`, `include`는 왜 필요한가?
5. `turtlebot.xacro`와 `turtlebot_gaze.xacro`의 역할은 어떻게 다른가?
6. `base_scan`, `camera_link`, `imu_link`는 센서 데이터 자체인가, 센서가 붙는 좌표계인가?

---

## 2. robot_state_publisher / TF

1. `robot_state_publisher`는 로봇을 움직이는 노드인가?
2. `robot_description`에는 무엇이 들어가는가?
3. `/tf`와 `/tf_static`의 차이는 무엇인가?
4. `/lee/joint_states`가 필요한 이유는 무엇인가?
5. `/tf`를 `/lee/tf`로 remap하면 어떤 장점과 단점이 있는가?
6. topic namespace가 frame 이름을 자동으로 바꾸지 않는다는 말은 무슨 뜻인가?

---

## 3. Gazebo plugin

1. Gazebo plugin이 없다면 `/lee/scan`, `/lee/odom`, `/lee/image_raw`가 자동으로 생기는가?
2. diff drive plugin은 어떤 topic을 구독하고 어떤 topic을 발행하는가?
3. LiDAR plugin의 `<frame_name>base_scan</frame_name>`은 무엇을 의미하는가?
4. `/lee/scan`과 `base_scan`의 차이는 무엇인가?
5. camera plugin이 발행하는 `/lee/image_raw`는 Day 06~09의 OpenCV/YOLO 노드와 어떻게 연결될 수 있는가?

---

## 4. Launch / World / Namespace

1. world 파일은 로봇을 정의하는 파일인가, 환경을 정의하는 파일인가?
2. `libgazebo_ros_init.so`와 `libgazebo_ros_factory.so`는 왜 필요한가?
3. `spawn_entity.py`의 `-entity turtlebot`는 ROS node 이름인가, Gazebo 모델 이름인가?
4. `use_sim_time:=true`는 왜 중요한가?
5. `/clock` publisher가 여러 개 있으면 어떤 문제가 생길 수 있는가?

---

## 5. LaserScan / 회피 노드

1. LaserScan의 `ranges[index]`가 어느 방향인지 어떻게 계산하는가?
2. 왜 `ranges[180]`이 항상 정면이라고 외우면 안 되는가?
3. 현재 `lidar_wall_follower.py`가 진짜 wall following이 아니라 단순 장애물 회피에 가까운 이유는 무엇인가?
4. teleop과 회피 노드를 동시에 켜면 왜 `/lee/cmd_vel` 충돌이 생기는가?

---

## 6. Day 11 연결 질문

1. SLAM Toolbox가 사용하기 위해 Day 10에서 준비되어야 하는 핵심 topic은 무엇인가?
2. `/lee/scan`이 있어도 TF가 맞지 않으면 SLAM이 어려운 이유는 무엇인가?
3. Gazebo에서 만든 `/lee/odom`은 실제 로봇의 wheel encoder odom과 어떤 점에서 비슷하고 어떤 점에서 다른가?
4. Day 10에서 frame/topic 구조를 대충 넘기면 Day 11~13에서 어떤 문제가 생길 수 있는가?
