import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetLaunchConfiguration
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_dir = get_package_share_directory('lee_robot_description')
    launch_dir = os.path.join(pkg_dir, 'launch')
    default_map_yaml = os.path.join(pkg_dir, 'maps', 'slam_map.yaml')
    default_params_file = os.path.join(pkg_dir, 'config', 'nav2_params.yaml')
    default_virtual_params_file = os.path.join(pkg_dir, 'config', 'nav2_params_virtual_obstacles.yaml')
    default_virtual_obstacles_config = os.path.join(pkg_dir, 'config', 'virtual_obstacles.yaml')

    namespace = LaunchConfiguration('namespace')
    map_frame = LaunchConfiguration('map_frame')
    odom_frame = LaunchConfiguration('odom_frame')
    entity_name = LaunchConfiguration('entity_name')
    world = LaunchConfiguration('world')
    map_yaml = LaunchConfiguration('map_yaml')
    params_file = LaunchConfiguration('params_file')
    selected_params_file = LaunchConfiguration('selected_params_file')
    virtual_params_file = LaunchConfiguration('virtual_params_file')
    virtual_obstacles_config = LaunchConfiguration('virtual_obstacles_config')
    clear_service_name = LaunchConfiguration('clear_service_name')
    reset_service_name = LaunchConfiguration('reset_service_name')
    state_topic = LaunchConfiguration('state_topic')
    monster_count = LaunchConfiguration('monster_count')
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')
    use_virtual_obstacles = LaunchConfiguration('use_virtual_obstacles')
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
            'virtual_params_file',
            default_value=default_virtual_params_file,
            description='Nav2 params file used when use_virtual_obstacles is true.',
        ),
        DeclareLaunchArgument(
            'virtual_obstacles_config',
            default_value=default_virtual_obstacles_config,
            description='YAML scenario for virtual dynamic obstacles.',
        ),
        DeclareLaunchArgument(
            'clear_service_name',
            default_value='',
            description='Virtual obstacle clear service name. Empty value uses /<namespace>/clear_nearest_virtual_obstacle.',
        ),
        DeclareLaunchArgument(
            'reset_service_name',
            default_value='',
            description='Virtual obstacle reset service name. Empty value uses /<namespace>/reset_virtual_obstacles.',
        ),
        DeclareLaunchArgument(
            'state_topic',
            default_value='',
            description='Virtual monster state topic. Empty value uses /<namespace>/virtual_monster_states.',
        ),
        DeclareLaunchArgument(
            'monster_count',
            default_value='-1',
            description='Override random_spawn.target_count. -1 uses the YAML value.',
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
            'use_virtual_obstacles',
            default_value='false',
            description='Start virtual dynamic obstacles and use the matching local costmap params.',
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
        SetLaunchConfiguration(
            'selected_params_file',
            params_file,
            condition=UnlessCondition(use_virtual_obstacles),
        ),
        SetLaunchConfiguration(
            'selected_params_file',
            virtual_params_file,
            condition=IfCondition(use_virtual_obstacles),
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
                os.path.join(launch_dir, 'virtual_dynamic_obstacles.launch.py'),
            ),
            condition=IfCondition(use_virtual_obstacles),
            launch_arguments={
                'namespace': namespace,
                'config_file': virtual_obstacles_config,
                'obstacle_frame': map_frame,
                'scan_frame': 'base_scan',
                'clear_service_name': clear_service_name,
                'reset_service_name': reset_service_name,
                'state_topic': state_topic,
                'monster_count': monster_count,
                'use_sim_time': use_sim_time,
            }.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(launch_dir, 'nav2_navigation.launch.py'),
            ),
            launch_arguments={
                'namespace': namespace,
                'params_file': selected_params_file,
                'use_sim_time': use_sim_time,
                'autostart': autostart,
                'use_respawn': use_respawn,
                'use_composition': use_composition,
                'log_level': log_level,
            }.items(),
        ),
    ])
