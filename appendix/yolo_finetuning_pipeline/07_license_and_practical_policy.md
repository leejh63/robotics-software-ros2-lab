# 07. 라이선스와 실제 프로젝트 적용 정책

## 1. 왜 라이선스를 봐야 하는가?

YOLO 모델은 기술적으로 학습만 한다고 끝이 아니다.

실제로 회사 서비스, 제품, 내부 시스템, 고객 납품에 넣을 경우 라이선스 문제가 생길 수 있다.

특히 Ultralytics YOLO 계열은 오픈소스 라이선스와 엔터프라이즈 라이선스 조건을 확인해야 한다.

---

## 2. 기술 관점과 법적 관점은 다르다

기술적으로는 아래가 가능하다.

```text
pretrained YOLO 다운로드
내 데이터셋으로 fine-tuning
best.pt 생성
서비스나 제품에 넣기
```

하지만 법적으로는 사용 목적과 배포 방식에 따라 조건이 달라질 수 있다.

```text
개인 학습
연구
오픈소스 프로젝트
회사 내부 PoC
회사 내부 운영 시스템
외부 고객에게 제공하는 제품
SaaS 서비스
상용 앱/장비 탑재
```

---

## 3. 파인튜닝한 모델의 성격

내 데이터로 파인튜닝한 `best.pt`는 보통 아래 요소를 포함한다.

```text
pretrained YOLO 가중치 기반
내 데이터셋으로 업데이트된 weight
내 클래스에 맞게 조정된 Head
내 학습 결과
```

즉, 완전히 독립적으로 처음부터 만든 모델이라고 보기 어렵다.

pretrained 모델과 학습 코드의 라이선스 영향을 받을 수 있다.

---

## 4. 실제 회사에서 흔한 선택지

### 선택지 A. AGPL 조건을 지키고 사용

오픈소스 조건을 충족할 수 있는 프로젝트라면 가능할 수 있다.

하지만 회사 제품이나 비공개 서비스에서는 부담이 클 수 있다.

### 선택지 B. Enterprise License 구매

상업 제품/서비스에 넣고 싶고 오픈소스 공개 의무를 피하고 싶다면 보통 엔터프라이즈 라이선스를 검토한다.

### 선택지 C. 다른 라이선스의 모델 사용

상용 사용 조건이 더 맞는 다른 객체 탐지 모델이나 프레임워크를 선택할 수 있다.

예:

```text
Apache-2.0
MIT
BSD
자체 학습 모델
회사 내부 모델
```

단, 모델 자체와 코드, pretrained weight의 라이선스를 각각 확인해야 한다.

---

## 5. 상업적 사용 판단 기준

대략 아래에 가까울수록 상업 사용 검토가 필요하다.

```text
회사 제품에 탑재
고객에게 납품
SaaS 서비스에서 추론 제공
앱/장비에 모델 포함
비공개 소스 기반으로 운영
매출과 직접 연결
```

내부 PoC라도 회사 정책상 라이선스 검토가 필요할 수 있다.

---

## 6. 실무적으로 안전한 정책

프로젝트 시작 시 아래를 문서화한다.

```text
사용한 YOLO 버전
사용한 pretrained weight
사용한 학습 코드
사용한 데이터셋
사용 목적
배포 형태
라이선스 검토 결과
```

예:

```markdown
# Model License Note

- framework: Ultralytics YOLO
- model: yolo26n.pt
- task: object detection
- dataset: private custom dataset
- usage: internal prototype
- deployment: not distributed yet
- license review:
  - AGPL/Enterprise 조건 확인 필요
```

---

## 7. 포트폴리오/학습 프로젝트 기준

개인 포트폴리오나 학습용이면 보통 아래처럼 명시하는 것이 좋다.

```text
이 프로젝트는 학습/연구 목적으로 작성됨
Ultralytics YOLO 사용
상업 배포 전 라이선스 확인 필요
```

README 예시:

```markdown
## License Notice

This project uses Ultralytics YOLO for object detection experiments.
Before commercial deployment, review the applicable Ultralytics license terms.
```

---

## 8. 회사/제품 적용 전 체크리스트

```text
[ ] 사용한 YOLO 버전 확인
[ ] pretrained weight 출처 확인
[ ] 코드 라이선스 확인
[ ] 모델 weight 라이선스 확인
[ ] 데이터셋 라이선스 확인
[ ] 상업 배포 여부 확인
[ ] 소스 공개 가능 여부 확인
[ ] SaaS 제공 여부 확인
[ ] 법무/오픈소스 담당자 검토
[ ] 필요 시 Enterprise License 문의
```

---

## 9. 결론

기술적으로는 파인튜닝이 쉽다.

하지만 상업 적용은 아래를 반드시 분리해서 봐야 한다.

```text
학습 가능 여부
배포 가능 여부
상업 사용 가능 여부
소스 공개 의무
모델 weight 사용 권리
데이터셋 사용 권리
```

실제 회사 프로젝트라면 모델 성능 실험과 동시에 라이선스 검토를 병행해야 한다.
