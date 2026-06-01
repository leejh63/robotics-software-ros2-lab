# 09. Day 06~09 Runtime Notes

이 문서는 Day 06~09 실습 코드를 GitHub 공개용으로 정리하면서 확인한 실행상 주의점을 기록한다.

---

## 1. 정리 방향

원본 workspace의 실습 코드는 임시 패키지명과 개인 실습용 실행 이름이 섞여 있었다. 공개용 정리본에서는 패키지와 주요 executable 이름을 역할 기준으로 바꾸었다.

```text
this_test        -> ros2_topic_examples
lee_pkg          -> ros2_cpp_examples
my_if            -> ros2_foundation_interfaces
my_robot_service -> ros2_service_examples
my_robot_action  -> ros2_action_examples
camera_pkg       -> ros2_camera_examples
py_launch_example-> ros2_launch_examples
tf_pkg_lee       -> ros2_tf_examples
```

이름을 바꿀 때는 폴더명만 바꾸는 것이 아니라 `package.xml`, `setup.py`, `setup.cfg`, `CMakeLists.txt`, Python import, launch 파일, 문서 명령어까지 함께 맞춰야 한다.

---

## 2. 저장소에 포함하지 않는 파일

아래 파일은 실행 결과 또는 외부 데이터에 가깝기 때문에 GitHub 정리본에는 포함하지 않는다.

```text
rosbag2_*/
bags/
*.db3
*.mcap
*.posegraph
*.data
*.pt
*.onnx
build/
install/
log/
__pycache__/
*.pyc
```

YOLO 예제에서 필요한 `yolov8n.pt`는 저장소에 직접 넣지 않고, 실행 시 `model_path` parameter로 전달한다.

---

## 3. image_publisher parameter 반영

원본 `imagePlee.py`는 `topic_name`, `image_size` parameter를 선언했지만 실제 publisher topic과 camera size 일부가 고정값으로 남아 있었다. 정리본에서는 `image_publisher.py`에서 parameter가 실제 publisher와 camera 설정에 반영되도록 수정했다.

```text
publish topic: topic_name parameter 사용
camera index: camera_index parameter 사용
camera width/height: image_size parameter 사용
```

---

## 4. YOLO confidence parameter 반영

원본 `imageYOLOlee.py`는 `confidence` parameter를 선언했지만 추론 호출에서 사용하지 않았다. 정리본의 `yolo_image_publisher.py`에서는 다음 흐름으로 맞췄다.

```text
confidence parameter -> YOLO model inference conf argument
```

---

## 5. launch argument 이름 정리

원본 launch 파일에는 `use_rviz`라는 이름으로 `rqt_image_view`를 실행하는 부분이 있었다. 정리본의 camera launch 파일에서는 실제 동작에 맞게 `use_viewer`로 바꿨다.

```bash
ros2 launch ros2_launch_examples camera_pipeline.launch.py use_viewer:=true
```

TF launch에서 RViz를 실행하는 경우는 그대로 `use_rviz`를 사용한다.

---

## 6. RViz config 절대경로 제거

원본 `lee_yolo_launch.py`에는 개인 로컬 경로가 들어 있었다.

```text
<absolute-user-workspace-path>/...
```

정리본에서는 RViz config를 `ros2_tf_examples/rviz/yolo_tf.rviz`에 포함하고, `get_package_share_directory()`로 찾도록 바꿨다.

---

## 7. frame 이름 확인

정리본에서도 TF frame 이름은 실습 당시 사용한 이름을 크게 바꾸지 않았다.

```text
map
odom
base_link
camera_link
object_person_example_0
```

패키지명은 공개용으로 바꿨지만, frame 이름은 TF 흐름을 확인하기 위한 실습 맥락이 있으므로 유지했다. 나중에 더 일반화하려면 launch argument로 frame prefix를 받도록 확장할 수 있다.

---

## 8. 현재 검증 범위

이 정리본은 파일 구조, Python syntax, XML/YAML 파싱, 문서 링크, 패키지명/import/launch 참조를 정적으로 확인한 1차 정리본이다.

실제 ROS2 환경에서는 아래 명령으로 추가 확인이 필요하다.

```bash
cd projects/ros2_foundation_lab
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
ros2 pkg list | grep ros2_
```

이후 각 패키지별 `ros2 run`, `ros2 launch` smoke test를 진행하면 된다.

---

## GitHub 공개용 정리 기준

Phase 3에서는 공개 저장소에서 어색해 보일 수 있는 흔적을 추가로 정리했다.

```text
cpp_test1.cpp / cpp_test2.cpp -> cpp_talker.cpp / cpp_listener.cpp
frame_name_tag 기본값 lee -> example
ROS2 template test 디렉터리 제거
package.xml/setup.py maintainer email을 GitHub noreply 형식으로 통일
코드 내부 주요 log/comment를 영어로 통일
```

이 변경은 실습 의미를 바꾸기 위한 것이 아니라, 공개용 코드에서 역할과 이름이 바로 보이도록 다듬은 것이다.
