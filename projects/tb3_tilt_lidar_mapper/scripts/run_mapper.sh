#!/usr/bin/env bash
set -euo pipefail

if ! command -v ros2 >/dev/null 2>&1; then
  if [[ -f /opt/ros/humble/setup.bash ]]; then
    # shellcheck source=/dev/null
    source /opt/ros/humble/setup.bash
  fi
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [[ -f "$PROJECT_DIR/install/setup.bash" ]]; then
  # shellcheck source=/dev/null
  source "$PROJECT_DIR/install/setup.bash"
elif [[ -n "${WS_DIR:-}" && -f "$WS_DIR/install/setup.bash" ]]; then
  # shellcheck source=/dev/null
  source "$WS_DIR/install/setup.bash"
elif [[ -f "$HOME/Workspace/ros2_ws/install/setup.bash" ]]; then
  # shellcheck source=/dev/null
  source "$HOME/Workspace/ros2_ws/install/setup.bash"
fi

ros2 launch tilt_lidar_mapper tilt_cloud.launch.py \
  use_sim_time:=true \
  world_frame:=base_link \
  height_scale:=1.0 \
  preserve_lidar_range:=true \
  fixed_lidar_origin:=true \
  use_roll_pitch_only:=true \
  zero_initial_orientation:=true \
  accumulate:=true \
  max_points:=120000
