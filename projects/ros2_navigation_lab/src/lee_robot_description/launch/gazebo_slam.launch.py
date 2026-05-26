import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_dir = get_package_share_directory('lee_robot_description')
    launch_dir = os.path.join(pkg_dir, 'launch')

    use_sim_time = LaunchConfiguration('use_sim_time')
    namespace = LaunchConfiguration('namespace')
    map_frame = LaunchConfiguration('map_frame')
    odom_frame = LaunchConfiguration('odom_frame')
    entity_name = LaunchConfiguration('entity_name')
    world = LaunchConfiguration('world')
    use_rviz = LaunchConfiguration('use_rviz')
    use_slam = LaunchConfiguration('use_slam')
    spawn_z = LaunchConfiguration('spawn_z')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use Gazebo simulation clock.',
        ),
        DeclareLaunchArgument(
            'namespace',
            default_value='lee',
            description='Robot namespace without a leading slash.',
        ),
        DeclareLaunchArgument(
            'map_frame',
            default_value='map_lee',
            description='Map frame published by SLAM Toolbox.',
        ),
        DeclareLaunchArgument(
            'odom_frame',
            default_value='odom_lee',
            description='Odometry frame passed to SLAM and the Gazebo xacro plugins.',
        ),
        DeclareLaunchArgument(
            'entity_name',
            default_value='turtlebot',
            description='Gazebo entity name used by spawn_entity.py.',
        ),
        DeclareLaunchArgument(
            'world',
            default_value='slam.world',
            description='Gazebo world file name under lee_robot_description/worlds. Default matches maps/slam_map.yaml.',
        ),
        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            description='Start RViz2 with the SLAM display config.',
        ),
        DeclareLaunchArgument(
            'use_slam',
            default_value='true',
            description='Start slam_toolbox for online async mapping.',
        ),
        DeclareLaunchArgument(
            'spawn_z',
            default_value='0.1',
            description='Initial z height for spawning turtlebot in Gazebo.',
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(launch_dir, 'slam.launch.py'),
            ),
            launch_arguments={
                'use_sim_time': use_sim_time,
                'namespace': namespace,
                'map_frame': map_frame,
                'odom_frame': odom_frame,
                'entity_name': entity_name,
                'world': world,
                'use_rviz': use_rviz,
                'use_slam': use_slam,
                'spawn_z': spawn_z,
            }.items(),
        ),
    ])
