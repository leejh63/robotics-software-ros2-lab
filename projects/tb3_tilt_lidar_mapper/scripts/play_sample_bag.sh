#!/usr/bin/env bash
set -euo pipefail

if ! command -v ros2 >/dev/null 2>&1; then
  if [[ -f /opt/ros/humble/setup.bash ]]; then
    # shellcheck source=/dev/null
    source /opt/ros/humble/setup.bash
  fi
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
BAG_SELECTOR="${1:-120848}"
shift || true

case "$BAG_SELECTOR" in
  120848|tb3_tilt_lidar_20260610_120848)
    BAG_DIR="$REPO_DIR/sample_bags/tb3_tilt_lidar_20260610_120848"
    ;;
  121243|tb3_tilt_lidar_20260610_121243)
    BAG_DIR="$REPO_DIR/sample_bags/tb3_tilt_lidar_20260610_121243"
    ;;
  *)
    BAG_DIR="$BAG_SELECTOR"
    ;;
esac

ros2 bag play "$BAG_DIR" --clock "$@"
