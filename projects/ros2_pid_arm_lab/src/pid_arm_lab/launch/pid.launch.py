import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


PACKAGE_NAME = 'pid_arm_lab'


def launch_setup(context, *args, **kwargs):
    pkg_share = get_package_share_directory(PACKAGE_NAME)
    pid_params_file = LaunchConfiguration('pid_params_file').perform(context)
    if not pid_params_file:
        pid_params_file = os.path.join(pkg_share, 'config', 'pid_params.yaml')

    node = Node(
        package=PACKAGE_NAME,
        executable='pid_arm_controller',
        name=LaunchConfiguration('pid_node_name'),
        output='screen',
        parameters=[
            pid_params_file,
            {
                'kp': LaunchConfiguration('kp'),
                'ki': LaunchConfiguration('ki'),
                'kd': LaunchConfiguration('kd'),
                'setpoint': LaunchConfiguration('setpoint'),
                'dt': LaunchConfiguration('dt'),
                'max_effort': LaunchConfiguration('max_effort'),
                'integral_limit': LaunchConfiguration('integral_limit'),
                'gravity_gain': LaunchConfiguration('gravity_gain'),
                'joint_name': LaunchConfiguration('joint_name'),
                'joint_states_topic': LaunchConfiguration('joint_states_topic'),
                'command_topic': LaunchConfiguration('command_topic'),
            },
        ],
    )

    return [node]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('pid_node_name', default_value='pid_arm_controller'),
        DeclareLaunchArgument('pid_params_file', default_value=''),
        DeclareLaunchArgument('kp', default_value='0.0'),
        DeclareLaunchArgument('ki', default_value='0.0'),
        DeclareLaunchArgument('kd', default_value='0.0'),
        DeclareLaunchArgument('setpoint', default_value='0.0'),
        DeclareLaunchArgument('dt', default_value='0.01'),
        DeclareLaunchArgument('max_effort', default_value='50.0'),
        DeclareLaunchArgument('integral_limit', default_value='10.0'),
        DeclareLaunchArgument('gravity_gain', default_value='0.0'),
        DeclareLaunchArgument('joint_name', default_value='arm_joint'),
        DeclareLaunchArgument('joint_states_topic', default_value='/joint_states'),
        DeclareLaunchArgument('command_topic', default_value='/effort_controller/commands'),
        OpaqueFunction(function=launch_setup),
    ])
