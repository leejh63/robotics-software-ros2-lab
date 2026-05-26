import os
from xml.dom import Node as DomNode

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


PACKAGE_NAME = 'pid_arm_lab'


def remove_xml_comments(node):
    for child in list(node.childNodes):
        if child.nodeType == DomNode.COMMENT_NODE:
            node.removeChild(child)
        else:
            remove_xml_comments(child)


def launch_setup(context, *args, **kwargs):
    pkg_share = get_package_share_directory(PACKAGE_NAME)

    xacro_file = LaunchConfiguration('xacro_file').perform(context)
    controller_config = LaunchConfiguration('controller_config').perform(context)
    world_file = LaunchConfiguration('world_file').perform(context)

    if not xacro_file:
        xacro_file = os.path.join(pkg_share, 'urdf', 'one_dof_arm.xacro')
    if not controller_config:
        controller_config = os.path.join(pkg_share, 'config', 'ros2_controllers.yaml')
    if not world_file:
        world_file = os.path.join(pkg_share, 'worlds', 'empty.world')

    robot_description_doc = xacro.process_file(
        xacro_file,
        mappings={
            'robot_name': LaunchConfiguration('robot_name').perform(context),
            'joint_name': LaunchConfiguration('joint_name').perform(context),
            'payload_mass': LaunchConfiguration('payload_mass').perform(context),
            'controller_config': controller_config,
        },
    )
    remove_xml_comments(robot_description_doc)
    robot_description = ParameterValue(
        robot_description_doc.documentElement.toxml(),
        value_type=str,
    )

    gazebo_cmd = [
        'gazebo',
        '--verbose',
        world_file,
        '-s', 'libgazebo_ros_init.so',
        '-s', 'libgazebo_ros_factory.so',
    ]

    gazebo = ExecuteProcess(cmd=gazebo_cmd, output='screen')

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }],
        output='screen',
    )

    spawn = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', LaunchConfiguration('robot_description_topic'),
            '-entity', LaunchConfiguration('entity_name'),
            '-z', LaunchConfiguration('start_z'),
        ],
        output='screen',
    )

    load_joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '-c', LaunchConfiguration('controller_manager_name'),
        ],
        output='screen',
    )

    load_effort_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            LaunchConfiguration('effort_controller_name'),
            '-c', LaunchConfiguration('controller_manager_name'),
        ],
        output='screen',
    )

    return [
        gazebo,
        robot_state_publisher,
        spawn,
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=spawn,
                on_exit=[load_joint_state_broadcaster],
            )
        ),
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=load_joint_state_broadcaster,
                on_exit=[load_effort_controller],
            )
        ),
    ]


def generate_launch_description():
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
        OpaqueFunction(function=launch_setup),
    ])
