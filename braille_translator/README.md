# Braille Translator

## Overview
Braille Translator는 한글/영문/숫자/특수문자에 대한 점자 변환 및 역변환을 지원하는 프로젝트입니다.  
텍스트 ↔ 점자(01문자열, 유니코드, 이미지) 변환, 점자 이미지 인식, 약자/조합형 선택 등 다양한 기능을 제공합니다.

## Project Structure
```
braille_translator
├── src
│   ├── braille_tabble.py      # 한글/영문 점자 매핑 테이블 및 역변환 테이블
│   ├── translator.py          # 텍스트-점자 변환 및 역변환 로직
│   ├── braille_utils.py       # 점자 유틸 함수(평탄화, 유니코드 변환 등)
│   ├── braille_image.py       # 점자 이미지 인식 및 변환
├── requirements.txt           # 프로젝트 의존성 목록
├── main.py                    # CLI 실행 진입점(모드 선택 지원)
└── README.md                  # 프로젝트 설명서
```

## Installation & Usage

### [Windows 기준]

1. **가상환경 생성 및 활성화**
   ```sh
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. **필수 패키지 설치**
   ```sh
   pip install -r requirements.txt
   ```

3. **프로그램 실행**
   ```sh
   python main.py
   ```

### [Mac/Linux 기준]

1. **가상환경 생성 및 활성화**
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **필수 패키지 설치**
   ```sh
   pip install -r requirements.txt
   ```

3. **프로그램 실행**
   ```sh
   python3 main.py
   ```

---

## Usage

실행 후 아래와 같이 모드를 선택할 수 있습니다.

- 1: 텍스트 → 점자(약자 우선 변환)
- 2: 텍스트 → 점자(초/중/종 조합형 변환)
- 3: 점자(01문자열) → 텍스트
- 4: 점자(유니코드) → 텍스트
- 5: 점자 이미지 → 텍스트

### 예시
- "안녕하세요"를 점자로 변환(약자 우선):
    ```
    모드 번호 입력: 1
    변환할 텍스트 입력: 안녕하세요
    ```
- 유니코드 점자(⠣⠒⠉⠻ 등)를 텍스트로 변환:
    ```
    모드 번호 입력: 4
    점자(유니코드) 입력: ⠣⠒⠉⠻
    ```

---

## 주요 기능
- 한글/영문/숫자/특수문자 점자 변환 및 역변환
- 약자/조합형 변환 선택 지원
- 점자 이미지 인식 및 텍스트 복원
- 점자 유니코드 변환, 안전한 파일명 처리 등 유틸 제공

## Contributing
기여를 환영합니다! 개선 제안이나 버그 리포트, PR을 보내주세요.

## License
MIT License