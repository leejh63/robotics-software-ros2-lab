# ROS 설치

**Locale 설정: UTF-8을 지원하도록 로케일 설정**

```bash
sudo apt update && sudo apt install locales

sudo locale-gen en_US en_US.UTF-8

sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

export LANG=en_US.UTF-8
```

**GPG 키 추가: ROS2 저장소 패키지가 신뢰할 수 있는지 확인하기 위한 보안 키 등록**

```bash
sudo apt update && sudo apt install curl gnupg lsb-release

sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
        -o /usr/share/keyrings/ros-archive-keyring.gpg
```

**apt 소스 등록: 패키지 매니저가 ROS2 패키지를 찾을 수 있도록 저장소 목록에 추가**

```bash
echo "deb [arch=$(dpkg --print-architecture) \
        signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
        http://packages.ros.org/ros2/ubuntu \
        $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | \
        sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

**ROS2 Humble 설치: 저장소 업데이트 후 데스크탑 버전 설치**

```bash
sudo apt update

sudo apt install ros-humble-desktop
```

**rosdep 초기화**

```bash
sudo apt install python3-rosdep

sudo rosdep init

rosdep update
```

**colcon: ROS2 패키지를 빌드하는 공식 빌드 도구**

```bash
sudo apt install python3-colcon-common-extensions

colcon version-check
```

**ROS2 시스템의 실행 파일, 라이브러리, 환경 변수(Path 등)**

```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

source ~/.bashrc

printenv | grep ROS
```