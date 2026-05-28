import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'ros2_launch_examples'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jaeho Lee',
    maintainer_email='leejh63@users.noreply.github.com',
    description='ROS2 launch examples for camera and perception pipelines.',
    license='Apache-2.0',
    entry_points={'console_scripts': []},
)
