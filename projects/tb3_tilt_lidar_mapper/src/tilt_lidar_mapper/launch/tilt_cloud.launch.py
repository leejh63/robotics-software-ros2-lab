from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    args = [
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('scan_topic', default_value='/scan'),
        DeclareLaunchArgument('imu_topic', default_value='/imu'),
        DeclareLaunchArgument('tf_static_topic', default_value='/tf_static'),
        DeclareLaunchArgument('cloud_topic', default_value='/tilted_lidar_cloud'),
        DeclareLaunchArgument('slice_topic', default_value='/tilted_lidar_slice'),
        DeclareLaunchArgument('world_frame', default_value='base_link'),
        DeclareLaunchArgument('base_frame', default_value='base_link'),
        DeclareLaunchArgument('accumulate', default_value='true'),
        DeclareLaunchArgument('max_points', default_value='120000'),
        DeclareLaunchArgument('point_stride', default_value='1'),
        DeclareLaunchArgument('publish_every_n_scans', default_value='1'),
        DeclareLaunchArgument('use_roll_pitch_only', default_value='true'),
        DeclareLaunchArgument('zero_initial_orientation', default_value='true'),
        DeclareLaunchArgument('invert_imu_rotation', default_value='false'),
        DeclareLaunchArgument('height_scale', default_value='1.0'),
        DeclareLaunchArgument('preserve_lidar_range', default_value='true'),
        DeclareLaunchArgument('fixed_lidar_origin', default_value='true'),
        DeclareLaunchArgument('min_range', default_value='0.05'),
        DeclareLaunchArgument('max_range', default_value='8.0'),
        DeclareLaunchArgument('publish_debug', default_value='true'),
    ]

    node = Node(
        package='tilt_lidar_mapper',
        executable='scan_imu_tilt_cloud',
        name='scan_imu_tilt_cloud',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'scan_topic': LaunchConfiguration('scan_topic'),
            'imu_topic': LaunchConfiguration('imu_topic'),
            'tf_static_topic': LaunchConfiguration('tf_static_topic'),
            'cloud_topic': LaunchConfiguration('cloud_topic'),
            'slice_topic': LaunchConfiguration('slice_topic'),
            'world_frame': LaunchConfiguration('world_frame'),
            'base_frame': LaunchConfiguration('base_frame'),
            'accumulate': LaunchConfiguration('accumulate'),
            'max_points': LaunchConfiguration('max_points'),
            'point_stride': LaunchConfiguration('point_stride'),
            'publish_every_n_scans': LaunchConfiguration('publish_every_n_scans'),
            'use_roll_pitch_only': LaunchConfiguration('use_roll_pitch_only'),
            'zero_initial_orientation': LaunchConfiguration('zero_initial_orientation'),
            'invert_imu_rotation': LaunchConfiguration('invert_imu_rotation'),
            'height_scale': LaunchConfiguration('height_scale'),
            'preserve_lidar_range': LaunchConfiguration('preserve_lidar_range'),
            'fixed_lidar_origin': LaunchConfiguration('fixed_lidar_origin'),
            'min_range': LaunchConfiguration('min_range'),
            'max_range': LaunchConfiguration('max_range'),
            'publish_debug': LaunchConfiguration('publish_debug'),
        }],
    )
    return LaunchDescription(args + [node])
