# Runtime Validation Result Template

이 템플릿은 실제 ROS2/Gazebo/Nav2 실행 결과를 기록하기 위한 문서입니다. 정적 검증 결과와 runtime 검증 결과를 섞지 않습니다.

작성한 결과 파일은 공개 commit에 포함할지 별도로 판단합니다. console log, bag, build output, screenshot은 용량과 개인정보를 확인한 뒤 필요한 것만 정리합니다.

---

## 1. 기본 정보

```text
Project:
Validation date:
Machine / OS:
ROS2 distribution:
Gazebo version:
Nav2 package version, if relevant:
Commit or patched zip stage:
Tester:
```

---

## 2. 사용한 소스

```text
Original source archive:
Patched source archive:
Diff file:
Modified files relevant to this validation:
```

---

## 3. Build 결과

```text
Command:
Result: PASS / FAIL / PARTIAL
Observed output summary:
Error, if any:
```

---

## 4. Runtime 환경 준비

```text
Workspace path:
Sourced setup files:
Extra environment variables:
External dataset / rosbag / camera / model path:
```

---

## 5. 실행 명령 기록

각 터미널별로 실제 입력한 명령을 그대로 적습니다.

### Terminal A

```bash
# commands
```

### Terminal B

```bash
# commands
```

### Terminal C

```bash
# commands
```

---

## 6. 관찰 결과

```text
Topics checked:
Frames checked:
Nodes checked:
Lifecycle states:
Actions checked:
Controller states, if relevant:
```

---

## 7. 통과 / 실패 판단

```text
PASS:
FAIL:
PARTIAL:
NOT TESTED:
```

판단 근거:

```text
- 
```

---

## 8. README에 적어도 되는 표현

```text
Verified:
- 

Not verified:
- 

Do not claim:
- 
```

---

## 9. 후속 수정 후보

```text
P0:
P1:
P2:
```
