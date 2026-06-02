import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def _topic(namespace, name):
    return f'/{namespace}/{name}'


def _launch_setup(context, *args, **kwargs):
    pkg_dir = get_package_share_directory('lee_robot_description')
    namespace = LaunchConfiguration('namespace').perform(context).strip('/')
    if not namespace:
        raise ValueError('namespace launch argument must not be empty.')

    config_file = LaunchConfiguration('config_file')
    obstacle_frame = LaunchConfiguration('obstacle_frame')
    scan_frame = LaunchConfiguration('scan_frame')
    use_sim_time = LaunchConfiguration('use_sim_time')
    clear_service_name = LaunchConfiguration('clear_service_name').perform(context).strip()
    if not clear_service_name:
        clear_service_name = _topic(namespace, 'clear_nearest_virtual_obstacle')

    reset_service_name = LaunchConfiguration('reset_service_name').perform(context).strip()
    if not reset_service_name:
        reset_service_name = _topic(namespace, 'reset_virtual_obstacles')

    state_topic = LaunchConfiguration('state_topic').perform(context).strip()
    if not state_topic:
        state_topic = _topic(namespace, 'virtual_monster_states')

    monster_count = LaunchConfiguration('monster_count')
    attack_range = LaunchConfiguration('attack_range')
    attack_fov_deg = LaunchConfiguration('attack_fov_deg')
    attack_cooldown = LaunchConfiguration('attack_cooldown')

    return [
        Node(
            package='lee_robot_description',
            executable='virtual_dynamic_obstacles.py',
            name='virtual_dynamic_obstacles',
            output='screen',
            parameters=[
                {
                    'config_file': config_file,
                    'obstacle_frame': obstacle_frame,
                    'scan_frame': scan_frame,
                    'scan_topic': _topic(namespace, 'virtual_scan'),
                    'marker_topic': _topic(namespace, 'virtual_obstacle_markers'),
                    'state_topic': state_topic,
                    'clear_service_name': clear_service_name,
                    'reset_service_name': reset_service_name,
                    'target_count': ParameterValue(monster_count, value_type=int),
                    'attack_range': ParameterValue(attack_range, value_type=float),
                    'attack_fov_deg': ParameterValue(attack_fov_deg, value_type=float),
                    'attack_cooldown': ParameterValue(attack_cooldown, value_type=float),
                    'use_sim_time': use_sim_time,
                },
            ],
            remappings=[
                ('/tf', _topic(namespace, 'tf')),
                ('/tf_static', _topic(namespace, 'tf_static')),
            ],
        ),
    ]


def generate_launch_description():
    pkg_dir = get_package_share_directory('lee_robot_description')
    default_config_file = os.path.join(pkg_dir, 'config', 'virtual_obstacles.yaml')

    return LaunchDescription([
        DeclareLaunchArgument(
            'namespace',
            default_value='lee',
            description='Robot namespace without a leading slash.',
        ),
        DeclareLaunchArgument(
            'config_file',
            default_value=default_config_file,
            description='YAML scenario for virtual dynamic obstacles.',
        ),
        DeclareLaunchArgument(
            'obstacle_frame',
            default_value='map_lee',
            description='Frame used by virtual obstacle waypoints. Random spawn mode should use the map frame.',
        ),
        DeclareLaunchArgument(
            'scan_frame',
            default_value='base_scan',
            description='Frame id used in the virtual LaserScan.',
        ),
        DeclareLaunchArgument(
            'clear_service_name',
            default_value='',
            description='Service used to clear the nearest virtual obstacle. Empty value uses /<namespace>/clear_nearest_virtual_obstacle.',
        ),
        DeclareLaunchArgument(
            'reset_service_name',
            default_value='',
            description='Service used to reset random virtual obstacles. Empty value uses /<namespace>/reset_virtual_obstacles.',
        ),
        DeclareLaunchArgument(
            'state_topic',
            default_value='',
            description='Topic used to publish virtual monster state JSON. Empty value uses /<namespace>/virtual_monster_states.',
        ),
        DeclareLaunchArgument(
            'monster_count',
            default_value='-1',
            description='Override random_spawn.target_count. -1 uses the YAML value.',
        ),
        DeclareLaunchArgument(
            'attack_range',
            default_value='-1.0',
            description='Override clear_rule.attack_range in meters. -1 uses the YAML value.',
        ),
        DeclareLaunchArgument(
            'attack_fov_deg',
            default_value='-1.0',
            description='Override clear_rule.attack_fov_deg. -1 uses the YAML value.',
        ),
        DeclareLaunchArgument(
            'attack_cooldown',
            default_value='-1.0',
            description='Override clear_rule.attack_cooldown in seconds. -1 uses the YAML value.',
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use Gazebo simulation clock.',
        ),
        OpaqueFunction(function=_launch_setup),
    ])
