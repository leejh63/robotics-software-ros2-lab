from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def _topic(namespace, name):
    return f'/{namespace}/{name}'


def _launch_setup(context, *args, **kwargs):
    namespace = LaunchConfiguration('namespace').perform(context).strip('/')
    if not namespace:
        raise ValueError('namespace launch argument must not be empty.')

    state_topic = LaunchConfiguration('state_topic').perform(context).strip()
    if not state_topic:
        state_topic = _topic(namespace, 'virtual_monster_states')

    clear_service_name = LaunchConfiguration('clear_service_name').perform(context).strip()
    if not clear_service_name:
        clear_service_name = _topic(namespace, 'clear_nearest_virtual_obstacle')

    navigate_action_name = LaunchConfiguration('navigate_action_name').perform(context).strip()
    if not navigate_action_name:
        navigate_action_name = _topic(namespace, 'navigate_to_pose')

    return [
        Node(
            package='lee_robot_description',
            executable='monster_hunter_node.py',
            name='monster_hunter_node',
            output='screen',
            parameters=[
                {
                    'state_topic': state_topic,
                    'clear_service_name': clear_service_name,
                    'navigate_action_name': navigate_action_name,
                    'map_frame': LaunchConfiguration('map_frame'),
                    'robot_frame': LaunchConfiguration('robot_frame'),
                    'approach_distance': ParameterValue(LaunchConfiguration('approach_distance'), value_type=float),
                    'clear_distance': ParameterValue(LaunchConfiguration('clear_distance'), value_type=float),
                    'target_kill_count': ParameterValue(LaunchConfiguration('target_kill_count'), value_type=int),
                    'update_rate': ParameterValue(LaunchConfiguration('update_rate'), value_type=float),
                    'autostart': ParameterValue(LaunchConfiguration('autostart'), value_type=bool),
                    'use_sim_time': ParameterValue(LaunchConfiguration('use_sim_time'), value_type=bool),
                },
            ],
            remappings=[
                ('/tf', _topic(namespace, 'tf')),
                ('/tf_static', _topic(namespace, 'tf_static')),
            ],
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
            'state_topic',
            default_value='',
            description='Monster state JSON topic. Empty value uses /<namespace>/virtual_monster_states.',
        ),
        DeclareLaunchArgument(
            'clear_service_name',
            default_value='',
            description='Clear service. Empty value uses /<namespace>/clear_nearest_virtual_obstacle.',
        ),
        DeclareLaunchArgument(
            'navigate_action_name',
            default_value='',
            description='Nav2 NavigateToPose action. Empty value uses /<namespace>/navigate_to_pose.',
        ),
        DeclareLaunchArgument(
            'map_frame',
            default_value='map_lee',
            description='Map frame used by the monster state and Nav2 goals.',
        ),
        DeclareLaunchArgument(
            'robot_frame',
            default_value='base_scan',
            description='Robot frame used for selecting the nearest monster.',
        ),
        DeclareLaunchArgument(
            'approach_distance',
            default_value='0.65',
            description='Goal distance to keep from the monster center.',
        ),
        DeclareLaunchArgument(
            'clear_distance',
            default_value='0.75',
            description='Distance at which the hunter tries the clear service directly.',
        ),
        DeclareLaunchArgument(
            'target_kill_count',
            default_value='1',
            description='Number of monsters to clear in this Stage 3 test node.',
        ),
        DeclareLaunchArgument(
            'update_rate',
            default_value='2.0',
            description='Hunter decision loop rate.',
        ),
        DeclareLaunchArgument(
            'autostart',
            default_value='true',
            description='Start hunting as soon as state, TF, and Nav2 are available.',
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use Gazebo simulation clock.',
        ),
        OpaqueFunction(function=_launch_setup),
    ])
