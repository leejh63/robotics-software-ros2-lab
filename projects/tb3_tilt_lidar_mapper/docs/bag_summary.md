# Sample bag summary

| Bag | Duration | `/imu` | `/scan` | `/tf` | `/tf_static` | Notes |
|---|---:|---:|---:|---:|---:|---|
| `tb3_tilt_lidar_20260610_120848` | about 145 s | 2910 | 1368 | 4528 | 1 | Longer sample. Recommended for first test. |
| `tb3_tilt_lidar_20260610_121243` | about 68 s | 1358 | 634 | 2213 | 1 | Shorter sample. Useful for quick checks. |

Main frames:

```text
/imu  -> imu_link
/scan -> base_scan
```

The static transform data includes the TurtleBot3 sensor frames needed to relate `base_scan` to `base_link`.

The sample bags contain only LiDAR, IMU, and TF data. They do not contain camera frames or audio.
