# 04. PID 튜닝 가이드

## 제일 먼저 P 제어만 본다

처음에는 I, D를 끄고 P만 봅니다.

```bash
ros2 param set /pid_arm_controller ki 0.0
ros2 param set /pid_arm_controller kd 0.0
ros2 param set /pid_arm_controller kp 5.0
ros2 param set /pid_arm_controller setpoint 0.5
```

팔이 거의 움직이지 않으면 `kp`를 올립니다.

```bash
ros2 param set /pid_arm_controller kp 10.0
ros2 param set /pid_arm_controller kp 20.0
```

## P gain이 너무 작을 때

```text
증상:
  - 팔이 목표각 근처까지 가지 못한다.
  - 반응이 느리다.
  - 중력 때문에 아래로 처진다.

대응:
  - kp를 올린다.
  - 필요하면 gravity_gain을 추가한다.
```

## P gain이 너무 클 때

```text
증상:
  - 팔이 목표각을 지나쳐 흔들린다.
  - 진동이 크다.
  - Gazebo에서 팔이 불안정하게 튄다.

대응:
  - kp를 낮춘다.
  - kd를 추가한다.
  - max_effort를 낮춘다.
```

## D gain 추가

D항은 변화율에 반응합니다. 흔들림을 줄이는 감쇠 역할을 합니다.

```bash
ros2 param set /pid_arm_controller kd 0.5
ros2 param set /pid_arm_controller kd 1.0
ros2 param set /pid_arm_controller kd 2.0
```

D가 너무 크면 노이즈나 작은 변화에 민감해질 수 있습니다.

## I gain 추가

I항은 오래 남는 offset을 줄이는 데 사용합니다.

```bash
ros2 param set /pid_arm_controller ki 0.1
```

I가 너무 크면 적분항이 쌓여서 overshoot가 커질 수 있습니다. 이 구현은 `integral_limit`과 saturation 시 적분 되돌리기를 통해 windup을 줄입니다.

## 중력 보상

팔은 중력 때문에 특정 각도에서 아래로 처질 수 있습니다. `gravity_gain`을 사용하면 간단한 feedforward 보상을 추가할 수 있습니다.

```bash
ros2 param set /pid_arm_controller gravity_gain 1.0
ros2 param set /pid_arm_controller gravity_gain 2.0
```

이 구현은 현재 각도 기준으로 아래 값을 더합니다.

```text
gravity_comp = -gravity_gain * cos(current_position)
```

부호가 반대로 느껴지면 `gravity_gain`을 음수로 줄 수 있습니다.

```bash
ros2 param set /pid_arm_controller gravity_gain -1.0
```

## 추천 튜닝 순서

```text
1. ki=0, kd=0으로 둔다.
2. kp를 올려서 팔이 목표 근처로 가게 만든다.
3. 흔들림이 크면 kd를 조금씩 올린다.
4. 목표 근처 offset이 계속 남으면 ki를 아주 작게 추가한다.
5. 팔이 중력 때문에 처지면 gravity_gain을 검토한다.
6. 출력이 너무 크면 max_effort를 낮춘다.
```

## 튜닝할 때 봐야 할 값

PID 노드는 로그로 아래 값을 출력합니다.

```text
pos  현재 각도
err  목표각과 현재각의 오차
eff  최종 effort 명령
P    비례항
I    적분항
D    미분항
G    중력 보상항
dt   제어 주기
```

값이 이상하면 gain을 바꾸기 전에 먼저 `/joint_states`와 controller 상태를 확인합니다.
