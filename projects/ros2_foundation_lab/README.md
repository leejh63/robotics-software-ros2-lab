# ROS2 Foundation Lab

Day 06~09에서 작성한 ROS2 기초 실습 코드를 공개용으로 정리한 프로젝트입니다.
임시 실습 패키지명을 그대로 유지하지 않고, Topic, Service, Action, Interface, Launch, Camera, TF처럼 역할이 드러나도록 패키지를 나누었습니다.

이 프로젝트는 개념 정리 문서인 `day_06_09_ros2_foundation/`과 연결됩니다. 문서는 학습 흐름을 설명하고, 이 폴더는 실제 실행 가능한 코드를 담습니다.

## 패키지 구성

| Package | 내용 |
|---|---|
| `ros2_topic_examples` | Python topic publisher/subscriber, turtlesim `cmd_vel` 예제 |
| `ros2_cpp_examples` | C++ topic publisher/subscriber 예제 |
| `ros2_foundation_interfaces` | custom msg/srv/action 정의 |
| `ros2_service_examples` | service server/client 예제 |
| `ros2_action_examples` | action server/client 예제 |
| `ros2_camera_examples` | camera, OpenCV, YOLO image, custom detection message 예제 |
| `ros2_launch_examples` | camera/perception pipeline launch 예제 |
| `ros2_tf_examples` | TF tree, TF listener, object TF broadcaster 예제 |

## 의존성

공통 빌드는 ROS2 Humble 기본 개발 환경과 `colcon`, `rosdep`을 기준으로 합니다.

```bash
source /opt/ros/humble/setup.bash
rosdep install --from-paths src -y --ignore-src
```

`ros2_topic_examples`의 `turtle_square` 예제는 `turtlesim` 실행 환경을 사용합니다. Camera, YOLO, TF 시각화 예제는 아래 항목이 추가로 필요할 수 있습니다.

```bash
sudo apt install -y \
  python3-opencv \
  ros-humble-cv-bridge \
  ros-humble-rqt-image-view \
  ros-humble-rqt-tf-tree \
  ros-humble-rviz2 \
  ros-humble-tf-transformations \
  ros-humble-turtlesim

python3 -m pip install ultralytics
```

YOLO weight 파일은 Git에 포함하지 않습니다. 실행 시 로컬에 준비한 `yolov8n.pt` 같은 weight 파일을 사용합니다.

## 빌드

```bash
cd projects/ros2_foundation_lab
source /opt/ros/humble/setup.bash
rosdep install --from-paths src -y --ignore-src
colcon build --symlink-install
source install/setup.bash
```

## 기본 확인

```bash
ros2 pkg list | grep ros2_
ros2 pkg executables ros2_topic_examples
ros2 pkg executables ros2_service_examples
ros2 pkg executables ros2_action_examples
ros2 pkg executables ros2_camera_examples
ros2 pkg executables ros2_tf_examples
```

## 실행 예시

Topic publisher/subscriber:

```bash
ros2 run ros2_topic_examples string_talker
ros2 run ros2_topic_examples string_listener
```

Service server/client:

```bash
ros2 run ros2_service_examples add_two_num_server
ros2 run ros2_service_examples add_two_num_client
```

Action server/client:

```bash
ros2 run ros2_action_examples move_action_server
ros2 run ros2_action_examples move_action_client
```

Camera pipeline:

```bash
ros2 launch ros2_launch_examples camera_pipeline.launch.py use_viewer:=false
```

Camera + YOLO detection pipeline:

```bash
ros2 launch ros2_launch_examples camera_yolo_pipeline.launch.py use_viewer:=false
```

TF tree demo:

```bash
ros2 launch ros2_tf_examples tf_tree_demo.launch.py use_listener:=true use_rqt_tree:=false
```

YOLO detection 결과를 TF frame으로 연결하는 pipeline:

```bash
ros2 launch ros2_tf_examples yolo_tf_pipeline.launch.py \
  use_rviz:=false \
  use_rqt_tree:=false \
  use_listener:=true \
  class_filter:=person
```

## 확인 포인트

- `ros2_topic_examples`는 topic publish/subscribe의 가장 기본 흐름을 확인한다.
- `ros2_service_examples`는 request/response 구조를 확인한다.
- `ros2_action_examples`는 goal, feedback, result 흐름을 확인한다.
- `ros2_foundation_interfaces`는 custom msg/srv/action이 다른 패키지에서 어떻게 사용되는지 확인한다.
- `ros2_camera_examples`는 camera image topic과 OpenCV/YOLO 처리 흐름을 확인한다.
- `ros2_tf_examples`는 TF broadcaster/listener와 frame tree 구성을 확인한다.

## 참고

- `build/`, `install/`, `log/`, rosbag, 모델 weight, cache 파일은 포함하지 않습니다.
- Camera 예제는 사용 가능한 camera device와 `cv_bridge`가 필요합니다.
- YOLO 예제는 `ultralytics`와 로컬 모델 파일이 필요합니다. 예: `yolov8n.pt`
