#!/usr/bin/env bash
set -euo pipefail

if ! command -v ros2 >/dev/null 2>&1; then
  if [[ -f /opt/ros/humble/setup.bash ]]; then
    # shellcheck source=/dev/null
    source /opt/ros/humble/setup.bash
  fi
fi

printf '
[Topics]
'
ros2 topic list | grep -E '(/scan|/imu|/tf_static|/tilted_lidar)' || true

printf '
[PointCloud width]
'
ros2 topic echo /tilted_lidar_cloud --once --field width || true

printf '
[PointCloud rate]
'
ros2 topic hz /tilted_lidar_cloud || true
