# ROS2 Foundation 트러블슈팅

## 1. `ros2 run`에서 executable을 못 찾는 경우

확인 순서:

```bash
pwd
ls src
colcon build --symlink-install
source install/setup.bash
ros2 pkg executables <package_name>
```

원인 후보:

```text
- workspace 루트가 아닌 곳에서 build함
- source install/setup.bash를 안 함
- setup.py console_scripts에 executable 등록이 없음
- CMakeLists.txt에서 install(TARGETS ...)가 없음
- package 이름과 executable 이름을 혼동함
```

---

## 2. node는 떠 있는데 topic이 안 보이는 경우

확인:

```bash
ros2 node list
ros2 node info /node_name
ros2 topic list
```

원인 후보:

```text
- publisher 생성 전 예외 발생
- 카메라/YOLO 모델 로드 실패
- callback이 실행되지 않음
- topic이 namespace 아래에 생성됨
- node name을 launch에서 바꿔서 다른 node를 보고 있음
```

---

## 3. publisher/subscriber가 연결되지 않는 경우

확인:

```bash
ros2 topic info /topic_name
ros2 topic echo /topic_name
```

확인할 것:

```text
- topic 이름이 같은가?
- message type이 같은가?
- namespace가 붙었는가?
- QoS가 호환되는가?
```

---

## 4. parameter가 적용되지 않는 경우

확인:

```bash
ros2 node list
ros2 param list /node_name
ros2 param get /node_name parameter_name
```

원인 후보:

```text
- YAML 최상위 키와 node name이 다름
- launch에서 node name을 바꿨는데 YAML은 기존 이름을 사용함
- parameter 파일 경로가 install/share 기준으로 설치되지 않음
- 코드에서 parameter를 읽지만 실제 동작에는 사용하지 않음
```

현재 예시:

```text
정리본의 image_publisher.py는 topic_name parameter를 publisher topic에 반영한다. topic이 보이지 않으면 실제 parameter 값과 topic list를 먼저 확인한다.
따라서 topic_name 변경은 실제 topic 변경으로 이어지지 않는다.
```

---

## 5. service call이 안 되는 경우

확인:

```bash
ros2 service list
ros2 service type /service_name
ros2 service call /service_name <type> "{...}"
```

원인 후보:

```text
- service server가 떠 있지 않음
- service 이름이 다름
- service type이 다름
- request YAML 문법이 틀림
```

---

## 6. action goal이 안 되는 경우

확인:

```bash
ros2 action list
ros2 action info /move_robot
ros2 action send_goal /move_robot ros2_foundation_interfaces/action/MoveDistance "{target_distance: 5.0}" --feedback
```

원인 후보:

```text
- action server가 떠 있지 않음
- action 이름이 다름
- action type이 다름
- namespace 때문에 실제 action 이름이 다름
```

Nav2에서도 같은 원리가 적용된다.

---

## 7. camera node가 안 되는 경우

확인:

```bash
ls /dev/video*
ros2 run ros2_camera_examples image_publisher
ros2 topic list
ros2 topic echo /image_raw --once
```

원인 후보:

```text
- 카메라 장치가 없음
- 다른 프로세스가 카메라를 사용 중
- Docker/WSL에서 카메라 접근이 안 됨
- OpenCV VideoCapture(0)가 다른 장치를 잡음
```

---

## 8. YOLO node가 안 되는 경우

확인:

```bash
python3 -c "from ultralytics import YOLO; print('ok')"
ros2 run ros2_camera_examples yolo_detection_publisher --ros-args -p model_path:=/absolute/path/to/yolov8n.pt
```

원인 후보:

```text
- ultralytics 미설치
- .venv 경로를 못 찾음
- yolov8n.pt 상대경로 문제
- GPU/CPU 환경 문제
- image_raw가 발행되지 않음
```

---

## 9. TF가 안 보이는 경우

확인:

```bash
ros2 topic list | grep tf
ros2 run tf2_tools view_frames
ros2 run tf2_ros tf2_echo odom base_link
ros2 run tf2_ros tf2_echo camera_link object_person_example_0
```

원인 후보:

```text
- parent frame이 TF tree에 없음
- child frame 이름이 예상과 다름
- source/target frame을 반대로 이해함
- msg.header.frame_id가 비어 있음
- static transform publisher를 실행하지 않음
```

---

## 10. RViz/rqt에서 안 보이는 경우

원인 후보를 분리해야 한다.

```text
1. topic 자체가 없는 문제
2. topic type이 다른 문제
3. GUI 환경 문제
4. RViz Fixed Frame 문제
5. TF tree 연결 문제
6. display 설정 문제
```

확인 순서:

```bash
ros2 topic list
ros2 topic info /target_topic
ros2 topic echo /target_topic --once
ros2 run tf2_tools view_frames
```

RViz에서 안 보인다고 바로 publisher가 없다고 판단하면 안 된다.
