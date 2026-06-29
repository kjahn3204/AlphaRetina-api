import json
import os
import pandas as pd
from collections import defaultdict

# SEG_CD 데이터 딕셔너리
seg_cd_dict = {
    "SRF": "01",
    "Chorioretinal scar": "02",
    "Cotton wool spot": "03",
    "Diffuse edema": "04",
    "Double layer sign": "05",
    "DRIL": "06",
    "Drusen": "07",
    "Ellipsoid zone alteration": "08",
    "Ellipsoid zone loss": "09",
    "ERM": "10",
    "Focal hyperreflectivity": "11",
    "Full thickness macular hole": "12",
    "Hard exudates": "13",
    "Hyperreflective foci": "14",
    "Hyperreflectivity of neurosensory retina": "15",
    "Hypertransmission": "16",
    "IRF": "17",
    "Lamellar macular hole": "18",
    "Microaneurysm": "19",
    "Neurosensory retina atrophy": "20",
    "Neurosensory retina detachment": "21",
    "Neurosensory retina detachmen": "21",
    "Outer retina tubulations": "22",
    "Posterior hyaloid membrane": "23",
    "Retinoschisis": "24",
    "RPE alteration": "25",
    "RPE detachment, Drusenoid": "26",
    "RPE detachment, Fibrovascular": "27",
    "RPE detachment, Serous": "28",
    "RPE loss": "29",
    "Shadowing": "30",
    "SHRM": "31",
    "Subretinal hyperreflectivity": "32",
    "Vitelliform material": "33",
    "Vitreomacular traction": "34",
    "RPE undulation": "35",
    "ILM detachment": "36",
    "staphyloma": "37",
    "choroidal excavation": "38",
    "thin choroid": "39",
}


def load_json(file_path):
    """ 지정된 경로에서 JSON 파일을 불러옵니다. """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def calculate_polygon_area(points):
    """ Shoelace 공식을 사용하여 다각형의 면적을 계산합니다. """
    n = len(points)
    area = 0.0

    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        area += x1 * y2 - x2 * y1

    return round(abs(area) / 2.0)


def generate_area_data(json_data):
    """ JSON 데이터를 사용하여 area_dict을 생성하고 className별로 그룹화하여 반환합니다. """
    area_dict_by_class = defaultdict(list)

    for instance in json_data["instances"]:
        class_name = instance["className"]
        points = [(instance["points"][i], instance["points"][i + 1]) for i in range(0, len(instance["points"]), 2)]

        # points를 [[x1,y1], [x2,y2], ...] 형식의 리스트로 변환
        points_list = [[x, y] for x, y in points]

        # 폴리곤 면적 계산
        area_size = calculate_polygon_area(points_list)

        # area_dict 형식으로 저장 (fill 추가)
        area_dict = {
            "class": class_name,
            "area_str": f"fill:{points_list}",
            "area_size": area_size
        }
        area_dict_by_class[class_name].append(area_dict)

    return area_dict_by_class


def process_directory(directory_path, exam_hist_id):
    """ 특정 디렉토리의 모든 JSON 파일을 처리하고 결과를 합산하여 반환합니다. """
    records = []

    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)
            img_nm = os.path.splitext(filename)[0]  # .json을 제거하여 이미지 파일명 추출

            # JSON 파일 불러오기
            json_data = load_json(file_path)

            # area_dict 생성 및 저장
            area_dict_by_class = generate_area_data(json_data)

            for class_name, area_data_list in area_dict_by_class.items():
                if class_name in seg_cd_dict:
                    cd = seg_cd_dict[class_name]
                    area_str_combined = '|'.join([entry['area_str'] for entry in area_data_list])
                    area_size_combined = sum(entry['area_size'] for entry in area_data_list)
                    records.append({
                        "SEG_CD": cd,
                        "IMG_NM": img_nm,
                        "EXAM_HIST_ID": exam_hist_id,
                        "AREA": area_str_combined,
                        "PIXEL_COUNT": area_size_combined
                    })

    return records


def main():
    # JSON 파일들이 있는 디렉토리 경로 목록
    directory_paths = [
        '/Users/gadeoghyeon/Downloads/NAVERWORKS/AR라벨링 수정본/421972_69_M/421972_69_M'
    ]

    # EXAM_HIST_ID 지정
    exam_hist_id = "Q8iNHgXczxFfxzMdu7BCDH7dkvbrFmvH"

    all_records = []

    for directory_path in directory_paths:
        records = process_directory(directory_path, exam_hist_id)
        all_records.extend(records)

    # 상위 디렉토리 경로 가져오기
    parent_dir = os.path.abspath(os.path.join(directory_paths[0], os.pardir))
    # db 폴더 경로 설정
    db_folder_path = os.path.join(parent_dir, 'db')
    os.makedirs(db_folder_path, exist_ok=True)

    # DataFrame 생성
    df = pd.DataFrame(all_records, columns=["SEG_CD", "IMG_NM", "EXAM_HIST_ID", "AREA", "PIXEL_COUNT"])

    # 결과를 CSV 파일로 저장
    csv_file_path = os.path.join(db_folder_path, 'output.csv')
    df.to_csv(csv_file_path, index=False, encoding='utf-8')


# 스크립트 실행
if __name__ == "__main__":
    main()
