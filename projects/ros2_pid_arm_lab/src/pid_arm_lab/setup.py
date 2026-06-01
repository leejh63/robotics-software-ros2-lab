from glob import glob
from setuptools import setup

package_name = 'pid_arm_lab'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/urdf', glob('urdf/*.xacro')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/worlds', glob('worlds/*.world')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jaeho Lee',
    maintainer_email='leejh63@users.noreply.github.com',
    description='Reproducible ROS2 Humble Gazebo Classic PID control lab for a one degree-of-freedom arm.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pid_arm_controller = pid_arm_lab.pid_arm_controller:main',
        ],
    },
)
