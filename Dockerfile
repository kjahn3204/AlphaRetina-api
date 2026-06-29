# 베이스 이미지로부터 시작
FROM your_account/python:3.11-slim-deps
RUN apt-get update && apt-get install -y libglib2.0-0

# ARG 및 ENV 설정
ARG VERSION=2.0.0
ARG DEPLOY_MODE
ENV VERSION=${VERSION}
ENV DEPLOY_MODE=${DEPLOY_MODE}
ENV PRJ_NAME=kevas
ENV APP_NAME=api
ENV REPO=${PRJ_NAME}-${APP_NAME}

ENV JWT_SECRET_KEY raonjwtqwer
ENV JWT_REFRESH_SECRET_KEY raonjwtrefreshqwer
ENV USER root
ENV HOME /root
ENV SHELL /bin/bash
ENV WORK_DIR ${HOME}/${REPO}
ENV LOG_DIR ${WORK_DIR}/logs

# 작업 디렉토리 설정
WORKDIR ${WORK_DIR}

# 주요 코드 복사
COPY ./requirements/${DEPLOY_MODE}.txt ./requirements.txt
COPY ./main.py ./main.py
COPY ./app ./app
COPY ./ai ./ai
COPY ./common ./common
COPY ./config ./config
COPY ./dependencies ./dependencies
COPY ./interface ./interface
COPY ./core ./core
COPY ./static ./static
COPY ./util ./util
COPY ./config/config.${DEPLOY_MODE}.yaml ./config/config.yaml

# 패키지 설치 (베이스 이미지에서 이미 설치된 패키지를 재설치할 필요 없음)
RUN pip install -r requirements.txt

# 포트 노출 및 엔트리포인트 설정
EXPOSE 8000
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--workers", "4"]