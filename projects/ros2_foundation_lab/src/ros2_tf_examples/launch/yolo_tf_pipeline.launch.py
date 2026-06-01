import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='false',
        description='Run RViz2 with the packaged TF visualization config.',
    )

    use_rqt_tree_arg = DeclareLaunchArgument(
        'use_rqt_tree',
        default_value='false',
        description='Run rqt_tf_tree.',
    )

    use_listener_arg = DeclareLaunchArgument(
        'use_listener',
        default_value='false',
        description='Run tf_listener for a selected object frame.',
    )

    camera_index_arg = DeclareLaunchArgument(
        'camera_index',
        default_value='0',
        description='OpenCV camera index used by image_publisher.',
    )

    class_filter_arg = DeclareLaunchArgument(
        'class_filter',
        default_value='person',
        description='YOLO class name to publish as TF.',
    )

    frame_name_tag_arg = DeclareLaunchArgument(
        'frame_name_tag',
        default_value='example',
        description='Tag inserted into object TF frame names.',
    )

    listener_source_frame_arg = DeclareLaunchArgument(
        'listener_source_frame',
        default_value='object_person_example_0',
        description='Source frame queried by tf_listener.',
    )

    object_depth_arg = DeclareLaunchArgument(
        'object_depth',
        default_value='1.0',
        description='Fixed depth used for YOLO object TF frames.',
    )

    map_odom_x_arg = DeclareLaunchArgument(
        'map_odom_x',
        default_value='1.5',
        description='X offset from map to odom.',
    )

    camera_config = os.path.join(
        get_package_share_directory('ros2_camera_examples'),
        'config',
        'pub_cam_params.yaml',
    )

    rviz_config = os.path.join(
        get_package_share_directory('ros2_tf_examples'),
        'rviz',
        'yolo_tf.rviz',
    )

    image_publisher = Node(
        package='ros2_camera_examples',
        executable='image_publisher',
        name='image_publisher',
        parameters=[camera_config, {
            'camera_index': ParameterValue(
                LaunchConfiguration('camera_index'), value_type=int),
        }],
        output='screen',
    )

    yolo_detection_publisher = Node(
        package='ros2_camera_examples',
        executable='yolo_detection_publisher',
        name='yolo_detection_publisher',
        output='screen',
    )

    map_to_odom = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='map_to_odom',
        arguments=[
            '--x', LaunchConfiguration('map_odom_x'),
            '--y', '0.0',
            '--z', '0.0',
            '--roll', '0.0',
            '--pitch', '0.0',
            '--yaw', '0.0',
            '--frame-id', 'map',
            '--child-frame-id', 'odom',
        ],
        output='screen',
    )

    odom_simulator = Node(
        package='ros2_tf_examples',
        executable='odom_simulator',
        name='odom_simulator',
        output='screen',
    )

    base_to_camera = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_to_camera_link',
        arguments=[
            '--x', '0.1',
            '--y', '0.0',
            '--z', '0.2',
            '--roll', '0.0',
            '--pitch', '0.0',
            '--yaw', '0.0',
            '--frame-id', 'base_link',
            '--child-frame-id', 'camera_link',
        ],
        output='screen',
    )

    yolo_tf_broadcaster = Node(
        package='ros2_tf_examples',
        executable='yolo_tf_broadcaster',
        name='yolo_tf_broadcaster',
        parameters=[{
            'detection_topic': 'yolo_detections',
            'class_filter': LaunchConfiguration('class_filter'),
            'frame_name_tag': LaunchConfiguration('frame_name_tag'),
            'fallback_parent_frame': 'camera_link',
            'image_width': 320.0,
            'image_height': 240.0,
            'fixed_depth': ParameterValue(LaunchConfiguration('object_depth'), value_type=float),
        }],
        output='screen',
    )

    tf_listener = Node(
        package='ros2_tf_examples',
        executable='tf_listener',
        name='tf_listener',
        parameters=[{
            'target_frame': 'odom',
            'source_frame': LaunchConfiguration('listener_source_frame'),
        }],
        condition=IfCondition(LaunchConfiguration('use_listener')),
        output='screen',
    )

    rqt_tf_tree = Node(
        package='rqt_tf_tree',
        executable='rqt_tf_tree',
        name='rqt_tf_tree',
        condition=IfCondition(LaunchConfiguration('use_rqt_tree')),
        output='screen',
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        condition=IfCondition(LaunchConfiguration('use_rviz')),
        output='screen',
    )

    return LaunchDescription([
        use_rviz_arg,
        use_rqt_tree_arg,
        use_listener_arg,
        camera_index_arg,
        class_filter_arg,
        frame_name_tag_arg,
        listener_source_frame_arg,
        object_depth_arg,
        map_odom_x_arg,
        image_publisher,
        yolo_detection_publisher,
        map_to_odom,
        odom_simulator,
        base_to_camera,
        yolo_tf_broadcaster,
        tf_listener,
        rqt_tf_tree,
        rviz,
    ])
