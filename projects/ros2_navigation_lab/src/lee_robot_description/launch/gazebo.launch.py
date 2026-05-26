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

    xacro_file = os.path.join(pkg_dir, 'urdf', 'turtlebot.xacro')
    use_sim_time = LaunchConfiguration('use_sim_time')
    world = LaunchConfiguration('world')
    use_rviz = LaunchConfiguration('use_rviz')
    use_avoidance = LaunchConfiguration('use_avoidance')
    spawn_z = LaunchConfiguration('spawn_z')

    world_file = PathJoinSubstitution([pkg_dir, 'worlds', world])
    rviz_file = os.path.join(pkg_dir, 'rviz', 'turtlebot.rviz')

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
            'use_avoidance',
            default_value='false',
            description='Start LiDAR obstacle avoidance cmd_vel publisher.',
        ),
        DeclareLaunchArgument(
            'spawn_z',
            default_value='0.1',
            description='Initial z height for spawning turtlebot in Gazebo.',
        ),

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
                'turtlebot_lee',
                '-z',
                spawn_z,
            ],
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

        Node(
            package='lee_robot_description',
            executable='lidar_wall_follower.py',
            name='lee_lidar_wall_follower',
            output='screen',
            condition=IfCondition(use_avoidance),
            parameters=[{
                'scan_topic': '/lee/scan',
                'cmd_vel_topic': '/lee/cmd_vel',
                'obstacle_distance': 0.55,
                'front_angle_deg': 25.0,
                'forward_speed': 0.16,
                'turn_speed': 0.45,
                'turn_direction': 'right',
            }],
        ),
    ])
