import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_dir = get_package_share_directory('lee_robot_description')
    default_map_yaml = os.path.join(pkg_dir, 'maps', 'slam_map.yaml')

    world = LaunchConfiguration('world')
    map_yaml = LaunchConfiguration('map_yaml')
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')
    spawn_z = LaunchConfiguration('spawn_z')

    declare_use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use Gazebo simulation clock.',
    )
    declare_world_arg = DeclareLaunchArgument(
        'world',
        default_value='slam.world',
        description='Gazebo world file name under lee_robot_description/worlds.',
    )
    declare_map_arg = DeclareLaunchArgument(
        'map_yaml',
        default_value=default_map_yaml,
        description='Map yaml file path loaded by nav2_map_server.',
    )
    declare_use_rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Start RViz2 with the AMCL display config.',
    )
    declare_spawn_z_arg = DeclareLaunchArgument(
        'spawn_z',
        default_value='0.3',
        description='Initial z height for spawning turtlebot in Gazebo.',
    )

    xacro_file = os.path.join(pkg_dir, 'urdf', 'turtlebot.xacro')
    world_file = PathJoinSubstitution([pkg_dir, 'worlds', world])
    rviz_file = os.path.join(pkg_dir, 'rviz', 'amcl.rviz')
    amcl_params_file = os.path.join(pkg_dir, 'config', 'amcl_param.yaml')

    robot_description = ParameterValue(
        Command([
            FindExecutable(name='xacro'),
            ' ',
            xacro_file,
        ]),
        value_type=str,
    )

    rviz_args = ['-d', rviz_file] if os.path.exists(rviz_file) else []

    isolated_remappings = [
        ('/robot_description', '/lee/robot_description'),
        ('/tf', '/lee/tf'),
        ('/tf_static', '/lee/tf_static'),
    ]

    return LaunchDescription([
        declare_use_sim_time_arg,
        declare_world_arg,
        declare_map_arg,
        declare_use_rviz_arg,
        declare_spawn_z_arg,

        ExecuteProcess(
            cmd=[
                'gazebo',
                '--verbose',
                world_file,
                '-s',
                'libgazebo_ros_init.so',
                '-s',
                'libgazebo_ros_factory.so',
            ],
            output='screen',
        ),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='lee_robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': use_sim_time,
            }],
            remappings=[
                *isolated_remappings,
                ('/joint_states', '/lee/joint_states'),
            ],
        ),

        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            name='lee_spawn_turtlebot',
            output='screen',
            arguments=[
                '-topic',
                '/lee/robot_description',
                '-entity',
                'turtlebot',
                '-z',
                spawn_z,
            ],
        ),

        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[{
                'yaml_filename': map_yaml,
                'use_sim_time': use_sim_time,
                'frame_id': 'map_lee',
            }],
            remappings=[
                ('/map', '/lee/map'),
            ],
        ),

        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[
                amcl_params_file,
                {
                    'use_sim_time': use_sim_time,
                },
            ],
            remappings=[
                ('/map', '/lee/map'),
                ('/tf', '/lee/tf'),
                ('/tf_static', '/lee/tf_static'),
            ],
        ),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_localization',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'autostart': True,
                'node_names': ['map_server', 'amcl'],
            }],
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            name='lee_rviz',
            output='screen',
            condition=IfCondition(use_rviz),
            arguments=rviz_args,
            parameters=[{
                'use_sim_time': use_sim_time,
            }],
            remappings=isolated_remappings,
        ),
    ])
