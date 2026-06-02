import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import Command, FindExecutable, LaunchConfiguration
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

    xacro_file = os.path.join(pkg_dir, 'urdf', 'turtlebot.xacro')
    world_file = os.path.join(pkg_dir, 'worlds', world_name)
    rviz_file = os.path.join(pkg_dir, 'rviz', 'slam.rviz')
    slam_params_file = os.path.join(pkg_dir, 'config', 'slam_param.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')
    use_slam = LaunchConfiguration('use_slam')
    spawn_z = LaunchConfiguration('spawn_z')

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
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            condition=IfCondition(use_slam),
            parameters=[
                slam_params_file,
                {
                    'use_sim_time': use_sim_time,
                    'map_frame': map_frame,
                    'odom_frame': odom_frame,
                    'scan_topic': _topic(namespace, 'scan'),
                },
            ],
            remappings=[
                ('/scan', _topic(namespace, 'scan')),
                ('/map', _topic(namespace, 'map')),
                ('/map_updates', _topic(namespace, 'map_updates')),
                ('/tf', _topic(namespace, 'tf')),
                ('/tf_static', _topic(namespace, 'tf_static')),
            ],
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
    return LaunchDescription([
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
            'use_sim_time',
            default_value='true',
            description='Use Gazebo simulation clock.',
        ),
        DeclareLaunchArgument(
            'world',
            default_value='slam.world',
            description='Gazebo world file name under lee_robot_description/worlds. Default matches maps/slam_map.yaml.',
        ),
        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            description='Start RViz2 with the TurtleBot display config.',
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
        OpaqueFunction(function=_launch_setup),
    ])
