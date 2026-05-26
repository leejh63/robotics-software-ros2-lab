import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_dir = get_package_share_directory('lee_robot_description')
    launch_dir = os.path.join(pkg_dir, 'launch')
    default_map_yaml = os.path.join(pkg_dir, 'maps', 'slam_map.yaml')
    default_params_file = os.path.join(pkg_dir, 'config', 'nav2_params.yaml')

    namespace = LaunchConfiguration('namespace')
    map_frame = LaunchConfiguration('map_frame')
    odom_frame = LaunchConfiguration('odom_frame')
    entity_name = LaunchConfiguration('entity_name')
    world = LaunchConfiguration('world')
    map_yaml = LaunchConfiguration('map_yaml')
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')
    spawn_z = LaunchConfiguration('spawn_z')
    autostart = LaunchConfiguration('autostart')
    use_respawn = LaunchConfiguration('use_respawn')
    use_composition = LaunchConfiguration('use_composition')
    log_level = LaunchConfiguration('log_level')

    return LaunchDescription([
        DeclareLaunchArgument(
            'namespace',
            default_value='lee',
            description='Robot namespace without a leading slash.',
        ),
        DeclareLaunchArgument(
            'map_frame',
            default_value='map_lee',
            description='Map frame used by localization.',
        ),
        DeclareLaunchArgument(
            'odom_frame',
            default_value='odom_lee',
            description='Odometry frame used by localization and Gazebo plugins.',
        ),
        DeclareLaunchArgument(
            'entity_name',
            default_value='turtlebot',
            description='Gazebo entity name used by spawn_entity.py.',
        ),
        DeclareLaunchArgument(
            'world',
            default_value='slam.world',
            description='Gazebo world file name under lee_robot_description/worlds.',
        ),
        DeclareLaunchArgument(
            'map_yaml',
            default_value=default_map_yaml,
            description='Map yaml file path loaded by nav2_map_server.',
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
            'use_rviz',
            default_value='true',
            description='Start RViz2 with the AMCL display config.',
        ),
        DeclareLaunchArgument(
            'spawn_z',
            default_value='0.3',
            description='Initial z height for spawning turtlebot in Gazebo.',
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
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(launch_dir, 'localization.launch.py'),
            ),
            launch_arguments={
                'namespace': namespace,
                'map_frame': map_frame,
                'odom_frame': odom_frame,
                'entity_name': entity_name,
                'world': world,
                'map_yaml': map_yaml,
                'use_sim_time': use_sim_time,
                'use_rviz': use_rviz,
                'spawn_z': spawn_z,
            }.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(launch_dir, 'nav2_navigation.launch.py'),
            ),
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
    ])
