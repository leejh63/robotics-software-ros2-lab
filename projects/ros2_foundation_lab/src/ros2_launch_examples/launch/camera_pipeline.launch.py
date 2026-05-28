from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_viewer_arg = DeclareLaunchArgument(
        'use_viewer',
        default_value='false',
        description='Run rqt_image_view for image topic inspection.',
    )

    image_publisher = Node(
        package='ros2_camera_examples',
        executable='image_publisher',
        name='image_publisher',
        output='screen',
    )

    yolo_image_publisher = Node(
        package='ros2_camera_examples',
        executable='yolo_image_publisher',
        name='yolo_image_publisher',
        output='screen',
    )

    image_edge_publisher = Node(
        package='ros2_camera_examples',
        executable='image_edge_publisher',
        name='image_edge_publisher',
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
        image_publisher,
        yolo_image_publisher,
        image_edge_publisher,
        viewer_node,
    ])
