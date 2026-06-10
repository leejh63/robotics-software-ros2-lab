# Algorithm note

For each valid LaserScan range value, the node first creates a 2D point in the LiDAR frame:

```text
p_scan = [r cos(theta), r sin(theta), 0]
```

Then the static LiDAR rotation is applied:

```text
v_base = R_base_scan * p_scan
```

The relative IMU orientation is converted to a rotation matrix. By default, yaw is removed and only roll/pitch are used:

```text
R_tilt = R_imu_relative_roll_pitch
```

The output point is computed as:

```text
p_out = t_base_scan + R_tilt * v_base
```

Because rotation matrices preserve vector length, the LiDAR range is kept unchanged when `height_scale` is `1.0`.

This repository intentionally does not integrate robot translation. For a map that follows the actual robot motion, the same point should be transformed by odometry or SLAM pose after the LiDAR/IMU conversion step.
