# Launch / Parameter / Debug Commands

## 1. launch 파일 확인

```bash
ros2 launch ros2_launch_examples camera_pipeline.launch.py --show-args
ros2 launch ros2_launch_examples camera_yolo_pipeline.launch.py --show-args
ros2 launch ros2_tf_examples tf_tree_demo.launch.py --show-args
ros2 launch ros2_tf_examples yolo_tf_pipeline.launch.py --show-args
```

실행:

```bash
ros2 launch ros2_launch_examples camera_pipeline.launch.py
ros2 launch ros2_launch_examples camera_yolo_pipeline.launch.py
ros2 launch ros2_tf_examples tf_tree_demo.launch.py
ros2 launch ros2_tf_examples yolo_tf_pipeline.launch.py
```

---

## 2. parameter 확인

`camera_yolo_pipeline.launch.py`는 `image_publisher` 노드에 YAML parameter를 적용한다.

```bash
ros2 launch ros2_launch_examples camera_yolo_pipeline.launch.py
ros2 param list /image_publisher
ros2 param get /image_publisher publish_rate
ros2 param get /image_publisher image_size
ros2 param get /image_publisher topic_name
ros2 param get /image_publisher camera_index
```

변경:

```bash
ros2 param set /image_publisher publish_rate 5.0
ros2 param set /image_publisher image_size "[320, 240]"
```

---

## 3. node/topic 연결 확인

```bash
ros2 node list
ros2 node info /image_publisher
ros2 topic list
ros2 topic info /image_raw
ros2 topic hz /image_raw
```

---

## 4. custom interface 확인

```bash
ros2 interface list | grep ros2_foundation_interfaces
ros2 interface show ros2_foundation_interfaces/msg/ObjectDetectionArray
ros2 interface show ros2_foundation_interfaces/srv/AddTwoNum
ros2 interface show ros2_foundation_interfaces/action/MoveDistance
```

---

## 5. YOLO model_path parameter 지정

`yolov8n.pt`는 저장소에 포함하지 않는다. 실행할 때 모델 경로를 명시한다.

```bash
ros2 run ros2_camera_examples yolo_detection_publisher --ros-args -p model_path:=/absolute/path/to/yolov8n.pt
ros2 run ros2_camera_examples yolo_image_publisher --ros-args -p model_path:=/absolute/path/to/yolov8n.pt -p confidence:=0.5
```

---

## 6. rqt tools

```bash
rqt_graph
rqt_image_view
ros2 run rqt_tf_tree rqt_tf_tree
```

`rqt_graph`는 node/topic 연결 확인에 좋고, `rqt_image_view`는 image topic 확인에 좋다. TF는 `rqt_tf_tree`나 `view_frames`가 더 적합하다.
