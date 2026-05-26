import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import PushRosNamespace


def generate_launch_description():
    pkg_dir = get_package_share_directory('lee_robot_description')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    namespace = LaunchConfiguration('namespace')
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    use_respawn = LaunchConfiguration('use_respawn')
    use_composition = LaunchConfiguration('use_composition')
    log_level = LaunchConfiguration('log_level')

    default_params_file = os.path.join(pkg_dir, 'config', 'nav2_params.yaml')
    navigation_launch_file = os.path.join(
        nav2_bringup_dir,
        'launch',
        'navigation_launch.py',
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'namespace',
            default_value='lee',
            description='Namespace used by the robot topics and TF topics.',
        ),
        DeclareLaunchArgument(
            'params_file',
            default_value=default_params_file,
            description='Nav2 navigation-only parameter file. It must match the selected namespace and frames.',
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use Gazebo simulation clock.',
        ),
        DeclareLaunchArgument(
            'autostart',
            default_value='true',
            description='Automatically configure and activate Nav2 navigation nodes.',
        ),
        DeclareLaunchArgument(
            'use_respawn',
            default_value='false',
            description='Respawn Nav2 nodes if a process crashes.',
        ),
        DeclareLaunchArgument(
            'use_composition',
            default_value='False',
            description='Use composed Nav2 bringup.',
        ),
        DeclareLaunchArgument(
            'log_level',
            default_value='info',
            description='Nav2 log level.',
        ),

        GroupAction([
            PushRosNamespace(namespace=namespace),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(navigation_launch_file),
                launch_arguments={
                    'namespace': namespace,
                    'params_file': params_file,
                    'use_sim_time': use_sim_time,
                    'autostart': autostart,
                    'use_respawn': use_respawn,
                    'use_composition': use_composition,
                    'log_level': log_level,
                }.items(),
            ),
        ]),
    ])
