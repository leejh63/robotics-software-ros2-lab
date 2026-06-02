from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory

import os


def _topic(namespace, name):
    return f'/{namespace}/{name}'


def _launch_setup(context, *args, **kwargs):
    namespace = LaunchConfiguration('namespace').perform(context).strip('/')
    if not namespace:
        raise ValueError('namespace launch argument must not be empty.')

    package_share = get_package_share_directory('lee_robot_description')
    config_file = LaunchConfiguration('config_file').perform(context).strip()
    if not config_file:
        config_file = os.path.join(package_share, 'config', 'monster_mission.yaml')

    candidate_topic = LaunchConfiguration('candidate_topic').perform(context).strip()
    if not candidate_topic:
        candidate_topic = _topic(namespace, 'detected_monster_candidates')

    mission_status_topic = LaunchConfiguration('mission_status_topic').perform(context).strip()
    if not mission_status_topic:
        mission_status_topic = _topic(namespace, 'monster_mission_status')

    patrol_marker_topic = LaunchConfiguration('patrol_marker_topic').perform(context).strip()
    if not patrol_marker_topic:
        patrol_marker_topic = _topic(namespace, 'patrol_waypoint_markers')

    clear_service_name = LaunchConfiguration('clear_service_name').perform(context).strip()
    if not clear_service_name:
        clear_service_name = _topic(namespace, 'clear_nearest_virtual_obstacle')

    navigate_action_name = LaunchConfiguration('navigate_action_name').perform(context).strip()
    if not navigate_action_name:
        navigate_action_name = _topic(namespace, 'navigate_to_pose')

    scan_topic = LaunchConfiguration('scan_topic').perform(context).strip()
    if not scan_topic:
        scan_topic = _topic(namespace, 'virtual_scan')

    common_overrides = {
        'use_sim_time': ParameterValue(LaunchConfiguration('use_sim_time'), value_type=bool),
        'map_frame': LaunchConfiguration('map_frame'),
        'scan_frame': LaunchConfiguration('scan_frame'),
    }

    return [
        Node(
            package='lee_robot_description',
            executable='monster_detector_node.py',
            name='monster_detector_node',
            output='screen',
            parameters=[
                config_file,
                common_overrides,
                {
                    'scan_topic': scan_topic,
                    'candidate_topic': candidate_topic,
                    'map_yaml': LaunchConfiguration('map_yaml'),
                    'max_range': ParameterValue(LaunchConfiguration('detection_max_range'), value_type=float),
                    'detection_fov_deg': ParameterValue(LaunchConfiguration('detection_fov_deg'), value_type=float),
                    'cluster_distance': ParameterValue(LaunchConfiguration('cluster_distance'), value_type=float),
                    'min_cluster_points': ParameterValue(LaunchConfiguration('min_cluster_points'), value_type=int),
                },
            ],
            remappings=[
                ('/tf', _topic(namespace, 'tf')),
                ('/tf_static', _topic(namespace, 'tf_static')),
            ],
        ),
        Node(
            package='lee_robot_description',
            executable='monster_mission_node.py',
            name='monster_mission_node',
            output='screen',
            parameters=[
                config_file,
                common_overrides,
                {
                    'candidate_topic': candidate_topic,
                    'mission_status_topic': mission_status_topic,
                    'patrol_marker_topic': patrol_marker_topic,
                    'robot_frame': LaunchConfiguration('scan_frame'),
                    'clear_service_name': clear_service_name,
                    'navigate_action_name': navigate_action_name,
                    'target_kill_count': ParameterValue(LaunchConfiguration('target_kill_count'), value_type=int),
                    'search_waypoints': LaunchConfiguration('search_waypoints'),
                    'exit_pose': LaunchConfiguration('exit_pose'),
                    'autostart': ParameterValue(LaunchConfiguration('autostart'), value_type=bool),
                    'max_candidate_distance': ParameterValue(LaunchConfiguration('max_candidate_distance'), value_type=float),
                    'approach_distance': ParameterValue(LaunchConfiguration('approach_distance'), value_type=float),
                    'clear_distance': ParameterValue(LaunchConfiguration('clear_distance'), value_type=float),
                    'candidate_center_offset': ParameterValue(LaunchConfiguration('candidate_center_offset'), value_type=float),
                    'max_clear_attempts': ParameterValue(LaunchConfiguration('max_clear_attempts'), value_type=int),
                    'clear_retry_delay_sec': ParameterValue(LaunchConfiguration('clear_retry_delay_sec'), value_type=float),
                    'patrol_mode': LaunchConfiguration('patrol_mode'),
                    'map_yaml': LaunchConfiguration('map_yaml'),
                    'patrol_grid_spacing': ParameterValue(LaunchConfiguration('patrol_grid_spacing'), value_type=float),
                    'patrol_wall_clearance': ParameterValue(LaunchConfiguration('patrol_wall_clearance'), value_type=float),
                    'patrol_max_waypoints': ParameterValue(LaunchConfiguration('patrol_max_waypoints'), value_type=int),
                    'patrol_start_nearest': ParameterValue(LaunchConfiguration('patrol_start_nearest'), value_type=bool),
                    'patrol_unknown_is_blocked': ParameterValue(LaunchConfiguration('patrol_unknown_is_blocked'), value_type=bool),
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
            'config_file',
            default_value='',
            description='Stage 4 mission YAML. Empty value uses config/monster_mission.yaml.',
        ),
        DeclareLaunchArgument(
            'scan_topic',
            default_value='',
            description='Scan topic used by detector. Empty value uses /<namespace>/virtual_scan.',
        ),
        DeclareLaunchArgument(
            'candidate_topic',
            default_value='',
            description='Detector output topic. Empty value uses /<namespace>/detected_monster_candidates.',
        ),
        DeclareLaunchArgument(
            'mission_status_topic',
            default_value='',
            description='Mission status JSON topic. Empty value uses /<namespace>/monster_mission_status.',
        ),
        DeclareLaunchArgument(
            'patrol_marker_topic',
            default_value='',
            description='Patrol waypoint MarkerArray topic. Empty value uses /<namespace>/patrol_waypoint_markers.',
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
            description='Map frame used by detector and mission goals.',
        ),
        DeclareLaunchArgument(
            'scan_frame',
            default_value='base_scan',
            description='Robot scan frame.',
        ),
        DeclareLaunchArgument(
            'map_yaml',
            default_value='maps/slam_map.yaml',
            description='Static map used by detector, occlusion filter, and map-grid patrol.',
        ),
        DeclareLaunchArgument(
            'detection_max_range',
            default_value='1.30',
            description='Detector max range in meters. Lower this if monster detection reacts too early.',
        ),
        DeclareLaunchArgument(
            'detection_fov_deg',
            default_value='110.0',
            description='Detector front field-of-view in degrees. Use 360.0 to detect all directions.',
        ),
        DeclareLaunchArgument(
            'cluster_distance',
            default_value='0.30',
            description='Maximum distance in meters for grouping scan hit points into one candidate.',
        ),
        DeclareLaunchArgument(
            'min_cluster_points',
            default_value='3',
            description='Minimum scan hit points required for one monster candidate.',
        ),
        DeclareLaunchArgument(
            'max_candidate_distance',
            default_value='1.60',
            description='Mission ignores candidates farther than this robot-relative distance in meters.',
        ),
        DeclareLaunchArgument(
            'approach_distance',
            default_value='0.75',
            description='Standoff distance from the corrected monster candidate for hunt approach goals.',
        ),
        DeclareLaunchArgument(
            'clear_distance',
            default_value='0.90',
            description='Mission enters ATTACK_MONSTER when the corrected candidate is within this distance.',
        ),
        DeclareLaunchArgument(
            'candidate_center_offset',
            default_value='0.25',
            description='Forward offset from detected scan-surface candidate toward the estimated monster center.',
        ),
        DeclareLaunchArgument(
            'max_clear_attempts',
            default_value='4',
            description='Maximum clear service attempts before returning to patrol.',
        ),
        DeclareLaunchArgument(
            'clear_retry_delay_sec',
            default_value='0.4',
            description='Delay between repeated clear service attempts.',
        ),
        DeclareLaunchArgument(
            'patrol_mode',
            default_value='map_grid',
            description='Patrol strategy: map_grid for map-wide coverage, manual for search_waypoints.',
        ),
        DeclareLaunchArgument(
            'patrol_grid_spacing',
            default_value='0.80',
            description='Distance between generated map-grid patrol waypoints in meters.',
        ),
        DeclareLaunchArgument(
            'patrol_wall_clearance',
            default_value='0.28',
            description='Minimum free-space clearance around generated patrol waypoints.',
        ),
        DeclareLaunchArgument(
            'patrol_max_waypoints',
            default_value='80',
            description='Maximum generated map-grid patrol waypoints. 0 means unlimited.',
        ),
        DeclareLaunchArgument(
            'patrol_start_nearest',
            default_value='true',
            description='Start map-grid patrol from the waypoint nearest to the robot.',
        ),
        DeclareLaunchArgument(
            'patrol_unknown_is_blocked',
            default_value='true',
            description='Treat unknown map cells as blocked when generating patrol waypoints.',
        ),
        DeclareLaunchArgument(
            'target_kill_count',
            default_value='3',
            description='Number of monsters to clear before navigating to exit_pose.',
        ),
        DeclareLaunchArgument(
            'search_waypoints',
            default_value='0.0,0.0,0.0;0.8,0.0,0.0;0.8,0.8,1.57;0.0,0.8,3.14',
            description='Manual fallback patrol waypoints as "x,y,yaw;x,y,yaw".',
        ),
        DeclareLaunchArgument(
            'exit_pose',
            default_value='0.0,0.0,0.0',
            description='Known exit pose as "x,y,yaw". Adjust in RViz for the map.',
        ),
        DeclareLaunchArgument(
            'autostart',
            default_value='true',
            description='Start the mission state machine automatically.',
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use Gazebo simulation clock.',
        ),
        OpaqueFunction(function=_launch_setup),
    ])
