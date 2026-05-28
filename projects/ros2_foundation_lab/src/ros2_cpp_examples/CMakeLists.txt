cmake_minimum_required(VERSION 3.8)
project(ros2_cpp_examples)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

add_executable(cpp_talker src/cpp_talker.cpp)
ament_target_dependencies(cpp_talker rclcpp std_msgs)

add_executable(cpp_listener src/cpp_listener.cpp)
ament_target_dependencies(cpp_listener rclcpp std_msgs)

install(TARGETS cpp_talker cpp_listener DESTINATION lib/${PROJECT_NAME})

ament_package()
