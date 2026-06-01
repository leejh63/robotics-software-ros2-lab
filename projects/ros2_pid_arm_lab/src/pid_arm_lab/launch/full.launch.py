import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


PACKAGE_NAME = 'pid_arm_lab'


def generate_launch_description():
    pkg_share = get_package_share_directory(PACKAGE_NAME)

    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_share, 'launch', 'sim.launch.py')),
        launch_arguments={
            'robot_name': LaunchConfiguration('robot_name'),
            'entity_name': LaunchConfiguration('entity_name'),
            'joint_name': LaunchConfiguration('joint_name'),
            'payload_mass': LaunchConfiguration('payload_mass'),
            'start_z': LaunchConfiguration('start_z'),
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'xacro_file': LaunchConfiguration('xacro_file'),
            'controller_config': LaunchConfiguration('controller_config'),
            'world_file': LaunchConfiguration('world_file'),
            'robot_description_topic': LaunchConfiguration('robot_description_topic'),
            'controller_manager_name': LaunchConfiguration('controller_manager_name'),
            'effort_controller_name': LaunchConfiguration('effort_controller_name'),
        }.items(),
    )

    pid_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_share, 'launch', 'pid.launch.py')),
        launch_arguments={
            'pid_node_name': LaunchConfiguration('pid_node_name'),
            'pid_params_file': LaunchConfiguration('pid_params_file'),
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
        }.items(),
    )

    return LaunchDescription([
        DeclareLaunchArgument('robot_name', default_value='one_dof_arm'),
        DeclareLaunchArgument('entity_name', default_value='one_dof_arm'),
        DeclareLaunchArgument('joint_name', default_value='arm_joint'),
        DeclareLaunchArgument('payload_mass', default_value='1.0'),
        DeclareLaunchArgument('start_z', default_value='1.0'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('xacro_file', default_value=''),
        DeclareLaunchArgument('controller_config', default_value=''),
        DeclareLaunchArgument('world_file', default_value=''),
        DeclareLaunchArgument('robot_description_topic', default_value='/robot_description'),
        DeclareLaunchArgument('controller_manager_name', default_value='/controller_manager'),
        DeclareLaunchArgument('effort_controller_name', default_value='effort_controller'),
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
        DeclareLaunchArgument('use_actual_dt', default_value='true'),
        DeclareLaunchArgument('reset_integral_on_setpoint_change', default_value='true'),
        DeclareLaunchArgument('joint_states_topic', default_value='/joint_states'),
        DeclareLaunchArgument('command_topic', default_value='/effort_controller/commands'),
        sim_launch,
        pid_launch,
    ])
