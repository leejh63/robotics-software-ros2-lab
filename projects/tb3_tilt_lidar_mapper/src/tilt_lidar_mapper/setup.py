from glob import glob
import os
from setuptools import setup

package_name = 'tilt_lidar_mapper'

setup(
    name=package_name,
    version='0.2.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jaehoon Lee',
    maintainer_email='leejh63@users.noreply.github.com',
    description='Accumulate TurtleBot3 2D LaserScan data as PointCloud2 using IMU tilt.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'scan_imu_tilt_cloud = tilt_lidar_mapper.scan_imu_tilt_cloud:main',
        ],
    },
)
