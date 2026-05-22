# Launch / Parameter / Debug Commands

## 1. launch 파일 확인

```bash
ros2 launch py_launch_example lee_bring_launch.py
ros2 launch py_launch_example lee_ep_launch.py
ros2 launch tf_pkg_example tf_tree_demo_launch.py
ros2 launch tf_pkg_example lee_yolo_launch.py
```

launch argument 확인:

```bash
ros2 launch py_launch_example lee_ep_launch.py --show-args
ros2 launch tf_pkg_example lee_yolo_launch.py --show-args
```

---

## 2. parameter 확인

`lee_ep_launch.py`는 `image_pub1` 노드 이름을 `test`로 실행한다.

```bash
ros2 launch py_launch_example lee_ep_launch.py
ros2 param list /test
ros2 param get /test publish_rate
ros2 param get /test image_size
ros2 param get /test topic_name
```

변경:

```bash
ros2 param set /test publish_rate 5.0
ros2 param set /test image_size "[320, 240]"
```

주의:

```text
현재 imagePlee.py에서는 topic_name parameter를 읽지만 publisher는 image_raw0로 고정되어 있다.
따라서 topic_name을 바꿔도 실제 topic은 바뀌지 않는다.
```

---

## 3. node/topic 연결 확인

```bash
ros2 node list
ros2 node info /test
ros2 topic list
ros2 topic info /image_raw0
ros2 topic hz /image_raw0
```

---

## 4. custom interface 확인

```bash
ros2 interface list | grep my_if
ros2 interface show my_if/msg/ObjectDetectionArray
ros2 interface show my_if/srv/AddTwoNum
ros2 interface show my_if/action/Movelee
```

---

## 5. YOLO model_path parameter로 지정

상대경로 문제를 피하려면 명시적으로 model path를 넘긴다.

```bash
ros2 run camera_pkg yolo_pub_l --ros-args -p model_path:=/absolute/path/to/yolov8n.pt
ros2 run camera_pkg image_yolo1 --ros-args -p model_path:=/absolute/path/to/yolov8n.pt -p confidence:=0.5
```

---

## 6. rqt tools

```bash
rqt_graph
rqt_image_view
ros2 run rqt_tf_tree rqt_tf_tree
```

`rqt_graph`는 node/topic 연결을 보기 좋고, `rqt_image_view`는 image topic 확인에 좋다. TF는 `rqt_tf_tree`나 `view_frames`가 더 적합하다.
