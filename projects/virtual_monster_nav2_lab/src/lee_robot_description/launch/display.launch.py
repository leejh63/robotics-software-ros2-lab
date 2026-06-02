import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, FindExecutable, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def _topic(namespace, name):
    return f'/{namespace}/{name}'


def _launch_setup(context, *args, **kwargs):
    pkg_dir = get_package_share_directory('lee_robot_description')
    namespace = LaunchConfiguration('namespace').perform(context).strip('/')
    odom_frame = LaunchConfiguration('odom_frame').perform(context)
    if not namespace:
        raise ValueError('namespace launch argument must not be empty.')

    xacro_file = os.path.join(pkg_dir, 'urdf', 'turtlebot.xacro')
    rviz_config_file = os.path.join(pkg_dir, 'rviz', 'turtlebot.rviz')
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')
    use_joint_state_gui = LaunchConfiguration('use_joint_state_gui')

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

    isolated_remappings = [
        ('/tf', _topic(namespace, 'tf')),
        ('/tf_static', _topic(namespace, 'tf_static')),
        ('/robot_description', _topic(namespace, 'robot_description')),
    ]

    return [
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
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen',
            condition=IfCondition(use_joint_state_gui),
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': use_sim_time,
            }],
            remappings=[
                ('/joint_states', _topic(namespace, 'joint_states')),
                ('/robot_description', _topic(namespace, 'robot_description')),
            ],
        ),

        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            output='screen',
            condition=UnlessCondition(use_joint_state_gui),
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': use_sim_time,
            }],
            remappings=[
                ('/joint_states', _topic(namespace, 'joint_states')),
                ('/robot_description', _topic(namespace, 'robot_description')),
            ],
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz',
            output='screen',
            condition=IfCondition(use_rviz),
            arguments=['-d', rviz_config_file],
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
            'odom_frame',
            default_value='odom_lee',
            description='Odometry frame passed to the Gazebo xacro plugins.',
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation clock if true.',
        ),
        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            description='Start RViz2.',
        ),
        DeclareLaunchArgument(
            'use_joint_state_gui',
            default_value='true',
            description='Use joint_state_publisher_gui instead of the non-GUI publisher.',
        ),
        OpaqueFunction(function=_launch_setup),
    ])
