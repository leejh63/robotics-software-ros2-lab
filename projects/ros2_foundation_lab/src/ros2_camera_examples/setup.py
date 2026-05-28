import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'ros2_camera_examples'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jaeho Lee',
    maintainer_email='leejh63@users.noreply.github.com',
    description='ROS2 camera, OpenCV, YOLO image, and custom detection message examples.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'image_publisher = ros2_camera_examples.image_publisher:main',
            'image_processor = ros2_camera_examples.image_processor:main',
            'image_edge_publisher = ros2_camera_examples.image_edge_publisher:main',
            'yolo_image_publisher = ros2_camera_examples.yolo_image_publisher:main',
            'yolo_detection_publisher = ros2_camera_examples.yolo_detection_publisher:main',
        ],
    },
)
