#!/bin/bash

# 애플리케이션 컨테이너 중지 및 삭제
docker stop AR_api || true
docker rm AR_api || true

# 애플리케이션 이미지만 삭제
docker rmi api || true

# 베이스 이미지가 존재하는지 확인
BASE_IMAGE_EXISTS=$(docker images -q your_account/python:3.11-slim-deps)

# 베이스 이미지가 존재하지 않으면 빌드
if [ -z "$BASE_IMAGE_EXISTS" ]; then
    docker build -f Dockerfile.base . -t your_account/python:3.11-slim-deps
else
    echo "베이스 이미지가 이미 존재합니다. 재활용 합니다."
fi

# 애플리케이션 이미지 빌드
docker build . -t api --build-arg VERSION="0.0.1" --build-arg DEPLOY_MODE="prod"

# 애플리케이션 컨테이너 실행
docker run -d --name AR_api --expose 9001 -p 9001:8000 --net mybridge --ip 172.19.0.4 -v /mnt/disk1/AlphaRetina_api/img:/image_data -v /mnt/disk1/AlphaRetina_api/ai/seg_model.onnx:/ai/seg_model.onnx -v /mnt/disk1/AlphaRetina_api/ai/cat_model.onnx:/ai/cat_model.onnx api