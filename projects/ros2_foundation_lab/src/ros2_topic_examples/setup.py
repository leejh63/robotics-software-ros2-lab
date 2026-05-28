from setuptools import find_packages, setup

package_name = 'ros2_topic_examples'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jaeho Lee',
    maintainer_email='leejh63@users.noreply.github.com',
    description='Python ROS2 topic publisher, subscriber, and turtlesim command velocity examples.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'string_talker = ros2_topic_examples.string_talker:main',
            'string_listener = ros2_topic_examples.string_listener:main',
            'turtle_square = ros2_topic_examples.turtle_square:main',
        ],
    },
)
