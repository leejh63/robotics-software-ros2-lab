import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    use_viewer_arg = DeclareLaunchArgument(
        'use_viewer',
        default_value='false',
        description='Run rqt_image_view for image topic inspection.',
    )

    camera_index_arg = DeclareLaunchArgument(
        'camera_index',
        default_value='0',
        description='OpenCV camera index used by image_publisher.',
    )

    camera_config = os.path.join(
        get_package_share_directory('ros2_camera_examples'),
        'config',
        'pub_cam_params.yaml',
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

    viewer_node = Node(
        package='rqt_image_view',
        executable='rqt_image_view',
        name='rqt_image_view',
        condition=IfCondition(LaunchConfiguration('use_viewer')),
        output='screen',
    )

    return LaunchDescription([
        use_viewer_arg,
        camera_index_arg,
        image_publisher,
        yolo_detection_publisher,
        viewer_node,
    ])
