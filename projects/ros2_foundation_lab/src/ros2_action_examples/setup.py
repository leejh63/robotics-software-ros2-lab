from setuptools import find_packages, setup

package_name = 'ros2_action_examples'

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
    description='ROS2 action server and client examples using a custom action interface.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'move_action_server = ros2_action_examples.move_server:main',
            'move_action_client = ros2_action_examples.move_client:main',
        ],
    },
)
