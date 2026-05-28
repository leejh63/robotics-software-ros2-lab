from setuptools import find_packages, setup

package_name = 'ros2_service_examples'

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
    description='ROS2 service server and client examples using custom interfaces.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'led_service_server = ros2_service_examples.led_server:main',
            'led_service_client = ros2_service_examples.led_client:main',
            'add_two_num_server = ros2_service_examples.add_server:main',
            'add_two_num_client = ros2_service_examples.add_client:main',
        ],
    },
)
