import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _launch_setup(context, *args, **kwargs):
    pkg_dir = get_package_share_directory('lee_robot_description')

    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')
    rviz_config = LaunchConfiguration('rviz_config')

    map_frame = LaunchConfiguration('map_frame')
    odom_frame = LaunchConfiguration('odom_frame')
    base_frame = LaunchConfiguration('base_frame')
    scan_topic = LaunchConfiguration('scan_topic')
    map_topic = LaunchConfiguration('map_topic')
    map_updates_topic = LaunchConfiguration('map_updates_topic')
    tf_topic = LaunchConfiguration('tf_topic')
    tf_static_topic = LaunchConfiguration('tf_static_topic')

    default_rviz_file = os.path.join(pkg_dir, 'rviz', 'bag_slam.rviz')
    rviz_file = rviz_config.perform(context)
    if not rviz_file:
        rviz_file = default_rviz_file
    rviz_args = ['-d', rviz_file] if os.path.exists(rviz_file) else []

    return [
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[
                params_file,
                {
                    'use_sim_time': use_sim_time,
                    'map_frame': map_frame,
                    'odom_frame': odom_frame,
                    'base_frame': base_frame,
                    'scan_topic': scan_topic,
                },
            ],
            remappings=[
                ('/scan', scan_topic),
                ('/map', map_topic),
                ('/map_updates', map_updates_topic),
                ('/tf', tf_topic),
                ('/tf_static', tf_static_topic),
            ],
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz',
            output='screen',
            condition=IfCondition(use_rviz),
            arguments=rviz_args,
            parameters=[{'use_sim_time': use_sim_time}],
            remappings=[
                ('/tf', tf_topic),
                ('/tf_static', tf_static_topic),
            ],
        ),
    ]


def generate_launch_description():
    pkg_dir = get_package_share_directory('lee_robot_description')
    default_params_file = os.path.join(pkg_dir, 'config', 'bag_slam_param.yaml')
    default_rviz_file = os.path.join(pkg_dir, 'rviz', 'bag_slam.rviz')

    return LaunchDescription([
        DeclareLaunchArgument(
            'params_file',
            default_value=default_params_file,
            description='SLAM Toolbox parameter file for rosbag mapping.',
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use /clock from ros2 bag play --clock.',
        ),
        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            description='Start RViz2 for rosbag SLAM visualization.',
        ),
        DeclareLaunchArgument(
            'rviz_config',
            default_value=default_rviz_file,
            description='RViz config file path. Pass an empty string to use RViz defaults.',
        ),
        DeclareLaunchArgument(
            'map_frame',
            default_value='map_lee',
            description='Map frame published by SLAM Toolbox.',
        ),
        DeclareLaunchArgument(
            'odom_frame',
            default_value='odom',
            description='Odometry frame recorded inside the rosbag messages.',
        ),
        DeclareLaunchArgument(
            'base_frame',
            default_value='base_footprint',
            description='Robot base frame recorded inside the rosbag messages.',
        ),
        DeclareLaunchArgument(
            'scan_topic',
            default_value='/lee/scan',
            description='LaserScan topic consumed by SLAM Toolbox.',
        ),
        DeclareLaunchArgument(
            'map_topic',
            default_value='/lee/map',
            description='Map topic published by SLAM Toolbox.',
        ),
        DeclareLaunchArgument(
            'map_updates_topic',
            default_value='/lee/map_updates',
            description='Map updates topic published by SLAM Toolbox.',
        ),
        DeclareLaunchArgument(
            'tf_topic',
            default_value='/lee/tf',
            description='TF topic used by the rosbag replay workflow.',
        ),
        DeclareLaunchArgument(
            'tf_static_topic',
            default_value='/lee/tf_static',
            description='Static TF topic used by the rosbag replay workflow.',
        ),
        OpaqueFunction(function=_launch_setup),
    ])
