[![Contributors][contributors-shield]][contributors-url]
[![Issues][issues-shield]][issues-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  

  <h2 align="center">Luxmind-api</h2>
  

  
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

Alpha Retina - WebAPI 

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

[![FastAPI][FastAPI]][FastAPI-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started


### Prerequisites

1. OS
   - Ubuntu (works completely in [Ubuntu 22.04 LTS][Ubuntu-link]) (**RECOMMENDED**)
   - Windows (works with a little issue in 11)
   - MacOS (works completely in Ventura)
2. Python >= 3.10 (**3.11 RECOMMENDED**)
   - `typing` 모듈 사용시 `Union`, `Optional` 대신 `|` 연산자의 사용을 권장하고 있음
   > ❓만약 local python 버전을 3.10 미만을 사용하고 있다면?  
   > 👉 별도로 3.10을 설치한 뒤 `virtualenv`를 추가로 설치하여 가상환경 생성시 python 버전을 3.10으로 명시
3. Database
   - RDB: MySQL (8.0 **RECOMMENDED**)
   - NoSQL: MongoDB (6.0.5 **RECOMMENDED**)
4. Environment Variables  
   다음 환경변수를 반드시 설정해야 서버를 구동할 수 있음 (참고: `src/core/constants.py`)
   - DEPLOY_MODE : 배포환경명
     - 로컬: local
     - 개발계: dev
     - 테스트계: test
     - 운영계: prod
   - JWT_SECRET_KEY : JWT token 인증을 위한 secret key
     - 영문자 사용 추천, 특수문자 사용 안됨
     - 배포환경마다 상이한 key를 설정해야 함
   - JWT_REFRESH_SECRET_KEY : JWT 인증 token 만료시 재발급을 위한 secret key
     - 영문자 사용 추천, 특수문자 사용 안됨
     - 배포환경마다 상이한 key를 설정해야 함
   - WORK_DIR : 프로젝트의 Root DIR


## 의료기기 사이버보안 기능

본 프로젝트는 의료기기 사이버보안 요구사항(IA, UC, SI, DC, TRE, RA, SC)에 따라 다음 기능이 구현되어 있습니다.

### 식별 및 인증 (IA)
- **IA-01 다중 로그인 방지**: 동일 계정 중복 로그인 차단, 강제 로그인 시 기존 세션 자동 무효화 (`common/core/session_store.py`)
- **IA-02 계정 관리**: 계정 CRUD, 활성화/비활성화, 소프트 삭제, 역할 할당 (`common/app/user/`)
- **IA-03 식별정보 유일성**: 사용자 ID/역할 ID 유일성 보장, 중복 체크
- **IA-04 인증정보 관리**: 초기 비밀번호 강제 변경, 30일 주기 비밀번호 만료, bcrypt 해싱
- **IA-05 비밀번호 강도**: 8~20자, 대소문자+숫자+특수문자 조합 검증
- **IA-06 인증 피드백**: 비밀번호 마스킹, 실패 정보 최소화 ("아이디 또는 비밀번호가 올바르지 않습니다")
- **IA-07 로그인 실패 제한**: 5회 초과 시 자동 계정 잠금
- **IA-08 시스템 사용 알림**: 관리자 전용 알림 메시지 발송 기능 (대상별/역할별/전체)

### 사용 통제 (UC)
- **UC-01 권한 부여**: RBAC 역할 기반 접근 제어 (`SUPER_ADMIN`, `ADMIN`, `DOCTOR`, `NURSE`, `USER`)
- **UC-04 감사 기록**: 주요 보안 이벤트 AUDIT_LOG 테이블 기록 (`common/core/audit.py`)
  - 로그인 성공/실패, 계정 변경, 권한 변경, 비밀번호 변경, 설정 변경 등
  - 타임스탬프, IP, 사용자, 카테고리, 심각도, 이벤트 ID 포함
- **UC-05 감사 처리 실패 대응**: 감사 로그 실패 시 서비스 기능 손실 없이 계속 동작
- **UC-06 타임스탬프**: 모든 감사 기록에 OS 시간 기반 datetime 기록

### 시스템 무결성 (SI)
- **SI-01 통신 무결성**: JWT HS256 서명, bcrypt 해싱, TLS (프로덕션)
- **SI-02 악성코드 방지**: AppArmor, Docker 격리, ClamAV 호환
- **SI-03 보안 기능 검증**: 인증 실패, 감사 로그 확인, 서버 실행 무결성 검증
- **SI-04 소프트웨어/정보 무결성**: `verify_integrity.py` 스크립트로 소스 SHA-256 해시 검증
- **SI-05 입력값 검증**: Pydantic 모델 검증, SQLAlchemy 파라미터 바인딩으로 SQL Injection 방어
- **SI-06 오류 시 결정된 출력**: 사전 정의된 에러 코드/메시지 형식 (`/security/failsafe`)
- **SI-09 업데이트 무결성**: 서버 기동 시 자동 무결성 검증 (`common/events/lifespan.py`)

### 데이터 기밀성 (DC)
- **DC-01 정보 기밀성**: 환자 데이터 AES-256-CBC 암호화 저장 (`common/core/encryption.py`)
- **DC-02 비식별화**: 환자 이름/생년월일 마스킹 (`name_masked`, `birth_dt_masked`)
- **DC-03 암호화 알고리즘**: AES-256 (NIST FIPS 197), SHA-256 (NIST FIPS 180-4), bcrypt

### 이벤트 감사 (TRE)
- **TRE-01 감사로그 보호**: 관리자 전용 읽기 접근 (`/audit-logs`), 수정/삭제 API 없음

### 자원 가용성 (RA)
- **RA-01 DoS 대응**: `DosProtectionMiddleware` - 레이트 리미팅, IP 차단, 트래픽 분석
- **RA-02 백업**: `backup.sh` 풀백업 스크립트 (DB + 소스 + Docker 이미지 + 설정 + 무결성 해시)

### 소프트웨어 구성 (SC)
- **SC-01 장애 복구**: `restore.sh` 복구 스크립트 (무결성 검증 후 복구)
- **SC-03 포트/서비스 제한**: 필수 포트만 개방, 불필요/취약 포트 차단

### AI 보안 (제12조)
- JWT + RBAC 기반 추론 API 접근 통제
- 모델 파일 외부 직접 접근 차단
- 환자 데이터 AES-256 암호화 저장/조회

### 검증 스크립트

프로젝트 루트에 위치한 검증 스크립트로 각 보안 항목을 자동 검증할 수 있습니다:

```bash
# 소프트웨어 무결성 검증
python verify_integrity.py          # 기준 해시 저장
python verify_integrity.py --check  # 저장된 해시와 비교

# 데이터 무결성 검증 (감사 로그 해시, 비밀번호 해싱 확인)
python verify_data_integrity.py

# 입력값 검증 (SQL Injection, XSS, Command Injection 등)
python verify_input_validation.py

# 사전 정의된 오류 출력 검증
python verify_failsafe.py

# AI 보안 검증 (모델 무결성, 접근 통제, 데이터 보호)
python verify_ai_security.py

# 포트 및 서비스 보안 검증
python verify_port_security.py

# 백업 및 복구
bash backup.sh                      # 풀백업
bash backup.sh --db-only            # DB만 백업
bash backup.sh --verify             # 최근 백업 검증
bash restore.sh                     # 복구
bash restore.sh --verify            # 복구 후 시스템 검증
```

### 보안 프로토콜 현황 조회

```
GET /security/protocols   # 암호화/인증/DoS 방어 프로토콜 현황
GET /security/integrity   # 주요 파일 SHA-256 해시 무결성
GET /security/failsafe    # 사전 정의된 오류 상태 및 출력 정의
```

## Installation

### 1. Local deployment
1. 파이썬 가상환경을 `${WORK_DIR}`에 생성합니다.
   ```bash
   python3.11 -m venv .venv
   . .venv/bin/activate
   ```

2. 배포 환경에 맞는 requirements를 [pip](https://pip.pypa.io/en/stable/) 를 통해 설치합니다.
   ```bash
   pip install -r requirements/${DEPLOY_MODE}.txt
   ```

3. 배포 환경에 맞는 config 파일을 복사하여 `config.yaml`로 생성합니다.

   ```bash
   cp config.${DEPLOY_MODE}.yaml config.yaml
   ```

4. api를 실행합니다.
   ```bash
   uvicorn main:app --reload --lifespan on
   ```



<!-- LICENSE -->
## License

Distributed under the Closed-source License. See [`LICENSE.txt`](./LICENSE.txt) for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments



<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[Project-link]: https://github.com/luxmind-ai/api
[contributors-shield]: https://img.shields.io/badge/contributors-1-blue?style=for-the-badge
[contributors-url]: https://github.com/luxmind-ai/api/graphs/contributors
[stars-shield]: https://img.shields.io/badge/stars-0-yellow?style=for-the-badge
[stars-url]: https://github.com/luxmind-ai/api/stargazers
[issues-shield]: https://img.shields.io/badge/issues-1-green?style=for-the-badge
[issues-url]: https://github.com/luxmind-ai/api/issues
[license-shield]: https://img.shields.io/badge/license-closed-red?style=for-the-badge
[FastAPI]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi
[FastAPI-url]: https://fastapi.tiangolo.com/ko/
[Ubuntu-link]: https://releases.ubuntu.com/jammy/
