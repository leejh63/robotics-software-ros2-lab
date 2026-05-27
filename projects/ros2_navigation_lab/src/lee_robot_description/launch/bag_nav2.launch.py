import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_dir = get_package_share_directory('lee_robot_description')
    launch_dir = os.path.join(pkg_dir, 'launch')

    default_map_yaml = os.path.join(pkg_dir, 'maps', 'bag_slam_map.yaml')
    default_amcl_params_file = os.path.join(pkg_dir, 'config', 'bag_amcl_param.yaml')
    default_nav2_params_file = os.path.join(pkg_dir, 'config', 'bag_nav2_params.yaml')
    default_rviz_file = os.path.join(pkg_dir, 'rviz', 'bag_nav2.rviz')

    namespace = LaunchConfiguration('namespace')
    map_yaml = LaunchConfiguration('map_yaml')
    amcl_params_file = LaunchConfiguration('amcl_params_file')
    nav2_params_file = LaunchConfiguration('nav2_params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')
    rviz_config = LaunchConfiguration('rviz_config')

    map_frame = LaunchConfiguration('map_frame')
    odom_frame = LaunchConfiguration('odom_frame')
    base_frame = LaunchConfiguration('base_frame')
    scan_topic = LaunchConfiguration('scan_topic')
    map_topic = LaunchConfiguration('map_topic')
    tf_topic = LaunchConfiguration('tf_topic')
    tf_static_topic = LaunchConfiguration('tf_static_topic')

    autostart = LaunchConfiguration('autostart')
    use_respawn = LaunchConfiguration('use_respawn')
    use_composition = LaunchConfiguration('use_composition')
    log_level = LaunchConfiguration('log_level')

    return LaunchDescription([
        DeclareLaunchArgument(
            'namespace',
            default_value='lee',
            description='Nav2 node namespace.',
        ),
        DeclareLaunchArgument(
            'map_yaml',
            default_value=default_map_yaml,
            description='Map yaml generated from rosbag SLAM.',
        ),
        DeclareLaunchArgument(
            'amcl_params_file',
            default_value=default_amcl_params_file,
            description='AMCL parameter file for rosbag replay localization.',
        ),
        DeclareLaunchArgument(
            'nav2_params_file',
            default_value=default_nav2_params_file,
            description='Nav2 parameter file for rosbag replay costmap/navigation checks.',
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use /clock from ros2 bag play --clock.',
        ),
        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            description='Start RViz2 with costmap displays.',
        ),
        DeclareLaunchArgument(
            'rviz_config',
            default_value=default_rviz_file,
            description='RViz config file path.',
        ),
        DeclareLaunchArgument(
            'map_frame',
            default_value='map_lee',
            description='Map frame used by map_server, AMCL, and Nav2 global costmap.',
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
            description='LaserScan topic consumed by AMCL and Nav2 costmaps.',
        ),
        DeclareLaunchArgument(
            'map_topic',
            default_value='/lee/map',
            description='Map topic published by map_server.',
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
                os.path.join(launch_dir, 'bag_localization.launch.py'),
            ),
            launch_arguments={
                'map_yaml': map_yaml,
                'amcl_params_file': amcl_params_file,
                'use_sim_time': use_sim_time,
                'use_rviz': use_rviz,
                'rviz_config': rviz_config,
                'map_frame': map_frame,
                'odom_frame': odom_frame,
                'base_frame': base_frame,
                'scan_topic': scan_topic,
                'map_topic': map_topic,
                'tf_topic': tf_topic,
                'tf_static_topic': tf_static_topic,
            }.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(launch_dir, 'bag_nav2_navigation.launch.py'),
            ),
            launch_arguments={
                'namespace': namespace,
                'params_file': nav2_params_file,
                'use_sim_time': use_sim_time,
                'autostart': autostart,
                'use_respawn': use_respawn,
                'use_composition': use_composition,
                'log_level': log_level,
            }.items(),
        ),
    ])
