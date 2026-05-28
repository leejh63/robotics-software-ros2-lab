```bash
cd ~/Downloads

sudo chmod +x imager_2.0.7_amd64.AppImage

./imager_2.0.7_amd64.AppImage
```

```bash
ssh ubuntu@turtle3-100.local
# ssh ubuntu@192.168.10.35

sudo nano /etc/netplan/50-cloud-init.yaml
```

```bash
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: true
      optional: true
  wifis:
    wlan0:
      dhcp4: true
      optional: true
      access-points:
        "아이폰_핫스팟_이름":
          password: "핫스팟_비밀번호"
        "집_와이파이_이름":
          password: "집_와이파이_비밀번호"
```

```bash
sudo nano /etc/apt/apt.conf.d/20auto-upgrades

APT::Periodic::Update-Package-Lists "0";
APT::Periodic::Unattended-Upgrade "0";
```

```bash
systemctl mask systemd-networkd-wait-online.service

sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

```bash
# 1. 현재 상태 확인
$ free -h
$ swapon --show

# 2. 기존 swap이 작다면 임시 swap 파일 추가 (예: 2GB)
$ sudo fallocate -l 2G /swapfile_tmp
$ sudo chmod 600 /swapfile_tmp
$ sudo mkswap /swapfile_tmp
$ sudo swapon /swapfile_tmp

# 3. 확인
$ free -h
```

```bash
locale  # check for UTF-8

sudo apt update && sudo apt install locales

sudo locale-gen en_US en_US.UTF-8

sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

export LANG=en_US.UTF-8

locale  # verify settings
```

```bash
sudo apt install software-properties-common

sudo add-apt-repository universe
```

```bash
sudo apt update && sudo apt install curl -y

export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F'"' '{print $4}')

curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"

sudo dpkg -i /tmp/ros2-apt-source.deb
```

```bash
sudo apt update

sudo apt upgrade

sudo reboot

sudo apt install ros-humble-ros-base

sudo apt install ros-dev-tools

sudo apt install ros-humble-demo-nodes-cpp
sudo apt install ros-humble-demo-nodes-py
```

```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
echo "export ROS_DOMAIN_ID=100" >> ~/.bashrc

source ~/.bashrc

printenv | grep ROS
```

```bash
sudo apt install python3-argcomplete python3-colcon-common-extensions libboost-system-dev build-essential

sudo apt install ros-humble-hls-lfcd-lds-driver

sudo apt install ros-humble-turtlebot3-msgs

sudo apt install ros-humble-dynamixel-sdk

sudo apt install ros-humble-xacro

sudo apt install libudev-dev
```

```bash
# 1. turtlebot3 관련 바이너리 설치
sudo apt update

sudo apt install -y ros-humble-turtlebot3 ros-humble-turtlebot3-bringup ros-humble-turtlebot3-msgs ros-humble-turtlebot3-node ros-humble-turtlebot3-teleop

# 2. ld08_driver 바이너리 확인 및 설치
sudo apt install -y ros-humble-ld08-driver

#
echo 'export LDS_MODEL=LDS-02' >> ~/.bashrc
```

```bash
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null

ros2 run ld08_driver ld08_driver

# 노트북 확인
ros2 topic list
ros2 topic echo /scan
ros2 topic hz /scan
```

https://www.youtube.com/watch?v=UqYR_z3q9a0

```bash
# 1. 패키지 설치 (사용자가 받은 명령 + 제가 안내한 것 합침)
$ sudo apt install -y ros-humble-v4l2-camera ros-humble-image-transport-plugins v4l-utils raspi-config

# 2. CSI 카메라 인터페이스 활성화
$ sudo raspi-config

sudo nano /boot/firmware/config.txt

  # Disable libcamera auto detect
  camera_auto_detect=0
  # Enable legacy camera stack for bcm2835-v4l2
  start_x=1

# 3. 재부팅 후 장치 확인
$ v4l2-ctl --list-devices

# 4. ROS2 노드 실행
$ ros2 run v4l2_camera v4l2_camera_node

# 5. 노트북 확인
ros2 run rqt_image_view rqt_image_view



ros2 run v4l2_camera v4l2_camera_node \
  --ros-args \
  -p image_size:=[320,240] \
  -p pixel_format:=YUYV \
  -p output_encoding:=yuv422_yuy2 \
  -p time_per_frame:=[1,10]
  
ros2 run v4l2_camera v4l2_camera_node \
  --ros-args \
  -p image_size:=[160,120] \
  -p pixel_format:=YUYV \
  -p output_encoding:=yuv422_yuy2 \
  -p time_per_frame:=[1,5]
```

https://emanual.robotis.com/docs/en/platform/turtlebot3/opencr_setup/#opencr-setup

```bash
$ sudo dpkg --add-architecture armhf  
$ sudo apt-get update  
$ sudo apt-get install libc6:armhf  
```

```bash
$ export OPENCR_PORT=/dev/ttyACM0  
$ export OPENCR_MODEL=burger
$ rm -rf ./opencr_update.tar.bz2  
```

```bash
$ wget https://github.com/ROBOTIS-GIT/OpenCR-Binaries/raw/master/turtlebot3/ROS2/latest/opencr_update.tar.bz2   
$ tar -xvf opencr_update.tar.bz2 
```

```bash
$ cd ./opencr_update  
$ ./update.sh $OPENCR_PORT $OPENCR_MODEL.opencr  
```

```bash
echo 'export TURTLEBOT3_MODEL=burger' >> ~/.bashrc
source ~/.bashrc

ros2 launch turtlebot3_bringup robot.launch.py

ros2 run turtlebot3_teleop teleop_keyboard
```




- 라이다 센서 시작
ros2 run ld08_driver ld08_driver
- 라이다 데이터 확인 (노트북)
-- scan 이 있는지 확인
ros2 topic list
-- 라이더 데이터 확인
ros2 topic echo /scan

- 카메라 센서 시작
ros2 run v4l2_camera v4l2_camera_node \
  --ros-args \
  -p image_size:=[320,240] \
  -p pixel_format:=YUYV \
  -p output_encoding:=yuv422_yuy2 \
  -p time_per_frame:=[1,10]

-- 카메라 데이터 확인 (노트북)
ros2 run rqt_image_view rqt_image_view
(새로 고침 후 옆에 박스 화살표 누른 후 /image_raw 선택)

- 바퀴 조절 모듈 시작
ros2 launch turtlebot3_bringup robot.launch.py

- 바퀴 컨트롤 (터틀봇)
ros2 run turtlebot3_teleop teleop_keyboard
