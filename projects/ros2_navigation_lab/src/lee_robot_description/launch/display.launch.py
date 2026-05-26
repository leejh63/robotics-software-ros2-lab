from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = FindPackageShare('lee_robot_description')

    xacro_file = PathJoinSubstitution([
        pkg_share,
        'urdf',
        'turtlebot.xacro',
    ])

    rviz_config_file = PathJoinSubstitution([
        pkg_share,
        'rviz',
        'turtlebot.rviz',
    ])

    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')
    use_joint_state_gui = LaunchConfiguration('use_joint_state_gui')

    robot_description = ParameterValue(
        Command([
            FindExecutable(name='xacro'),
            ' ',
            xacro_file,
        ]),
        value_type=str,
    )

    isolated_remappings = [
        ('/tf', '/lee/tf'),
        ('/tf_static', '/lee/tf_static'),
        ('/robot_description', '/lee/robot_description'),
    ]

    return LaunchDescription([
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
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='lee_joint_state_publisher_gui',
            output='screen',
            condition=IfCondition(use_joint_state_gui),
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': use_sim_time,
            }],
            remappings=[
                ('/joint_states', '/lee/joint_states'),
                ('/robot_description', '/lee/robot_description'),
            ],
        ),

        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='lee_joint_state_publisher',
            output='screen',
            condition=UnlessCondition(use_joint_state_gui),
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': use_sim_time,
            }],
            remappings=[
                ('/joint_states', '/lee/joint_states'),
                ('/robot_description', '/lee/robot_description'),
            ],
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            name='lee_rviz',
            output='screen',
            condition=IfCondition(use_rviz),
            arguments=['-d', rviz_config_file],
            parameters=[{
                'use_sim_time': use_sim_time,
            }],
            remappings=isolated_remappings,
        ),
    ])
