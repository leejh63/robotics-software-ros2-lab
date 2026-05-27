# 01. TurtleBot3 환경 설정

## 1. 목적

TurtleBot3 Burger 실습을 위해 ROS 2 Humble, Gazebo Classic, TurtleBot3 패키지 환경을 준비한다.

기존 자료의 예시처럼 `~/.bashrc`에 워크스페이스 경로를 직접 추가하지 않고, 별도 환경 파일을 사용한다.

```bash
source ~/envs/tb3_humble.bash
```

이 방식은 다른 ROS2 프로젝트와 TurtleBot3 실습 환경이 섞이는 문제를 줄인다.


## 경로 표기 기준

문서에서는 개인 경로를 직접 쓰지 않고 아래 변수로 워크스페이스를 표현한다.

```bash
# 예시: 사용자의 실제 TurtleBot3 워크스페이스 경로로 지정한다.
export TB3_WS=~/turtlebot3_ws
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
```

## 2. 기준 워크스페이스

```bash
$TB3_WS
```

소스 폴더:

```bash
$TB3_WS/src
```

## 3. 워크스페이스 생성

처음 구성하는 경우:

```bash
mkdir -p "$TB3_WS/src"
cd "$TB3_WS/src"
```

## 4. TurtleBot3 소스 다운로드

처음 한 번만 실행한다.

```bash
git clone -b humble https://github.com/ROBOTIS-GIT/DynamixelSDK.git
git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3_msgs.git
git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3.git
git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3_simulations.git
```

확인:

```bash
ls
```

예상:

```text
DynamixelSDK
turtlebot3
turtlebot3_msgs
turtlebot3_simulations
```

## 5. 의존성 설치

```bash
sudo apt update
sudo apt install -y \
  ros-humble-cartographer \
  ros-humble-cartographer-ros \
  ros-humble-nav2-map-server \
  ros-humble-nav2-lifecycle-manager \
  ros-humble-nav2-bringup \
  ros-humble-slam-toolbox \
  ros-humble-tf2-ros
```

필요하면 `rosdep`도 사용한다.

```bash
cd "$TB3_WS"
rosdep update
rosdep install --from-paths src -y --ignore-src
```

## 6. 빌드

```bash
cd "$TB3_WS"
colcon build --symlink-install
```

확인:

```bash
ls install/setup.bash
```

정상:

```text
install/setup.bash
```

## 7. 환경 적용

각 터미널에서 TurtleBot3 실습을 시작할 때 실행한다.

```bash
cd "$TB3_WS"
source ~/envs/tb3_humble.bash
```

확인:

```bash
echo $TURTLEBOT3_MODEL
ros2 pkg list | grep turtlebot3
```

정상 모델:

```text
burger
```

## 8. 환경 파일 권장 예시

`~/envs/tb3_humble.bash`에는 `TB3_WS`를 먼저 확정한 뒤, ROS 2와 워크스페이스 환경을 적용한다.

```bash
# ~/envs/tb3_humble.bash

export TB3_WS="$HOME/turtlebot3_ws"
export TURTLEBOT3_MODEL=burger

source /opt/ros/humble/setup.bash
source /usr/share/gazebo/setup.sh

if [ -f "$TB3_WS/install/setup.bash" ]; then
  source "$TB3_WS/install/setup.bash"
else
  echo "[tb3_humble] warning: $TB3_WS/install/setup.bash not found"
fi
```

이렇게 두면 새 터미널에서 아래 명령만 실행해도 동일한 기준 환경을 적용할 수 있다.

```bash
source ~/envs/tb3_humble.bash
cd "$TB3_WS"
```

주의할 점은 `source $TB3_WS/install/setup.bash`를 `TB3_WS` 정의보다 먼저 쓰지 않는 것이다. 그러면 새 터미널에서 `TB3_WS`가 비어 있거나 다른 값일 때 환경 적용이 실패할 수 있다.
