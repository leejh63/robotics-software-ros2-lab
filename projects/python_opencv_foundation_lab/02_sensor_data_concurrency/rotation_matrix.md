# 회전행렬 & 관련 수학 정리

---

## 2D 회전행렬 (2×2)

점 $\mathbf{p}$를 원점 기준으로 $\theta$ 만큼 **반시계 방향** 회전:

$$R(\theta) = \begin{bmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{bmatrix}$$

$$\mathbf{p}' = R(\theta)\,\mathbf{p}$$

**핵심 성질:**
- $R(\theta)^{-1} = R(\theta)^T = R(-\theta)$ — 역회전 = 전치행렬
- $\det(R) = 1$ — 크기 보존
- $R(\alpha)R(\beta) = R(\alpha+\beta)$ — 회전 합성 = 각도 덧셈

---

## 3D 회전행렬 (3×3)

각 축 기준 회전을 따로 정의:

**X축 회전 $R_x$:**

$$R_x(\theta) = \begin{bmatrix} 1 & 0 & 0 \\ 0 & \cos\theta & -\sin\theta \\ 0 & \sin\theta & \cos\theta \end{bmatrix}$$

**Y축 회전 $R_y$:**

$$R_y(\theta) = \begin{bmatrix} \cos\theta & 0 & \sin\theta \\ 0 & 1 & 0 \\ -\sin\theta & 0 & \cos\theta \end{bmatrix}$$

**Z축 회전 $R_z$:**

$$R_z(\theta) = \begin{bmatrix} \cos\theta & -\sin\theta & 0 \\ \sin\theta & \cos\theta & 0 \\ 0 & 0 & 1 \end{bmatrix}$$

**합성 (예: ZYX 오일러 순서):**

$$R = R_z(\psi)\,R_y(\phi)\,R_x(\theta)$$

> ⚠️ 행렬 곱은 **비가환** — 순서가 달라지면 결과도 다름

**공통 성질 (2D와 동일):**

| 성질 | 내용 |
|------|------|
| $R^{-1} = R^T$ | 직교행렬 |
| $\det(R) = 1$ | 특수직교행렬 SO(3) |
| $R^T R = I$ | 열벡터들이 서로 직교 & 단위길이 |

---

## 사용된 수학 개념

| 개념 | 역할 |
|------|------|
| **삼각함수** (sin, cos) | 회전 성분 표현의 기본 도구 |
| **벡터** | 공간상의 점·방향 표현 |
| **행렬 곱셈** | 선형변환 합성 |
| **선형변환** | 회전 = 원점 고정 선형변환 |
| **직교행렬** | $R^T R = I$, 역행렬 = 전치 |
| **행렬식 (det)** | = 1이면 크기/방향 보존 |
| **단위벡터** | 행/열 벡터가 모두 단위길이 |
