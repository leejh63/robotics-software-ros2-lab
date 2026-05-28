# Python 학습 문서 — 기초 문법부터 코드 해석까지

---

### 실행 환경

- Python 3.10 이상 권장 (match-case 등 일부 문법 포함)
- 코드 예제는 모두 독립 실행 가능하게 작성됨

### 라이브러리 설치

```bash
# 가상환경 만들기 (프로젝트별로 패키지 환경을 분리)
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows

# 패키지 설치
pip install numpy matplotlib
```

> **가상환경이 필요한 이유:**  
> 프로젝트마다 필요한 라이브러리 버전이 다를 수 있습니다. 가상환경을 쓰면 프로젝트 A는 numpy 1.24, 프로젝트 B는 numpy 2.0을 따로 유지할 수 있습니다. `.venv` 폴더는 git에 올리지 않는 게 관례입니다.

### requirements.txt

다른 사람이나 다른 환경에서 **같은 패키지를 그대로 설치**할 수 있게 목록을 기록해두는 파일입니다.

#### 만들기 — 가상환경 안에서 해야 합니다

```bash
# 가상환경을 먼저 활성화한 뒤
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate         # Windows

# 현재 설치된 패키지 전체를 기록
pip freeze > requirements.txt
```

`pip freeze`는 **현재 활성화된 환경**의 패키지 목록을 출력합니다. 가상환경 밖(전역 환경)에서 실행하면 시스템에 설치된 모든 패키지가 섞여 들어가 지저분해집니다. **반드시 가상환경 안에서 실행하세요.**

결과 파일은 이런 형태입니다.

```
numpy==2.0.1
matplotlib==3.9.2
```
#### 설치하기 — 가상환경 안에서 해야 합니다

```bash
# 가상환경 활성화 후
pip install -r requirements.txt
```

이것도 가상환경 밖에서 실행하면 전역 환경에 설치되므로, 활성화 여부를 확인하고 실행하세요.

#### 한눈에 정리

| 작업 | 가상환경 필요? |
|------|---------------|
| `pip freeze > requirements.txt` (자동 생성) | **필요** (안 하면 전역 패키지까지 포함됨) |
| 에디터로 직접 작성/수정 | 불필요 (그냥 텍스트 파일) |
| `pip install -r requirements.txt` (설치) | **필요** (안 하면 전역 환경에 설치됨) |

> **팁:** `pip freeze`는 설치된 모든 패키지를 담기 때문에 간접 의존성(내가 설치한 패키지가 내부적으로 쓰는 패키지)까지 전부 들어갑니다. 내가 직접 쓰는 패키지만 깔끔하게 관리하고 싶다면 `pip-tools` 같은 도구를 쓰기도 합니다.

---

## 목차

1. [자료형과 객체 개념](#1-자료형과-객체-개념)
2. [흐름 제어](#2-흐름-제어)
3. [함수와 스코프](#3-함수와-스코프)
4. [예외 처리와 파일 처리](#4-예외-처리와-파일-처리)
5. [클래스와 객체지향](#5-클래스와-객체지향)
6. [NumPy 배열 연산](#6-numpy-배열-연산)
7. [Matplotlib 시각화](#7-matplotlib-시각화)

---

## 1. 자료형과 객체 개념

### Python에서 변수는 "이름표"다

Python에서 변수는 값을 담는 상자가 아니라 객체에 붙이는 **이름표**입니다.  
`a = [1, 2, 3]`이라고 쓰면 `[1, 2, 3]`이라는 리스트 객체가 메모리에 만들어지고, `a`는 그 객체를 가리킵니다.

```python
a = [1, 2, 3]
b = a           # b도 같은 객체를 가리킴 (복사가 아님)

b.append(4)
print(a)        # [1, 2, 3, 4] ← a도 바뀜
```

이 이름표 개념을 이해하면 복사, 함수 인자 전달, 클래스 등 여러 곳에서 생기는 혼란이 해소됩니다.

---

### mutable vs immutable

Python의 모든 객체는 값을 바꿀 수 있는지 여부로 나뉩니다.

| 종류 | 타입 |
|------|------|
| **immutable** (변경 불가) | `int`, `float`, `str`, `bool`, `tuple`, `frozenset` |
| **mutable** (변경 가능) | `list`, `dict`, `set`, 대부분의 클래스 인스턴스 |

immutable 객체는 "수정"처럼 보이는 연산도 실제로는 새 객체를 만듭니다.

```python
x = "hello"
x += " world"   # x가 수정된 게 아니라, 새 문자열 객체가 만들어지고 x가 그걸 가리킴

nums = [1, 2, 3]
nums.append(4)  # 이건 진짜 수정. 같은 객체가 바뀜
```

이 차이가 중요한 이유는 **함수에 인자를 넘길 때** 드러납니다.

```python
def modify_list(lst):
    lst.append(99)      # 원본 객체를 직접 수정

def modify_int(n):
    n = n + 1           # 새 객체를 만들어 n에 붙임. 외부 변수는 그대로

my_list = [1, 2, 3]
my_num  = 10

modify_list(my_list)
modify_int(my_num)

print(my_list)  # [1, 2, 3, 99] ← 바뀜
print(my_num)   # 10             ← 안 바뀜
```

---

### `is` vs `==`

초보자가 자주 혼동하는 두 연산자입니다.

- `==` : **값**이 같은지 비교
- `is` : **같은 객체**인지 비교 (메모리 주소가 동일한지)

```python
a = [1, 2, 3]
b = [1, 2, 3]

print(a == b)   # True  ← 값은 같음
print(a is b)   # False ← 다른 객체

c = a
print(a is c)   # True  ← 같은 객체를 가리킴
```

`is`를 쓰는 경우는 주로 `None` 체크입니다.  
`== None` 대신 `is None`을 쓰는 게 관례이고 더 정확합니다.

```python
result = some_function()

if result is None:      # 권장
    print("결과 없음")

if result == None:      # 비권장 (None과 == 비교를 커스터마이징한 객체에서 오작동 가능)
    print("결과 없음")
```

---

### 기본 자료형

#### int / float

```python
x = 10
y = 3.14

# 산술 연산
x + y       # 13.14
x / y       # 3.184...  (나누기는 항상 float 반환)
x // 3      # 3   (정수 몫)
x % 3       # 1   (나머지)
2 ** 8      # 256 (거듭제곱)

# int()는 "0 방향으로 버림"
int(3.9)    # 3   (소수점 아래 버림)
int(-3.9)   # -3  (음수도 0 방향, -4가 아님)

# math.floor()는 진짜 내림 (음수에서 차이 남)
import math
math.floor(-3.9)   # -4
math.ceil(-3.9)    # -3
round(3.567, 2)    # 3.57
abs(-5)            # 5
```

#### str

문자열은 immutable입니다. `.replace()`, `.upper()` 같은 메서드는 원본을 바꾸지 않고 **새 문자열을 반환**합니다.

```python
s = "  Hello, World!  "

s.strip()               # "Hello, World!"    (앞뒤 공백 제거)
s.upper()               # "  HELLO, WORLD!  "
s.replace("World", "Python")  # "  Hello, Python!  "
s.strip().split(", ")   # ['Hello', 'World!']
"-".join(["a", "b", "c"])     # "a-b-c"

s.find("World")         # 8   (없으면 -1)
s.startswith("  H")     # True
s.count("l")            # 3

# 포매팅 — f-string이 현재 표준
name, score = "철수", 95.5
f"{name}의 점수: {score:.1f}"     # "철수의 점수: 95.5"
f"{score:>10.2f}"                 # "     95.50"  (너비 10, 오른쪽 정렬)
f"{1000000:,}"                    # "1,000,000"

# 슬라이싱 — 문자열도 시퀀스
s = "abcdefg"
s[2:5]      # "cde"
s[::-1]     # "gfedcba" (역순)
```

---

### 컬렉션 자료형

#### list

순서가 있고 수정 가능한 시퀀스입니다. Python에서 가장 자주 쓰이는 컬렉션입니다.

```python
nums = [3, 1, 4, 1, 5, 9]

# 추가 / 삽입 / 삭제
nums.append(2)          # 끝에 추가
nums.insert(2, 99)      # 인덱스 2 위치에 삽입
nums.extend([10, 11])   # 여러 개 한 번에 추가
nums.pop()              # 마지막 꺼내기 (반환 후 삭제)
nums.pop(0)             # 인덱스 0 꺼내기
nums.remove(1)          # 값 1 첫 번째 삭제

# 정렬 — sort()와 sorted()의 차이
nums.sort()             # 원본 수정
nums.sort(reverse=True)
new = sorted(nums)      # 원본 유지, 새 리스트 반환

# 슬라이싱
nums[1:4]               # 인덱스 1,2,3
nums[-3:]               # 뒤에서 3개
nums[::2]               # 2칸씩 건너뜀

# 리스트 컴프리헨션 — for 루프를 한 줄로 표현
squares = [x**2 for x in range(10)]
evens   = [x for x in range(20) if x % 2 == 0]

# 중첩 컴프리헨션 (2D 행렬 생성)
matrix = [[i * j for j in range(1, 4)] for i in range(1, 4)]
# → [[1,2,3], [2,4,6], [3,6,9]]

# 살짝 괴랄한 예제 1 — 문자열에서 모음만 뽑아 위치와 함께 저장
vowels = [(idx, ch) for idx, ch in enumerate("comprehension") if ch in "aeiou"]
# → [(1, 'o'), (4, 'e'), (7, 'e'), (10, 'i'), (11, 'o')]

# 살짝 괴랄한 예제 2 — 2중 루프 + 조건을 한 줄에서 처리
pairs = [(x, y) for x in range(5) for y in range(5) if x != y and (x + y) % 2 == 0]
# → [(0, 2), (0, 4), (1, 3), (2, 0), ...]
```

#### tuple

리스트와 비슷하지만 immutable입니다.  
"이 값들은 함께 묶여서 바뀌지 않아야 한다"는 의도를 코드로 표현할 때 씁니다.  
좌표, 설정값, 함수의 다중 반환값 등에 자주 사용됩니다.

```python
point = (10, 20)
x, y = point            # 언패킹

# 확장 언패킹
first, *rest = (1, 2, 3, 4, 5)   # first=1, rest=[2,3,4,5]
a, *mid, b   = (1, 2, 3, 4, 5)   # a=1, mid=[2,3,4], b=5

# 네임드 튜플 — 인덱스 대신 이름으로 접근
from collections import namedtuple
Point = namedtuple("Point", ["x", "y"])
p = Point(3, 7)
print(p.x, p.y)    # 3 7
print(p[0])        # 3 (인덱스도 사용 가능)
```

#### dict

키-값 쌍의 컬렉션입니다. Python 3.7부터 삽입 순서를 보장합니다.  
실전 코드에서 JSON 데이터, 설정값, 객체 속성 등 어디서나 등장합니다.

```python
person = {"name": "철수", "age": 25}

person["name"]                   # "철수"
person.get("phone", "없음")      # 없는 키 → 기본값 반환 (KeyError 없음)
person.update({"age": 26, "city": "서울"})  # 여러 개 수정/추가
person.pop("city")               # 삭제 후 값 반환

# 순회
for key, value in person.items():
    print(f"{key}: {value}")

# 딕셔너리 컴프리헨션
squares = {x: x**2 for x in range(5)}
# → {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# defaultdict — 없는 키 접근 시 자동으로 기본값 생성
from collections import defaultdict

word_count = defaultdict(int)
for word in ["a", "b", "a", "c", "a"]:
    word_count[word] += 1    # 없는 키여도 KeyError 없이 0으로 시작
```

#### set

순서 없고 중복 없는 컬렉션입니다.  
"이 값이 목록에 있는가"를 빠르게 체크하거나, 중복을 제거할 때 유용합니다.

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

a & b           # {3, 4}          교집합
a | b           # {1,2,3,4,5,6}   합집합
a - b           # {1, 2}          차집합
a ^ b           # {1, 2, 5, 6}    대칭 차집합

# 중복 제거 — 순서 보장 안 됨
unique = list(set([1, 2, 2, 3, 3, 3]))

# 포함 여부 체크 (리스트보다 훨씬 빠름)
allowed = {"admin", "user", "guest"}
role = "admin"
if role in allowed:
    print("접근 허용")
```

---

### 얕은 복사 vs 깊은 복사

변수 이름표 개념을 이해했다면 이 부분이 훨씬 명확하게 보입니다.

#### 얕은 복사 (Shallow Copy)

새 컨테이너 객체를 만들지만, **내부 원소는 여전히 원본과 같은 객체를 가리킵니다.**

```python
import copy

original = [1, 2, [10, 20]]

shallow = original.copy()   # 또는 original[:] 또는 copy.copy(original)

# 외부 리스트는 독립
shallow.append(99)
print(original)     # [1, 2, [10, 20]]  ← 영향 없음

# 내부 리스트는 여전히 공유
shallow[2].append(30)
print(original)     # [1, 2, [10, 20, 30]]  ← 내부까지 바뀜!
```

#### 깊은 복사 (Deep Copy)

중첩 구조를 포함해 모든 객체를 **완전히 새로 만듭니다.**

```python
import copy

original = [1, 2, [10, 20]]
deep = copy.deepcopy(original)

deep[2].append(30)
print(original)   # [1, 2, [10, 20]]      ← 전혀 영향 없음
print(deep)       # [1, 2, [10, 20, 30]]
```

#### 언제 무엇을 쓸까

| | `b = a` | 얕은 복사 | 깊은 복사 |
|---|---|---|---|
| 새 컨테이너 | ✗ | ✓ | ✓ |
| 내부 원소 독립 | ✗ | ✗ | ✓ |
| 사용 시점 | 같은 객체를 참조만 | 중첩 없는 단순 리스트/딕셔너리 | 중첩 구조가 있고 완전 독립 필요 |

dict도 동일합니다.

```python
import copy

original = {"scores": [85, 92, 78]}

shallow = original.copy()
shallow["scores"].append(100)
print(original)   # {"scores": [85, 92, 78, 100]}  ← 공유됨

deep = copy.deepcopy(original)
deep["scores"].append(999)
print(original)   # {"scores": [85, 92, 78, 100]}  ← 변화 없음
```

---

### 자료형 변환

```python
int("42")           # 42
int(3.9)            # 3   (0 방향으로 버림)
int(-3.9)           # -3  (음수도 0 방향)
float("3.14")       # 3.14
str(100)            # "100"
bool(0)             # False  ← 0, "", [], {}, set(), None 은 모두 False
bool("hello")       # True   ← 나머지는 True

list((1, 2, 3))     # [1, 2, 3]
tuple([1, 2, 3])    # (1, 2, 3)
set([1, 1, 2, 2])   # {1, 2}
dict([("a", 1), ("b", 2)])   # {"a": 1, "b": 2}
```

---

## 2. 흐름 제어

### if / elif / else

```python
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"

# 삼항 연산자 — 단순한 if-else를 한 줄로
grade = "합격" if score >= 60 else "불합격"
```

---

### for

Python의 `for`는 "인덱스로 순회"가 아니라 **이터러블 객체를 직접 순회**합니다.  
인덱스가 필요하면 `enumerate()`, 두 리스트를 동시에 돌려야 하면 `zip()`을 씁니다.

```python
fruits = ["사과", "바나나", "딸기"]

# 인덱스 없이
for fruit in fruits:
    print(fruit)

# 인덱스도 필요하면 enumerate
for i, fruit in enumerate(fruits, start=1):
    print(f"{i}. {fruit}")

# 두 리스트 동시에
names  = ["철수", "영희", "민준"]
scores = [85, 92, 78]
for name, score in zip(names, scores):
    print(f"{name}: {score}")

# range
for i in range(0, 10, 2):   # 0, 2, 4, 6, 8
    print(i)
```

#### for-else

`for`문이 `break` 없이 끝까지 완료되면 `else` 블록이 실행됩니다.  
"찾았는지 못 찾았는지"를 플래그 변수 없이 처리할 때 유용합니다.

```python
targets = [3, 7, 15, 22]
needle = 15

for n in targets:
    if n == needle:
        print("찾았다!")
        break
else:
    print("없다")   # break가 실행되지 않으면 여기 옴
```

---

### while

종료 시점을 조건으로 표현하기 어려울 때, 또는 이벤트 기반 루프에 씁니다.

```python
count = 0
while count < 5:
    print(count)
    count += 1

# 무한 루프 + break — 메뉴/CLI 프로그램의 기본 구조
while True:
    cmd = input("> ")
    if cmd == "q":
        break
    print(f"입력: {cmd}")
```

---

### break / continue / pass

세 개 모두 루프 제어에 쓰이지만 역할이 다릅니다.

```python
# break — 루프 자체를 빠져나감
for i in range(10):
    if i == 5:
        break     # i가 5가 되는 순간 for 전체 종료
    print(i)      # 0, 1, 2, 3, 4

# continue — 이번 반복만 건너뜀
for i in range(10):
    if i % 2 == 0:
        continue  # 짝수는 건너뜀
    print(i)      # 1, 3, 5, 7, 9

# pass — 아무것도 하지 않음 (문법적으로 블록이 필요한 자리를 채울 때)
for i in range(10):
    pass    # 나중에 구현할 예정이라 일단 비워둠

def placeholder():
    pass    # 함수 정의만 해두고 구현은 나중에

class Empty:
    pass    # 나중에 채울 클래스
```

`pass`는 "지금은 구현 안 했지만 이 구조가 필요하다"는 의미로 씁니다.  
실전 코드에서 추상 클래스나 기반 클래스 정의에 자주 등장합니다.

---

### 컴프리헨션

반복문 + 조건을 한 줄로 표현하는 문법입니다.  
코드가 짧아지고 실제로 약간 더 빠릅니다. 단, 너무 복잡해지면 오히려 가독성이 떨어지니 단순한 경우에만 쓰세요.

```python
# 리스트 컴프리헨션
squares = [x**2 for x in range(10)]
evens   = [x for x in range(20) if x % 2 == 0]

# 딕셔너리 컴프리헨션
word_len = {w: len(w) for w in ["apple", "banana", "kiwi"]}
# → {'apple': 5, 'banana': 6, 'kiwi': 4}

# 셋 컴프리헨션
lengths = {len(w) for w in ["apple", "banana", "kiwi"]}
# → {4, 5, 6}

# 조금 더 괴랄한 리스트 컴프리헨션
weird = ["짝수" if x % 2 == 0 else "홀수" for x in range(7) if x != 3]
# → ['짝수', '홀수', '짝수', '짝수', '홀수', '짝수']
# 해석: 0~6 중에서 3은 제외하고, 남은 숫자를 짝수/홀수 문자열로 바꾼다

# 2차원 데이터를 평탄화하면서 조건까지 걸기
flat_even = [n for row in [[1, 2, 3], [4, 5], [6, 7, 8]] for n in row if n % 2 == 0]
# → [2, 4, 6, 8]

# 딕셔너리 컴프리헨션에 조건식까지 섞기
grade_map = {name: ("pass" if score >= 60 else "fail")
             for name, score in {"kim": 91, "lee": 58, "park": 77}.items()}
# → {'kim': 'pass', 'lee': 'fail', 'park': 'pass'}

# 제너레이터 표현식 — () 사용, 즉시 계산 안 하고 필요할 때마다 하나씩 생성
gen = (x**2 for x in range(1_000_000))   # 메모리 거의 안 씀
next(gen)    # 0
next(gen)    # 1
```

---

### match-case (Python 3.10+)

`if-elif` 체인을 더 명확하게 표현할 수 있습니다. 특히 명령어나 상태를 분기할 때 유용합니다.

```python
command = "start"

match command:
    case "start":
        print("시작")
    case "stop":
        print("정지")
    case "pause" | "wait":   # OR 조건
        print("일시정지")
    case _:                  # 기본값 (if의 else에 해당)
        print("알 수 없는 명령")
```

---

## 3. 함수와 스코프

### 함수가 코드에서 어떤 역할을 하는가

긴 코드를 읽다 보면 `def`로 시작하는 블록이 많이 등장합니다.  
함수는 크게 세 가지 이유로 씁니다.

1. **반복되는 코드를 하나로** — 같은 로직을 여러 곳에서 쓸 때
2. **복잡한 로직을 이름으로 감추기** — 세부 구현을 숨기고 의도만 드러내기
3. **입력 → 출력 관계를 명확히** — 어떤 데이터를 받아서 어떤 결과를 내는지

코드를 읽을 때 함수 이름과 인자/반환값을 먼저 보면 내부 구현을 몰라도 전체 흐름을 파악할 수 있습니다.

---

### lambda (람다 함수)

`lambda`는 이름 없는 짧은 함수를 만들 때 씁니다.  
한 줄짜리 간단한 함수를 잠깐 넘겨야 할 때 유용하지만, 로직이 길어지면 그냥 `def`를 쓰는 편이 더 읽기 쉽습니다.

```python
# 일반 함수
def add_one(x):
    return x + 1

# 같은 내용을 lambda로 표현
add_one = lambda x: x + 1

print(add_one(10))   # 11

# sorted에서 자주 사용
words = ["apple", "kiwi", "banana"]
print(sorted(words, key=lambda w: len(w)))
# → ['kiwi', 'apple', 'banana']

# 튜플의 두 번째 값을 기준으로 정렬
pairs = [("a", 3), ("b", 1), ("c", 2)]
print(sorted(pairs, key=lambda x: x[1]))
# → [('b', 1), ('c', 2), ('a', 3)]

# map / filter 와도 함께 자주 등장
nums = [1, 2, 3, 4, 5]
print(list(map(lambda x: x * 10, nums)))          # [10, 20, 30, 40, 50]
print(list(filter(lambda x: x % 2 == 0, nums)))   # [2, 4]
```

주의할 점:

- `lambda` 안에는 `return`을 쓰지 않습니다. 식(expression) 하나의 결과가 곧 반환값입니다.
- 조건식은 가능하지만 여러 줄짜리 복잡한 로직에는 잘 안 어울립니다.
- 실무에서는 `sorted(..., key=...)` 같은 곳에서 가장 자주 보게 됩니다.

```python
# 가능은 하지만 읽기 어려운 예
label = lambda x: "big" if x >= 10 else "small"

# 이런 경우는 def가 더 읽기 편함
def label(x):
    if x >= 10:
        return "big"
    return "small"
```

---

### 인자 종류

```python
# 위치 인자 (positional)
def add(a, b):
    return a + b

add(1, 2)        # a=1, b=2

# 기본값 인자 (default)
def greet(name, msg="안녕"):
    return f"{msg}, {name}!"

greet("철수")         # "안녕, 철수!"
greet("철수", "반가워") # "반가워, 철수!"

# 키워드 인자 (keyword) — 호출할 때 이름으로 전달
greet(msg="오랜만", name="영희")

# 키워드 전용 인자 (* 이후는 반드시 키워드로 넘겨야 함)
def connect(host, *, port=80, timeout=30):
    pass

connect("localhost", port=443)    # OK
connect("localhost", 443)         # TypeError
```

---

### *args / **kwargs 상세

#### *args — 여러 위치 인자를 튜플로 받기

```python
def total(*args):
    print(args)        # 튜플로 들어옴
    return sum(args)

total(1, 2, 3)         # args = (1, 2, 3)
total(10, 20)          # args = (10, 20)
total()                # args = ()  빈 튜플도 OK
```

튜플이니까 인덱싱, 루프, len() 다 됩니다.

```python
def describe(*args):
    print(f"총 {len(args)}개")
    for i, v in enumerate(args):
        print(f"  {i}번째: {v}")

describe("사과", "바나나", "딸기")
# 총 3개
#   0번째: 사과
#   1번째: 바나나
#   2번째: 딸기
```

#### **kwargs — 여러 키워드 인자를 딕셔너리로 받기

```python
def config(**kwargs):
    print(kwargs)       # 딕셔너리로 들어옴

config(host="localhost", port=8080, debug=True)
# {'host': 'localhost', 'port': 8080, 'debug': True}
```

딕셔너리니까 `.items()`, `.get()`, `in` 다 됩니다.

```python
def setup(**kwargs):
    host    = kwargs.get("host", "localhost")   # 없으면 기본값
    port    = kwargs.get("port", 80)
    debug   = kwargs.get("debug", False)

    print(f"{host}:{port} (debug={debug})")

setup(host="192.168.0.1", port=443)
# 192.168.0.1:443 (debug=False)
```

#### 일반 인자와 함께 쓸 때 — 순서가 중요

인자 선언 순서는 반드시 이 순서를 따라야 합니다.

```
def 함수(일반인자, *args, **kwargs)
```

```python
def log(level, *messages, **options):
    # level   → 일반 위치 인자 (첫 번째 값)
    # messages → 그 이후 위치 인자들 (튜플)
    # options  → 키워드 인자들 (딕셔너리)

    print(f"[{level}]", " | ".join(messages))
    for k, v in options.items():
        print(f"  {k}: {v}")

log("INFO", "서버 시작", "포트 열림", time="12:00", pid=1234)
# [INFO] 서버 시작 | 포트 열림
#   time: 12:00
#   pid: 1234
```

어떤 값이 어디로 가는지 순서대로 보면:
- `"INFO"` → `level` (첫 번째 일반 인자)
- `"서버 시작"`, `"포트 열림"` → `messages` (나머지 위치 인자들)
- `time=...`, `pid=...` → `options` (키워드 인자들)

#### 일반 인자 + *args 조합 — 가장 흔한 패턴

첫 번째 인자는 이름으로 고정하고, 나머지를 `*args`로 받는 형태입니다.

```python
def oper_to_str(opr, *args):
    # opr  → 연산자 기호 (첫 번째 값)
    # args → 나머지 숫자들 (튜플)
    result = f" {opr} ".join(str(x) for x in args)
    print(result)

oper_to_str("+", 1, 2, 3)     # "1 + 2 + 3"
oper_to_str("*", 4, 5)        # "4 * 5"
oper_to_str("-", 10, 3, 2)    # "10 - 3 - 2"
```

`args` 안의 값들은 튜플이라 그냥은 계산이 안 되고, 직접 꺼내서 써야 합니다.

```python
def calculate(opr, *args):
    if opr == "+":
        return sum(args)
    if opr == "*":
        result = 1
        for n in args:
            result *= n
        return result

calculate("+", 1, 2, 3, 4)   # 10
calculate("*", 2, 3, 4)      # 24
```

#### 세 가지 조합 한눈에 보기

```python
def 주문(매장, *메뉴, **옵션):
    print(f"매장: {매장}")
    print(f"메뉴: {메뉴}")
    print(f"옵션: {옵션}")

주문("강남점", "아메리카노", "라떼", 샷추가=True, 온도="hot")
# 매장: 강남점
# 메뉴: ('아메리카노', '라떼')
# 옵션: {'샷추가': True, '온도': 'hot'}
```

- `"강남점"` → `매장` (첫 번째 고정 인자)
- `"아메리카노"`, `"라떼"` → `*메뉴` (값만 넘긴 것)
- `샷추가=True`, `온도="hot"` → `**옵션` (이름=값 으로 넘긴 것)

#### `*`로 리스트/튜플 풀어서 넘기기, `**`로 딕셔너리 풀어서 넘기기

반대로 **이미 있는 리스트나 딕셔너리를 인자로 풀어서 넘길 때**도 `*`, `**`를 씁니다.

```python
def add(a, b, c):
    return a + b + c

nums = [1, 2, 3]
add(*nums)          # add(1, 2, 3) 과 동일

params = {"a": 1, "b": 2, "c": 3}
add(**params)       # add(a=1, b=2, c=3) 과 동일
```

```python
# 실전 예 — 함수에 설정값 딕셔너리를 그대로 넘기기
settings = {"host": "localhost", "port": 443, "debug": True}
setup(**settings)   # setup(host="localhost", port=443, debug=True) 와 동일
```

---

### 타입 힌트

실행에는 영향 없지만 **코드를 읽는 사람에게 의도를 전달**합니다.  
AI 생성 코드나 라이브러리 코드에 자주 등장하니 읽을 줄 알아야 합니다.

```python
def add(a: int, b: int) -> int:
    return a + b

def greet(name: str, times: int = 1) -> str:
    return name * times

# 복잡한 타입은 typing 모듈 사용
from typing import List, Dict, Optional, Union, Tuple

def process(data: List[int]) -> Dict[str, int]:
    return {"sum": sum(data), "count": len(data)}

# Optional[X]는 X 또는 None
def find_user(name: str) -> Optional[str]:
    return None   # 못 찾으면 None 반환

# Union[X, Y]는 X 또는 Y
def calc(x: Union[int, float]) -> float:
    return float(x)
```

---

### 스코프 — local / global / nonlocal

변수가 어느 범위에서 유효한지를 스코프라고 합니다.  
Python은 변수를 찾을 때 **지역(local) → 감싸는 함수(enclosing) → 전역(global) → 내장(built-in)** 순서로 탐색합니다.

```python
x = 10   # 전역 변수

def outer():
    y = 20   # outer의 지역 변수

    def inner():
        z = 30   # inner의 지역 변수
        print(x, y, z)   # x, y는 바깥에서 읽기는 가능

    inner()

outer()
```

**바깥 변수를 함수 안에서 수정하고 싶으면** `global` 또는 `nonlocal`을 명시해야 합니다.

```python
count = 0

def increment():
    global count     # 전역 변수를 수정하겠다고 선언
    count += 1

increment()
print(count)   # 1
```

```python
def make_counter():
    count = 0

    def counter():
        nonlocal count   # 바로 바깥 함수의 변수를 수정
        count += 1
        return count

    return counter

c = make_counter()
c()   # 1
c()   # 2
c()   # 3
```

`global`은 전역 상태를 함수가 수정하므로 코드가 복잡해지면 추적하기 어렵습니다. 가능하면 함수가 값을 반환하는 방식을 선호하세요.

---

### 클로저

클로저는 **함수가 자신이 만들어질 때의 변수 환경을 기억하는 패턴**입니다.  
위의 `make_counter`가 클로저입니다. 바깥 함수가 끝났음에도 `count`가 사라지지 않고 `counter` 함수 안에 살아 있습니다.

실전 코드에서는 설정값을 고정한 함수를 만들 때 자주 씁니다.

```python
def make_multiplier(factor):
    def multiply(x):
        return x * factor   # factor는 make_multiplier의 변수였지만 기억됨
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)

double(5)   # 10
triple(5)   # 15

# double과 triple은 각각 다른 factor를 기억하는 함수
```

---

### 데코레이터

데코레이터는 **함수를 감싸서 기능을 추가하는 패턴**입니다.  
`@데코레이터` 문법은 `func = 데코레이터(func)`의 줄임입니다.

AI 생성 코드나 프레임워크 코드에 자주 등장하니 구조를 이해해두면 읽기 편합니다.

```python
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)              # 원래 함수 실행
        print(f"{func.__name__}: {time.time() - start:.4f}초")
        return result
    return wrapper

@timer
def slow_task():
    time.sleep(0.5)
    return "완료"

slow_task()
# slow_task: 0.5002초
```

`@timer`는 `slow_task = timer(slow_task)`와 완전히 동일합니다.  
데코레이터 덕분에 `slow_task` 함수 코드를 건드리지 않고 기능을 추가할 수 있습니다.

인자를 받는 데코레이터는 한 겹 더 감쌉니다.

```python
def repeat(n):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(n):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(3)
def hello():
    print("안녕!")

hello()   # "안녕!" 3번 출력
```

---

### 제너레이터

제너레이터는 **값을 한 번에 전부 만들지 않고, 필요할 때 하나씩 만들어주는 함수**입니다.  
`return` 대신 `yield`를 씁니다.

백만 개짜리 리스트를 만들면 메모리에 전부 올라가지만, 제너레이터는 요청할 때마다 하나씩 계산하므로 메모리를 거의 쓰지 않습니다.

```python
def countdown(n):
    while n > 0:
        yield n      # 여기서 값을 내보내고 일시 중단. 다음 호출 시 여기서 재개
        n -= 1

for x in countdown(5):
    print(x)     # 5, 4, 3, 2, 1

# next()로 하나씩 꺼낼 수도 있음
gen = countdown(3)
next(gen)   # 3
next(gen)   # 2
next(gen)   # 1
next(gen)   # StopIteration 발생

# 실용 예 — 대용량 파일 한 줄씩 처리
def read_lines(filepath):
    with open(filepath) as f:
        for line in f:
            yield line.strip()

for line in read_lines("data.txt"):
    process(line)   # 파일 전체를 메모리에 올리지 않고 처리
```

---

### 모듈과 import

하나의 `.py` 파일이 모듈입니다. 여러 모듈을 묶은 폴더가 패키지입니다.

```python
# 모듈 전체 가져오기
import math
math.sqrt(16)    # 4.0

# 특정 이름만 가져오기
from math import sqrt, pi
sqrt(16)         # 4.0

# 별칭 붙이기 (긴 이름을 짧게)
import numpy as np
from collections import defaultdict as ddict

# 같은 폴더의 내 파일 가져오기
# utils.py 파일이 있다면:
from utils import some_function
```

표준 라이브러리(math, os, json, collections 등)는 별도 설치 없이 바로 씁니다.  
외부 라이브러리(numpy, pandas 등)는 `pip install`로 설치합니다.

```bash
pip install numpy          # 설치
pip list                   # 설치된 패키지 목록
pip freeze > requirements.txt   # 현재 환경 기록 (공유/배포용)
pip install -r requirements.txt  # 기록된 환경 그대로 설치
```

---

## 4. 예외 처리와 파일 처리

### 왜 예외 처리가 필요한가

코드를 실행하다 보면 예상치 못한 상황이 생깁니다. 파일이 없거나, 사용자 입력이 잘못되거나, 네트워크가 끊어지거나.  
예외 처리는 이런 상황을 **프로그램이 멈추지 않고 대응하게** 만드는 구조입니다.

---

### 기본 구조

```python
try:
    result = 10 / int(input("숫자를 입력: "))
except ValueError:
    print("숫자가 아닙니다")
except ZeroDivisionError:
    print("0으로 나눌 수 없습니다")
else:
    print(f"결과: {result}")   # 예외가 없었을 때만 실행
finally:
    print("항상 실행")          # 예외 여부와 관계없이 무조건 실행 (정리 작업에 사용)
```

`else`는 자주 생략하지만, "성공했을 때만 실행할 코드"를 `try` 블록에서 분리할 때 씁니다.  
`finally`는 파일이나 네트워크 연결처럼 **반드시 닫아야 하는 자원**을 정리할 때 주로 씁니다.

---

### 예외 정보 꺼내기 / 여러 예외 묶기

```python
try:
    x = int("abc")
except ValueError as e:
    print(f"오류: {e}")       # invalid literal for int() with base 10: 'abc'
    print(type(e).__name__)   # ValueError

# 여러 예외를 하나로 묶기
try:
    data = {}
    print(data["key"])
except (KeyError, IndexError) as e:
    print(f"접근 오류: {e}")
```

---

### with 문 — 자원 관리

`with` 블록을 벗어나면 자원이 **자동으로 정리**됩니다. 파일, 네트워크 연결, DB 연결 등에 씁니다.

```python
# finally로 직접 닫는 방식
f = None
try:
    f = open("data.txt", "r", encoding="utf-8")
    content = f.read()
except FileNotFoundError:
    print("파일 없음")
finally:
    if f:
        f.close()

# with 문으로 간결하게 (권장)
try:
    with open("data.txt", "r", encoding="utf-8") as f:
        content = f.read()
except FileNotFoundError:
    print("파일 없음")
```

---

### 파일 I/O

```python
# 쓰기
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("첫 번째 줄\n")
    f.write("두 번째 줄\n")

# 이어 쓰기
with open("output.txt", "a", encoding="utf-8") as f:
    f.write("추가 줄\n")

# 읽기
with open("output.txt", "r", encoding="utf-8") as f:
    content = f.read()       # 전체 문자열로
    # 또는
    lines = f.readlines()    # 줄 단위 리스트로

# 한 줄씩 처리 (큰 파일에 적합)
with open("output.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())

# JSON 읽고 쓰기
import json

data = {"name": "철수", "scores": [85, 92, 78]}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

with open("data.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)
```

| 모드 | 의미 |
|------|------|
| `"r"` | 읽기 (파일 없으면 오류) |
| `"w"` | 쓰기 (파일 있으면 덮어씀) |
| `"a"` | 이어쓰기 |
| `"x"` | 생성 (파일 이미 있으면 오류) |

---

### 예외 다시 던지기 / 커스텀 예외

```python
# re-raise — 로그를 남기고 예외를 위로 전달
def load_config(path):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"설정 파일 없음: {path}")
        raise   # 원래 예외를 그대로 위로 전달

# 다른 예외로 변환
def parse_age(s):
    try:
        return int(s)
    except ValueError as e:
        raise TypeError(f"나이는 정수여야 합니다: {s!r}") from e
```

```python
# 커스텀 예외 — 속성 포함
class ValidationError(Exception):
    def __init__(self, field, message):
        super().__init__(f"[{field}] {message}")
        self.field = field

# 계층 구조로 묶기
class DatabaseError(Exception): pass
class ConnectionError(DatabaseError): pass
class QueryError(DatabaseError): pass

try:
    raise ConnectionError("연결 실패")
except DatabaseError as e:    # 부모 클래스로 묶어서 잡기
    print(e)
```

---

### assert — 검증 습관

`assert`는 "이 조건이 반드시 참이어야 한다"는 내부 검증입니다.  
주로 함수 입력이나 중간 상태를 확인할 때 씁니다.

```python
def set_age(age):
    assert isinstance(age, int), f"age는 int여야 합니다, 받은 값: {type(age)}"
    assert 0 <= age <= 150, f"나이 범위 오류: {age}"
    return age
```

`AssertionError`를 발생시키며, Python을 `-O` 옵션으로 실행하면 무시됩니다.  
따라서 사용자 입력 검증처럼 항상 작동해야 하는 곳에는 쓰지 말고, **개발 중 내부 논리 확인용**으로 씁니다.

---

### 자주 쓰는 예외 종류

| 예외 | 발생 상황 |
|------|-----------|
| `ValueError` | 잘못된 값 (`int("abc")`) |
| `TypeError` | 잘못된 타입 연산 (`"1" + 1`) |
| `IndexError` | 리스트 범위 초과 |
| `KeyError` | 딕셔너리 키 없음 |
| `ZeroDivisionError` | 0으로 나누기 |
| `FileNotFoundError` | 파일 없음 |
| `AttributeError` | 없는 속성/메서드 호출 |
| `NameError` | 정의되지 않은 변수 사용 |
| `ImportError` | 모듈 import 실패 |
| `RecursionError` | 재귀 깊이 초과 |

---

## 5. 클래스와 객체지향

### 클래스가 코드에서 어떤 역할을 하는가

클래스는 **관련된 데이터와 함수를 하나로 묶는 구조**입니다.  
긴 코드에서 클래스를 보면 이렇게 읽으세요.

- `class` 이름: 이게 다루는 개념이 무엇인지
- `__init__`: 생성될 때 어떤 초기 상태를 가지는지
- 메서드들: 이 객체가 할 수 있는 동작이 무엇인지

함수가 "동작"을 표현한다면, 클래스는 "동작을 가진 사물"을 표현합니다.

---

### 클래스 변수 vs 인스턴스 변수

```python
class Dog:
    species = "Canis familiaris"   # 클래스 변수: 모든 인스턴스가 공유
    count = 0

    def __init__(self, name, age):
        self.name = name   # 인스턴스 변수: 각 인스턴스마다 독립
        self.age = age
        Dog.count += 1     # 클래스 변수는 클래스명으로 접근 권장

dog1 = Dog("초코", 3)
dog2 = Dog("콩이", 1)

print(dog1.species)  # "Canis familiaris"  ← 공유
print(dog2.species)  # "Canis familiaris"  ← 같은 값
print(dog1.name)     # "초코"              ← 개별
print(dog2.name)     # "콩이"              ← 다른 값
print(Dog.count)     # 2
```

| | 클래스 변수 | 인스턴스 변수 |
|---|---|---|
| 선언 위치 | 클래스 블록 최상단 | `__init__` 안에서 `self.변수명` |
| 저장 위치 | 클래스 자체에 1개 | 인스턴스마다 별도 |
| 쓰는 경우 | 모든 객체에 동일한 값이나 카운터 | 객체마다 다른 상태 |

---

### 접근 제한과 name mangling

Python에는 다른 언어처럼 진짜 private가 없습니다.  
대신 관례(convention)와 name mangling으로 접근을 구분합니다.

```python
class BankAccount:
    def __init__(self, balance):
        self.owner = "철수"       # public: 제한 없음
        self._balance = balance   # protected: 관례상 "내부용"이라는 표시. 강제는 아님
        self.__pin = "1234"       # private: name mangling 적용

account = BankAccount(10000)
print(account.owner)      # "철수"  ← 접근 가능
print(account._balance)   # 10000   ← 접근은 되지만 관례상 하지 않음

# __pin은 직접 접근 불가
# print(account.__pin)    # AttributeError

# Python은 __attr를 _ClassName__attr로 이름을 바꿔 저장 (name mangling)
# 이름 충돌을 피하려는 목적이며, 완전한 차단이 아님
print(account._BankAccount__pin)  # "1234" ← 실제 저장된 이름으로는 접근 가능
```

`__`를 쓰는 주 이유는 **서브클래스에서 이름이 겹치는 것을 방지**하기 위함입니다.  
단순히 "외부에서 쓰지 말 것"을 표시하려면 `_`로도 충분합니다.

---

### @property

getter/setter를 속성처럼 쓸 수 있게 해주는 데코레이터입니다.  
외부에서 보기엔 일반 속성처럼 보이지만, 내부에서는 함수가 실행됩니다.

```python
class Temperature:
    def __init__(self, celsius):
        self._celsius = celsius

    @property
    def celsius(self):          # getter — t.celsius 로 접근
        return self._celsius

    @celsius.setter
    def celsius(self, value):   # setter — t.celsius = 25 로 설정
        if value < -273.15:
            raise ValueError("절대 영도 이하")
        self._celsius = value

    @property
    def fahrenheit(self):       # setter 없음 → 읽기 전용
        return self._celsius * 9/5 + 32

t = Temperature(25)
print(t.celsius)      # 25
print(t.fahrenheit)   # 77.0
t.celsius = 30        # setter 호출
t.celsius = -300      # ValueError
```

`@property`가 유용한 이유는 처음에 단순 속성으로 시작했다가 나중에 검증 로직을 추가해야 할 때, 외부 코드를 바꾸지 않고 내부만 바꿀 수 있기 때문입니다.

---

### @staticmethod / @classmethod

```python
class MathUtils:
    pi = 3.14159

    @staticmethod
    def add(a, b):
        # self도 cls도 받지 않음
        # 클래스 상태에 접근할 필요 없는 유틸 함수
        return a + b

    @classmethod
    def circle_area(cls, r):
        # cls = 클래스 자체 (MathUtils)
        # 클래스 변수에 접근하거나 다른 인스턴스를 만들 때 씁니다
        return cls.pi * r ** 2

    @classmethod
    def from_string(cls, s):
        # 대안 생성자 패턴 — 문자열로 객체 만들기
        a, b = map(int, s.split(","))
        return cls.add(a, b)   # 예시용 단순화

MathUtils.add(3, 4)          # 7   (인스턴스 없이 호출)
MathUtils.circle_area(5)     # 78.53...
```

| | instance method | classmethod | staticmethod |
|---|---|---|---|
| 첫 인자 | `self` (인스턴스) | `cls` (클래스) | 없음 |
| 접근 | 인스턴스/클래스 변수 모두 | 클래스 변수 | 없음 |
| 쓰는 경우 | 일반 메서드 | 대안 생성자, 클래스 변수 조작 | 클래스와 무관한 유틸 |

---

### 매직 메서드 (Dunder Method)

`__이름__` 형태의 특수 메서드입니다. Python 내장 연산자나 함수에 반응합니다.

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):          # print() 또는 str() 호출 시
        return f"Vector({self.x}, {self.y})"

    def __repr__(self):         # REPL이나 디버거에서 출력 시 (개발자용)
        return f"Vector(x={self.x}, y={self.y})"

    def __add__(self, other):   # v1 + v2
        return Vector(self.x + other.x, self.y + other.y)

    def __len__(self):          # len(v)
        return 2

    def __eq__(self, other):    # v1 == v2
        return self.x == other.x and self.y == other.y

    def __getitem__(self, idx): # v[0], v[1]
        return (self.x, self.y)[idx]

v1 = Vector(1, 2)
v2 = Vector(3, 4)
print(v1)            # Vector(1, 2)
print(v1 + v2)       # Vector(4, 6)
print(len(v1))       # 2
print(v1 == Vector(1, 2))   # True
print(v1[0])         # 1
```

---

### 상속과 추상 클래스

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    def __init__(self, color="black"):
        self.color = color

    @abstractmethod
    def area(self) -> float:
        # abstractmethod: 자식 클래스에서 반드시 구현해야 함
        # 구현하지 않으면 인스턴스 생성 시 TypeError 발생
        pass

    def describe(self):
        return f"{self.color} 도형, 넓이: {self.area():.2f}"


class Circle(Shape):
    def __init__(self, radius, color="black"):
        super().__init__(color)   # 부모 __init__ 호출 필수
        self.radius = radius

    def area(self):
        return 3.14159 * self.radius ** 2


class Rectangle(Shape):
    def __init__(self, w, h, color="black"):
        super().__init__(color)
        self.w, self.h = w, h

    def area(self):
        return self.w * self.h


# 다형성: 같은 인터페이스로 다른 구현체를 처리
shapes = [Circle(5), Rectangle(3, 4, "red"), Circle(2, "blue")]
for s in shapes:
    print(s.describe())

# Shape() 직접 생성 불가
# Shape()  → TypeError: Can't instantiate abstract class
```

---

### 상속 vs 컴포지션

클래스 간 관계를 표현하는 두 가지 방식입니다.

**상속(inheritance)**은 "is-a" 관계입니다. `Circle`은 `Shape`다.

**컴포지션(composition)**은 "has-a" 관계입니다. `Car`는 `Engine`을 가지고 있다.

```python
# 컴포지션 예 — Car가 Engine을 상속하지 않고 포함
class Engine:
    def __init__(self, hp):
        self.hp = hp

    def start(self):
        return f"{self.hp}hp 엔진 시동"

class GPS:
    def navigate(self, dest):
        return f"{dest}으로 안내 시작"

class Car:
    def __init__(self, hp):
        self.engine = Engine(hp)   # Engine을 포함
        self.gps = GPS()

    def drive(self, dest):
        return f"{self.engine.start()} → {self.gps.navigate(dest)}"

car = Car(200)
print(car.drive("서울"))
```

| | 상속 | 컴포지션 |
|---|---|---|
| 관계 | is-a (원은 도형이다) | has-a (차는 엔진을 가진다) |
| 결합도 | 높음 (부모 바뀌면 영향 받음) | 낮음 (교체 쉬움) |
| 쓰는 경우 | 공통 인터페이스 강제, 코드 재사용 | 기능 조합, 유연한 설계 |

실전에서는 "상속보다 컴포지션을 선호하라"는 원칙이 자주 등장합니다. 상속 계층이 깊어지면 코드 흐름을 따라가기 어려워지기 때문입니다.

---

## 6. NumPy 배열 연산

### 왜 NumPy를 쓰는가

Python 리스트로 수치 연산을 하면 루프가 필요하고 느립니다.  
NumPy의 배열 연산은 C로 구현되어 있어 **수십~수백 배 빠르고**, 브로드캐스팅으로 루프 없이 배열 전체에 연산을 적용할 수 있습니다.

```python
import numpy as np

# 리스트 방식 (느림)
result = [x * 2 for x in range(1_000_000)]

# NumPy 방식 (빠름)
arr = np.arange(1_000_000)
result = arr * 2   # 루프 없이 전체에 적용
```

---

### 배열 생성

```python
import numpy as np

# 직접 생성
a = np.array([1, 2, 3])             # 1D
b = np.array([[1, 2], [3, 4]])      # 2D

# 초기화 배열
np.zeros((3, 4))                    # 0으로 채운 3×4
np.ones((2, 3))                     # 1로 채운 2×3
np.full((3, 3), 7)                  # 7로 채운 3×3
np.eye(4)                           # 4×4 단위행렬

# 수열
np.arange(0, 10, 2)                 # [0, 2, 4, 6, 8]
np.linspace(0, 1, 5)                # [0.0, 0.25, 0.5, 0.75, 1.0]

# 난수
np.random.rand(3, 3)                # 0~1 균등분포
np.random.randn(3, 3)               # 표준정규분포
np.random.randint(0, 10, (3, 3))    # 정수 난수
np.random.normal(0, 0.1, 360)       # 평균, 표준편차 지정
```

---

### shape / ndim / dtype — 배열의 기본 속성

NumPy 코드를 읽을 때 shape를 추적하는 게 핵심입니다.

```python
a = np.array([[1, 2, 3],
              [4, 5, 6]])

a.ndim    # 2     (차원 수)
a.shape   # (2, 3) (행 2개, 열 3개)
a.size    # 6     (전체 원소 수)
a.dtype   # dtype('int64')

# dtype은 정밀도와 메모리에 영향
np.array([1.0, 2.0]).dtype    # float64 (기본)
np.array([1, 2], dtype=np.float32)  # float32로 강제
```

---

### 형태 변환 (reshape / flatten / ravel)

```python
a = np.arange(12)   # [0, 1, 2, ... 11]

# reshape — 원소 수가 같다면 자유롭게 형태 변환
a.reshape(3, 4)     # (3, 4)
a.reshape(2, 6)     # (2, 6)
a.reshape(-1, 3)    # (-1은 자동 계산) → (4, 3)

# reshape(-1)과 flatten()의 차이
mat = a.reshape(3, 4)

flat1 = mat.reshape(-1)   # 가능하면 view 반환 (원본과 메모리 공유 가능)
flat2 = mat.flatten()     # 항상 복사본 반환 (원본과 독립)

flat1[0] = 999
print(mat[0, 0])   # 999 — reshape(-1)이 view면 원본도 바뀔 수 있음

flat2[0] = 999
print(mat[0, 0])   # 999 — flatten()은 복사본이므로 원본 불변

# 전치 (행과 열 바꾸기)
mat.T
```

---

### 인덱싱과 슬라이싱

```python
arr = np.array([10, 20, 30, 40, 50])

arr[2]          # 30
arr[-1]         # 50
arr[1:4]        # [20, 30, 40]
arr[::2]        # [10, 30, 50]

# 2D 인덱싱
mat = np.array([[1, 2, 3],
                [4, 5, 6],
                [7, 8, 9]])

mat[1, 2]           # 6         (1행 2열)
mat[:, 1]           # [2, 5, 8] (1열 전체)
mat[0:2, 1:3]       # [[2,3],[5,6]]

# 불리언 인덱싱 — 조건을 배열로 표현
arr = np.array([10, 20, 30, 40, 50])
mask = arr > 25
arr[mask]               # [30, 40, 50]
arr[(arr > 15) & (arr < 45)]   # [20, 30, 40]

# np.where — 조건에 따라 값 선택
np.where(arr > 25, arr, 0)     # [0, 0, 30, 40, 50] (조건 불만족 시 0)

# 팬시 인덱싱
arr[[0, 2, 4]]          # [10, 30, 50]
```

---

### Broadcasting

shape가 다른 배열끼리 연산할 때 작은 배열을 자동으로 확장하는 규칙입니다.  
규칙이 맞으면 루프 없이 고차원 연산이 됩니다.

```python
a = np.array([[1, 2, 3],   # shape (2, 3)
              [4, 5, 6]])

# 스칼라 브로드캐스팅 — 스칼라가 배열 shape로 확장됨
a + 10     # [[11,12,13],[14,15,16]]

# 벡터 브로드캐스팅
b = np.array([10, 20, 30])   # shape (3,) → (1,3) → (2,3)으로 확장
a + b      # [[11,22,33],[14,25,36]]

# 열벡터 브로드캐스팅
c = np.array([[100], [200]])  # shape (2,1) → (2,3)으로 확장
a + c      # [[101,102,103],[204,205,206]]
```

브로드캐스팅 규칙 요약:
1. 차원 수가 다르면 앞에 1을 채운다 (3,) → (1, 3)
2. 크기가 1인 축은 상대 배열의 크기에 맞게 복사된다
3. 크기가 다르고 둘 다 1이 아니면 에러

---

### axis — 어느 방향으로 연산할지

`axis=0`은 행 방향(세로), `axis=1`은 열 방향(가로)으로 연산합니다.

```python
mat = np.array([[1, 2, 3],
                [4, 5, 6]])

np.sum(mat)           # 21    (전체 합)
np.sum(mat, axis=0)   # [5, 7, 9]  (각 열의 합, 행을 압축)
np.sum(mat, axis=1)   # [6, 15]    (각 행의 합, 열을 압축)

np.mean(mat, axis=0)  # [2.5, 3.5, 4.5]
np.max(mat, axis=1)   # [3, 6]
```

---

### 주요 연산 함수

```python
arr = np.array([3, 1, 4, 1, 5, 9, 2, 6])

np.sum(arr)           # 31
np.mean(arr)          # 3.875
np.std(arr)           # 표준편차
np.min(arr), np.max(arr)     # 1, 9
np.argmin(arr), np.argmax(arr)  # 최솟값/최댓값의 인덱스
np.median(arr)        # 중앙값
np.cumsum(arr)        # 누적 합
np.sort(arr)          # 정렬 (새 배열)
np.argsort(arr)       # 정렬 시 원래 인덱스

# 수학 함수
np.sqrt(arr)
np.abs(arr)
np.log(arr)           # 자연로그
np.exp(arr)

# 선형대수
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

A @ B                      # 행렬 곱
np.linalg.det(A)           # 행렬식
np.linalg.inv(A)           # 역행렬
np.linalg.norm(A)          # 프로베니우스 노름
np.dot(A, B)               # 내적 / 행렬 곱 (@ 와 동일)
```

---

### 배열 합치기

```python
a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6], [7, 8]])

np.vstack([a, b])    # 세로로 쌓기 → (4, 2)
np.hstack([a, b])    # 가로로 붙이기 → (2, 4)
np.concatenate([a, b], axis=0)   # vstack과 같음
np.concatenate([a, b], axis=1)   # hstack과 같음
```

---

## 7. Matplotlib 시각화

### 기본 구조

Matplotlib의 구조는 `Figure(도화지) > Axes(좌표계) > 그래프 요소` 계층입니다.  
`plt.plot()` 같은 함수형 API와 `ax.plot()` 같은 객체지향 API가 모두 있는데, 서브플롯이 있거나 세밀한 제어가 필요하면 객체지향 방식을 씁니다.

```python
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 2 * np.pi, 200)

# 객체지향 방식 (권장)
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(x, np.sin(x), label="sin", color="steelblue", linewidth=2)
ax.plot(x, np.cos(x), label="cos", color="tomato",    linestyle="--")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("삼각함수")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("trig.png", dpi=150)
plt.show()
```

---

### 다양한 차트

```python
import numpy as np
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(12, 8))

# 산점도
rng = np.random.default_rng(42)
x = rng.standard_normal(100)
y = x + rng.standard_normal(100) * 0.5
axes[0, 0].scatter(x, y, c=y, cmap="coolwarm", alpha=0.7)
axes[0, 0].set_title("Scatter Plot")

# 막대 그래프
categories = ["A", "B", "C", "D"]
values = [23, 45, 12, 67]
axes[0, 1].bar(categories, values, color="steelblue", edgecolor="black")
axes[0, 1].set_title("Bar Chart")

# 히스토그램
data = rng.normal(0, 1, 1000)
axes[1, 0].hist(data, bins=30, color="mediumseagreen", edgecolor="black", alpha=0.7)
axes[1, 0].set_title("Histogram")

# 박스플롯
data = [rng.normal(0, 1, 100), rng.normal(2, 1.5, 100)]
axes[1, 1].boxplot(data, labels=["A", "B"])
axes[1, 1].set_title("Boxplot")

plt.tight_layout()
plt.show()
```

---

### 서브플롯과 주석

```python
import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 5))

x = np.linspace(0, 2 * np.pi, 200)
y = np.sin(x)

ax.plot(x, y)

# 특정 포인트에 주석
peak_x = np.pi / 2
ax.annotate(
    "최댓값 (1.0)",
    xy=(peak_x, 1.0),                     # 화살표 끝 (실제 데이터 포인트)
    xytext=(peak_x + 0.5, 1.15),          # 텍스트 위치
    arrowprops=dict(arrowstyle="->", color="red"),
    fontsize=11,
    color="red"
)

ax.axhline(y=0, color="black", linewidth=0.8, linestyle=":")   # 수평 기준선
ax.axvline(x=np.pi, color="gray", linewidth=0.8, linestyle="--")  # 수직 기준선
ax.set_title("sin(x)와 주석")
plt.tight_layout()
plt.show()
```

---

### 실시간 플롯

```python
import numpy as np
import matplotlib.pyplot as plt

plt.ion()   # interactive mode on
fig, ax = plt.subplots()

data = []

for i in range(30):
    data.append(np.random.randn())
    ax.clear()
    ax.plot(data, color="steelblue")
    ax.set_title(f"실시간 데이터 (frame {i+1})")
    ax.set_ylim(-4, 4)
    ax.axhline(y=0, color="red", linestyle="--", alpha=0.5)
    plt.pause(0.1)   # 화면 갱신 + 0.1초 대기

plt.ioff()  # interactive mode off
plt.show()
```

---

### 스타일

```python
import matplotlib.pyplot as plt

# 사용 가능한 스타일 목록
print(plt.style.available)

# 스타일 적용
plt.style.use("seaborn-v0_8")
# 또는
plt.style.use("ggplot")
```

---

*이 문서는 01.02 ~ 02.03 실습 내용을 기반으로 작성되었습니다.*
