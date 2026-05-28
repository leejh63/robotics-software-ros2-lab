from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_listener_arg = DeclareLaunchArgument(
        'use_listener',
        default_value='false',
        description='Run tf_listener for the left_marker frame.',
    )

    use_rqt_tree_arg = DeclareLaunchArgument(
        'use_rqt_tree',
        default_value='false',
        description='Run rqt_tf_tree.',
    )

    tf_tree_simulator = Node(
        package='ros2_tf_examples',
        executable='tf_tree_simulator',
        name='tf_tree_simulator',
        output='screen',
    )

    tf_listener = Node(
        package='ros2_tf_examples',
        executable='tf_listener',
        name='tf_listener',
        parameters=[{
            'target_frame': 'odom',
            'source_frame': 'left_marker',
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

    return LaunchDescription([
        use_listener_arg,
        use_rqt_tree_arg,
        tf_tree_simulator,
        tf_listener,
        rqt_tf_tree,
    ])
