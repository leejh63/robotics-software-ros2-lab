import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def _topic(namespace, name):
    return f'/{namespace}/{name}'


def _launch_setup(context, *args, **kwargs):
    pkg_dir = get_package_share_directory('lee_robot_description')
    namespace = LaunchConfiguration('namespace').perform(context).strip('/')
    map_frame = LaunchConfiguration('map_frame').perform(context)
    odom_frame = LaunchConfiguration('odom_frame').perform(context)
    entity_name = LaunchConfiguration('entity_name').perform(context)
    world_name = LaunchConfiguration('world').perform(context)
    if not namespace:
        raise ValueError('namespace launch argument must not be empty.')

    map_yaml = LaunchConfiguration('map_yaml')
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')
    spawn_z = LaunchConfiguration('spawn_z')

    xacro_file = os.path.join(pkg_dir, 'urdf', 'turtlebot.xacro')
    world_file = os.path.join(pkg_dir, 'worlds', world_name)
    rviz_file = os.path.join(pkg_dir, 'rviz', 'amcl.rviz')
    amcl_params_file = os.path.join(pkg_dir, 'config', 'amcl_param.yaml')

    robot_description = ParameterValue(
        Command([
            FindExecutable(name='xacro'),
            ' ',
            xacro_file,
            ' ',
            'namespace:=',
            namespace,
            ' ',
            'odom_frame:=',
            odom_frame,
        ]),
        value_type=str,
    )

    rviz_args = ['-d', rviz_file] if os.path.exists(rviz_file) else []

    isolated_remappings = [
        ('/robot_description', _topic(namespace, 'robot_description')),
        ('/tf', _topic(namespace, 'tf')),
        ('/tf_static', _topic(namespace, 'tf_static')),
    ]

    return [
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
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': use_sim_time,
            }],
            remappings=[
                *isolated_remappings,
                ('/joint_states', _topic(namespace, 'joint_states')),
            ],
        ),

        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            name='spawn_turtlebot',
            output='screen',
            arguments=[
                '-topic',
                _topic(namespace, 'robot_description'),
                '-entity',
                entity_name,
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
                'frame_id': map_frame,
            }],
            remappings=[
                ('/map', _topic(namespace, 'map')),
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
                    'global_frame_id': map_frame,
                    'odom_frame_id': odom_frame,
                    'scan_topic': _topic(namespace, 'scan'),
                },
            ],
            remappings=[
                ('/map', _topic(namespace, 'map')),
                ('/tf', _topic(namespace, 'tf')),
                ('/tf_static', _topic(namespace, 'tf_static')),
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
            name='rviz',
            output='screen',
            condition=IfCondition(use_rviz),
            arguments=rviz_args,
            parameters=[{
                'use_sim_time': use_sim_time,
            }],
            remappings=isolated_remappings,
        ),
    ]


def generate_launch_description():
    pkg_dir = get_package_share_directory('lee_robot_description')
    default_map_yaml = os.path.join(pkg_dir, 'maps', 'slam_map.yaml')

    declare_use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use Gazebo simulation clock.',
    )
    declare_namespace_arg = DeclareLaunchArgument(
        'namespace',
        default_value='lee',
        description='Robot namespace without a leading slash.',
    )
    declare_map_frame_arg = DeclareLaunchArgument(
        'map_frame',
        default_value='map_lee',
        description='Map frame used by map_server and AMCL.',
    )
    declare_odom_frame_arg = DeclareLaunchArgument(
        'odom_frame',
        default_value='odom_lee',
        description='Odometry frame used by AMCL and the Gazebo xacro plugins.',
    )
    declare_entity_arg = DeclareLaunchArgument(
        'entity_name',
        default_value='turtlebot',
        description='Gazebo entity name used by spawn_entity.py.',
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

    return LaunchDescription([
        declare_namespace_arg,
        declare_map_frame_arg,
        declare_odom_frame_arg,
        declare_entity_arg,
        declare_use_sim_time_arg,
        declare_world_arg,
        declare_map_arg,
        declare_use_rviz_arg,
        declare_spawn_z_arg,
        OpaqueFunction(function=_launch_setup),
    ])
