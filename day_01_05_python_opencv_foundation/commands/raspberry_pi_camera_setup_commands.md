# Raspberry Pi / TurtleBot Camera Setup Memo Commands

이 문서는 기존 `day_05_raspberry_pi/in_rasp_install.md`에 있던 실제 환경 메모를 안전하게 다시 정리한 것이다. 장비/이미지/네트워크 조건에 따라 그대로 맞지 않을 수 있으므로 실행 전 현재 환경을 확인해야 한다.

## 1. Raspberry Pi Imager 실행 예시

```bash
cd ~/Downloads
chmod +x imager_2.0.7_amd64.AppImage
./imager_2.0.7_amd64.AppImage
```

## 2. SSH 접속

```bash
ssh ubuntu@ROBOT_HOST.local
ssh ubuntu@ROBOT_IP
```

## 3. netplan 설정

```bash
sudo nano /etc/netplan/50-cloud-init.yaml
sudo netplan apply
ip addr
```

예시 구조:

```yaml
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
        "WIFI_NAME":
          password: "WIFI_PASSWORD_PLACEHOLDER"
```

## 4. 자동 업데이트 비활성화 메모

```bash
sudo nano /etc/apt/apt.conf.d/20auto-upgrades
```

예시:

```text
APT::Periodic::Update-Package-Lists "0";
APT::Periodic::Unattended-Upgrade "0";
```

## 5. 절전 비활성화 메모

```bash
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
sudo systemctl mask systemd-networkd-wait-online.service
```

## 6. swap 임시 추가

```bash
free -h
swapon --show
sudo fallocate -l 2G /swapfile_tmp
sudo chmod 600 /swapfile_tmp
sudo mkswap /swapfile_tmp
sudo swapon /swapfile_tmp
free -h
```

해제:

```bash
sudo swapoff /swapfile_tmp
sudo rm /swapfile_tmp
```

## 7. UTF-8 locale 설정

```bash
locale
sudo apt update
sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
locale
```

## 8. 카메라 장치 확인

```bash
ls /dev/video*
v4l2-ctl --list-devices
```

ROS2를 여러 장비에서 쓸 때는 같은 네트워크, 같은 `ROS_DOMAIN_ID`, 방화벽, multicast 환경을 확인해야 한다.
