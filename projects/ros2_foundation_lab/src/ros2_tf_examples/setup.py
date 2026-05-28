import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'ros2_tf_examples'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jaeho Lee',
    maintainer_email='leejh63@users.noreply.github.com',
    description='ROS2 TF tree, listener, and YOLO object transform examples.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'odom_simulator = ros2_tf_examples.odom_simulator:main',
            'tf_listener = ros2_tf_examples.tf_listener:main',
            'tf_tree_simulator = ros2_tf_examples.tf_tree_simulator:main',
            'yolo_tf_broadcaster = ros2_tf_examples.yolo_tf_broadcaster:main',
        ],
    },
)
