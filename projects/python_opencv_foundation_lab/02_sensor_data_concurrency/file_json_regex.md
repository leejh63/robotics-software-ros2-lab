# 파일 I/O · JSON · 정규표현식

---

## 목차

1. [파일 I/O — open()과 모드](#1-파일-io--open과-모드)
2. [with 문 — 파일 핸들 누수 방지](#2-with-문--파일-핸들-누수-방지)
3. [JSON 처리 4가지 핵심 함수](#3-json-처리-4가지-핵심-함수)
4. [센서 로그를 JSON으로 저장·로드](#4-센서-로그를-json으로-저장로드)
5. [예외 처리](#5-예외-처리)
6. [정규표현식 — 메타 문자](#6-정규표현식--메타-문자)
7. [re 모듈 핵심 함수](#7-re-모듈-핵심-함수)
8. [그룹 캡처 — 번호 그룹 vs 이름 붙은 그룹](#8-그룹-캡처--번호-그룹-vs-이름-붙은-그룹)
9. [로봇 로그 파싱 예제](#9-로봇-로그-파싱-예제)
10. [탐욕적 매칭 주의](#10-탐욕적-매칭-주의)
11. [코드 완성 문제 정답](#11-코드-완성-문제-정답)
12. [오류 찾기 문제 정답](#12-오류-찾기-문제-정답)

---

## 1. 파일 I/O — open()과 모드

로봇은 센서 로그 저장, 설정 파일 로드, 경로 기록 등 파일을 통해 상태를 유지합니다.

```python
f = open("파일명", "모드")
```

| 모드 | 설명 |
|------|------|
| `'r'` | 읽기 전용. 파일 없으면 `FileNotFoundError` |
| `'w'` | 쓰기. 파일 없으면 생성, 있으면 **덮어씀** |
| `'a'` | 추가. 파일 끝에 이어 씀. 기존 내용 보존 |
| `'rb'` / `'wb'` | 바이너리 읽기/쓰기 (pickle 등) |

---

## 2. with 문 — 파일 핸들 누수 방지

`close()`를 직접 호출하면 예외 발생 시 누락될 수 있습니다.  
`with` 문은 블록을 벗어나면 예외 여부와 관계없이 자동으로 파일을 닫아줍니다.

```python
# 나쁜 예 — close() 누락 가능
f = open("sensor_data.csv", "r")
data = f.read()
# f.close() 빠뜨리면 파일 핸들 누수

# 좋은 예 — with 문
with open("sensor_data.csv", "r") as f:
    data = f.read()
# 블록 종료 시 자동 close()
```

---

## 3. JSON 처리 4가지 핵심 함수

| 함수 | 대상 | 방향 |
|------|------|------|
| `json.dump(obj, f)` | 파일 객체 | Python → 파일에 JSON 저장 |
| `json.load(f)` | 파일 객체 | 파일 → Python 객체 로드 |
| `json.dumps(obj)` | 문자열 | Python → JSON 문자열 변환 |
| `json.loads(s)` | 문자열 | JSON 문자열 → Python 객체 변환 |

```
s가 붙으면 문자열(string) 대상, 없으면 파일 대상
dump  → 저장 방향 (Python → JSON)
load  → 불러오기 방향 (JSON → Python)
```

```python
import json

# 저장
data = {"robot_id": "Alpha-01", "battery": 85.5}
with open("robot_config.json", "w") as f:
    json.dump(data, f, indent=2)

# 로드
with open("robot_config.json", "r") as f:
    loaded = json.load(f)

print(loaded["battery"])  # 85.5

# 문자열 변환
json_str = json.dumps(data)        # Python → 문자열
obj      = json.loads(json_str)    # 문자열 → Python
```

---

## 4. 센서 로그를 JSON으로 저장·로드

NumPy 배열은 JSON 직렬화가 안 되므로 `.tolist()`로 변환해야 합니다.

```python
import json, numpy as np

t     = np.arange(100)
accel = np.random.randn(100, 3)

log = {
    "sensor": "IMU-01",
    "time":   t.tolist(),      # ndarray → list 변환 필수
    "accel":  accel.tolist()   # (100, 3) ndarray → 중첩 list
}

with open("robot_logs.json", "w") as f:
    json.dump(log, f, indent=2)

# 로드 후 ndarray 복원
with open("robot_logs.json", "r") as f:
    loaded = json.load(f)

t_back     = np.array(loaded["time"])    # (100,)
accel_back = np.array(loaded["accel"])   # (100, 3)
```

| 작업 | 코드 |
|------|------|
| ndarray → JSON | `.tolist()` |
| JSON → ndarray | `np.array(loaded_list)` |

---

## 5. 예외 처리

로봇 소프트웨어는 예외가 발생해도 루프가 멈추지 않아야 합니다.

```python
try:
    with open("robot_logs.json", "r") as f:
        logs = json.load(f)
except FileNotFoundError:
    print("파일을 찾을 수 없습니다.")
except json.JSONDecodeError:
    print("JSON 파싱 오류입니다.")
```

| 예외 | 발생 상황 |
|------|-----------|
| `FileNotFoundError` | 존재하지 않는 파일을 `'r'`로 열 때 |
| `json.JSONDecodeError` | JSON 형식이 잘못된 파일을 파싱할 때 |
| `TypeError: not JSON serializable` | ndarray 등 직렬화 불가 타입을 `json.dump`할 때 |

---

## 6. 정규표현식 — 메타 문자

| 메타 문자 | 의미 | 예시 |
|-----------|------|------|
| `.` | 임의의 한 문자 | `a.c` → abc, a1c |
| `\d` | 숫자 `[0-9]` | `\d+` → 123 |
| `\w` | 단어 문자 `[a-zA-Z0-9_]` | `\w+` → ERROR |
| `\s` | 공백 문자 | |
| `*` | 0회 이상 반복 | `a*` |
| `+` | 1회 이상 반복 | `\d+` |
| `?` | 0 또는 1회 | |
| `{n}` | 정확히 n회 | `\d{4}` → 2026 |
| `[]` | 문자 클래스 | `[A-Z]` |
| `^` | 문자열 시작 | |
| `$` | 문자열 끝 | |
| `\[` `\]` | 대괄호 리터럴 (이스케이프 필수) | `\[\d+\]` |

---

## 7. re 모듈 핵심 함수

| 함수 | 동작 |
|------|------|
| `re.match(pat, s)` | 문자열 **시작**에서만 매칭. 중간 패턴엔 사용 금지 |
| `re.search(pat, s)` | 문자열 **전체**에서 첫 번째 매칭 찾기. 로그 파싱에 주로 사용 |
| `re.findall(pat, s)` | 매칭되는 **모든 결과를 리스트**로 반환 |
| `re.sub(pat, rep, s)` | 매칭된 부분을 `rep`으로 **치환** |

```python
import re

log = "2026-04-22 ERROR: Motor overheated"

# search — 문자열 어디서든 찾음
match = re.search(r"\d{4}-\d{2}-\d{2}", log)
print(match.group())  # 2026-04-22

# findall — 모든 숫자 추출
nums = re.findall(r"\d+", log)
print(nums)  # ['2026', '04', '22']

# sub — 날짜 마스킹
masked = re.sub(r"\d{4}-\d{2}-\d{2}", "XXXX-XX-XX", log)
print(masked)  # XXXX-XX-XX ERROR: Motor overheated
```

---

## 8. 그룹 캡처 — 번호 그룹 vs 이름 붙은 그룹

괄호 `()`로 원하는 부분만 추출할 수 있습니다.

```python
log = "[2026-04-07 10:00:12] ERROR: Motor torque exceeded"
pattern = r"\[(?P<timestamp>.*?)\] (?P<level>\w+): (?P<msg>.*)"
match = re.search(pattern, log)
```

| 접근 방식 | 코드 | 결과 |
|-----------|------|------|
| `group(0)` | 전체 매칭 문자열 | `[2026-04-07 10:00:12] ERROR: Motor torque exceeded` |
| `group(1)` | 첫 번째 캡처 그룹 | `2026-04-07 10:00:12` |
| `group(2)` | 두 번째 캡처 그룹 | `ERROR` |
| `group(3)` | 세 번째 캡처 그룹 | `Motor torque exceeded` |
| `group('timestamp')` | 이름 붙은 그룹 | `2026-04-07 10:00:12` |
| `group('level')` | 이름 붙은 그룹 | `ERROR` |
| `group('msg')` | 이름 붙은 그룹 | `Motor torque exceeded` |

`group(1)` == `group('timestamp')` — 같은 값, 이름 붙은 그룹이 가독성이 좋음.

---

## 9. 로봇 로그 파싱 예제

```python
import re

logs = [
    "[2026-04-07 10:00:12] ERROR: Motor torque exceeded",
    "[2026-04-07 10:00:15] INFO: System OK",
    "[2026-04-07 10:00:18] WARNING: Battery 15%",
]

pattern = r"\[(?P<timestamp>.*?)\] (?P<level>\w+): (?P<msg>.*)"

for log in logs:
    match = re.search(pattern, log)
    if match:
        print(f"[{match.group('level')}] {match.group('timestamp')} — {match.group('msg')}")
```

```
[ERROR] 2026-04-07 10:00:12 — Motor torque exceeded
[INFO] 2026-04-07 10:00:15 — System OK
[WARNING] 2026-04-07 10:00:18 — Battery 15%
```

---

## 10. 탐욕적 매칭 주의

`.*`는 가능한 가장 긴 문자열을 소비합니다(탐욕적).  
로그처럼 구분자가 있는 문자열을 파싱할 때는 `.*?`(비탐욕적)를 사용합니다.

```python
log = "[2026-04-07] [INFO] Motor Active"

# 탐욕적 — 첫 [ 부터 마지막 ] 까지 전부 소비
re.search(r"\[.*\]", log).group()    # '[2026-04-07] [INFO]'

# 비탐욕적 — 첫 ] 에서 멈춤
re.search(r"\[.*?\]", log).group()   # '[2026-04-07]'
```

대괄호 `[` `]`는 메타 문자이므로 리터럴로 쓰려면 `\[` `\]`로 이스케이프해야 합니다.

---

## 11. 코드 완성 문제 정답

```python
# Q1. JSON 파일 안전하게 읽기
try:
    with open("robot_logs.json", "r") as f:
        logs = json.load(f)
except FileNotFoundError:
    print("파일을 찾을 수 없습니다.")
except json.JSONDecodeError:
    print("JSON 파싱 오류입니다.")

# Q2. 로그에서 배터리 수치 추출
pattern = r"Battery (\d+)%"
match = re.search(pattern, "Status: Battery 15%")
print(match.group(1))  # 15

# Q3. 보정 데이터를 JSON으로 저장
calibration = {"offset": 0.05, "gain": 1.1}
with open("calib.json", "w") as f:
    json.dump(calibration, f, indent=2)

# Q4. 대괄호 안 날짜 추출
pattern = r"\[(.+?)\]"
match = re.search(pattern, "[2026-04-07] INFO: Motor Active")
print(match.group(1))  # 2026-04-07

# Q5. 파일 끝에 내용 추가 (append 모드)
with open("sensor_log.txt", "a") as f:
    f.write("Sensor: temperature=36.5\n")
```

---

## 12. 오류 찾기 문제 정답

```python
# Q1. 파일 핸들 누수 → with 문으로 해결
with open("sensor_data.csv", "r") as f:
    data = f.read()

# Q2. json.load()는 파일 객체 전용 → 문자열엔 json.loads()
json_str = '{"voltage": 12.0}'
data = json.loads(json_str)   # load() → loads()
print(data["voltage"])        # 12.0

# Q3. eval()은 보안 위험 → json.loads()로 대체
raw_data = '{"cmd": "reboot"}'
data = json.loads(raw_data)   # eval() → json.loads()
print(data["cmd"])            # reboot
```

| 문제 | 핵심 |
|------|------|
| Q1 | `close()` 대신 `with` 문으로 자동 자원 해제 |
| Q2 | 파일 → `json.load()`, 문자열 → `json.loads()` |
| Q3 | `eval()`은 임의 코드 실행 위험. 항상 `json.loads()` 사용 |

---

*이 문서는 day2 · 03.01 파일 I/O · JSON · 정규표현식 실습 내용을 기반으로 작성되었습니다.*
