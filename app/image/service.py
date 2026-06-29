import asyncio
import os
import stat
import zipfile
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from typing import Any, List

import aiofiles
from PIL import Image
from starlette.datastructures import UploadFile

from app.image.entity.image import ImgDetailEntity
from app.image.exception import AlreadySavedImageError, NotSupportTypeFileError
from app.image.model.image import ImgDetailModel
from app.image.repository import ImageRepository


class ImageService:
    def __init__(self, repository: ImageRepository, config: Any):
        self._repo: ImageRepository = repository
        self.config = config
        self.root_path = config['api']['mount']['data']
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.tif'}
        self.executor = ThreadPoolExecutor()

    async def get_images(self, page: int, size: int, exam_history_id: str) -> List[
        ImgDetailModel]:  # exam_hist_id -> exam_history_id
        image_entities = await self._repo.get_by_page(page * size, size, exam_history_id)
        image = list(map(ImgDetailModel.from_entity, image_entities))
        return image

    async def check_exam(self, exam_history_id: str):  # exam_hist_id -> exam_history_id
        result = await self._repo.get_by_exam_history_id(exam_history_id)
        if len(result) == 0:
            return
        else:
            raise AlreadySavedImageError(f"시험번호 : {exam_history_id}, 저장된 이미지 : {len(result)}건")

    async def add_images(self, exam_history_id: str, files: List[UploadFile]):
        # 1. 준비 작업
        await self.check_exam(exam_history_id)
        save_path = os.path.join(self.root_path, exam_history_id)
        os.makedirs(save_path, exist_ok=True)  # Ensure the directory exists
        save_files = []

        # 2. 단일 파일 or ZIP 파일 체크
        if len(files) == 1:
            file = files[0]
            file_content_type = file.content_type
            if file_content_type == 'application/zip':
                # ZIP 파일 처리
                save_files = await self.save_zip_file(file, save_path)

                # Remove files where the filename starts with a '.'
                save_files = [file for file in save_files if not file.startswith('.')]
                save_files.sort()
            else:
                # 단일 파일 처리 (save_file의 변경 사항 반영 -> 단일 파일 리스트로 감싸서 호출)
                save_files = await self.save_file([file], save_path)
        else:
            # 여러 파일 처리 (save_file의 확장된 기능 사용)
            files.sort(key=lambda x: x.filename)
            save_files = await self.save_file(files, save_path)

        # 3. 이미지 크기 측정 및 Entity 생성
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                self.executor,
                self.get_image_size,
                os.path.join(save_path, save_file)
            )
            for save_file in save_files
        ]

        sizes = await asyncio.gather(*tasks)
        entities = []

        for idx, (save_file, size) in enumerate(zip(save_files, sizes), start=1):
            if size is not None:
                width, height = size
                entity = ImgDetailEntity(
                    IMG_NAME=save_file,  # IMG_NM -> IMAGE_NAME
                    EXAM_HISTORY_ID=exam_history_id,  # EXAM_HIST_ID -> EXAM_HISTORY_ID
                    IMG_SET_LEN=len(save_files),  # IMG_SET_LEN -> IMAGE_SET_LENGTH
                    CUT_NO=str(idx).zfill(2),
                    WIDTH=width,
                    HEIGHT=height,
                    SRC_PATH=os.path.join(exam_history_id, save_file)  # SRC_PATH -> SOURCE_PATH
                )
                entities.append(entity)

        # 4. DB 저장 및 상태 업데이트
        result = list(map(ImgDetailModel.from_entity, entities))
        await self._repo.add_images(entities)
        await self._repo.update_exam_inf_state(exam_history_id, 'READY')

        return result

    def process_image_to_png(self, content, save_directory, filename_without_ext):
        """이미지를 PNG로 변환하고 저장"""
        try:
            # 이미지 열기
            img = Image.open(BytesIO(content))

            # 해상도 제한
            img.thumbnail((2000, 2000))  # 최대 해상도 제한
            img = img.convert("RGB")

            # 파일 저장 경로 준비
            destination_path = os.path.join(save_directory, f"{filename_without_ext}.png")

            # PNG로 저장
            img.save(destination_path, "PNG", optimize=True)

            return f"{filename_without_ext}.png"  # 저장된 파일 이름 반환
        except Exception as e:
            return None  # 에러 발생 시 None 반환

    async def save_zip_file(self, file: UploadFile, save_path: str):
        with zipfile.ZipFile(file.file, 'r') as zip_ref:
            save_files = []
            extension_count = {}
            all_files_count = 0

            all_members = [info for info in zip_ref.infolist() if not info.is_dir()]

            # 확장자 카운트
            for member in all_members:
                filename = member.filename
                extension = os.path.splitext(filename)[1].lower()
                if extension in self.image_extensions:
                    extension_count[extension] = extension_count.get(extension, 0) + 1
                    all_files_count += 1

            # 멀티스레드 풀 생성
            with ThreadPoolExecutor() as executor:
                futures = []

                for member in all_members:
                    filename = member.filename
                    extension = os.path.splitext(filename)[1].lower()

                    if extension in self.image_extensions and extension_count[extension] == 1:
                        continue

                    if extension in self.image_extensions:
                        with zip_ref.open(member) as source:
                            content = source.read()
                            basename = os.path.splitext(os.path.basename(filename))[0]

                            # 스레드를 통한 비동기 작업 할당
                            future = executor.submit(self.process_image_to_png, content, save_path, basename)
                            futures.append(future)

                # 작업 결과 수집
                for future in futures:
                    result = future.result()
                    if result:
                        save_files.append(result)

        return save_files

    async def save_file(self, files: List[UploadFile], save_path: str):
        save_files = []

        # 멀티스레드 풀 구성
        with ThreadPoolExecutor() as executor:
            futures = []

            # 파일별로 처리 작업 스레드에 할당
            for file in files:
                extension = os.path.splitext(file.filename)[1].lower()

                # 지원하는 파일 형식인지 체크
                if extension in self.image_extensions:
                    try:
                        # 비동기로 파일 읽기
                        file_data = await file.read()
                        filename_without_ext = os.path.splitext(file.filename)[0]

                        # 스레드 풀에 작업 제출
                        future = executor.submit(
                            self.process_image_to_png,  # PNG 변환 함수
                            file_data,  # 이미지 데이터
                            save_path,  # 저장 경로
                            filename_without_ext  # 저장 파일 이름 (확장자 제외)
                        )
                        futures.append(future)
                    except Exception as e:
                        raise NotSupportTypeFileError(
                            f"이미지 처리 실패 - 파일명: {file.filename}, 오류: {str(e)}"
                        )
                else:
                    raise NotSupportTypeFileError(f"지원되지 않는 파일 형식: {file.filename}")

            # 병렬 처리된 결과 모으기
            for future in futures:
                result = future.result()  # 스레드 결과 가져오기
                if result:
                    save_files.append(result)

        return save_files

    def get_image_size(self, image_path):
        """이미지 파일의 크기를 반환"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
            return width, height
        except Exception as e:
            # 에러 발생 시 None 반환
            return None, None

    async def del_images(self, exam_history_id: str):  # exam_hist_id -> exam_history_id
        dir_path = os.path.join(self.root_path, exam_history_id)
        if os.path.exists(dir_path):
            for root, dirs, files in os.walk(dir_path):
                for f in files:
                    os.chmod(os.path.join(root, f), stat.S_IWRITE)  # Ensure file has write permission
                    os.remove(os.path.join(root, f))
            os.rmdir(dir_path)
        await self._repo.del_images(exam_history_id)
        return await self._repo.update_exam_inf_state(exam_history_id, 'NO_IMG')
