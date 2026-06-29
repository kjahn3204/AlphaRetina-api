import os
from typing import Any, Tuple

import cv2
import numpy as np
import onnxruntime
import torchvision.transforms.functional as TF
from PIL import Image


class SegmentationModel:
    def __init__(self, config:Any):
        segment_config = config['ai']['segment_model']
        model_path = segment_config['model_path']
        num_threads = segment_config.get('num_threads', config['ai'].get('num_threads', 4))
        root_path = config['api']['mount']['data']
        sess_options = onnxruntime.SessionOptions()
        sess_options.intra_op_num_threads = num_threads
        self.model = onnxruntime.InferenceSession(model_path, sess_options=sess_options,
                                                  providers=["CPUExecutionProvider"])
        self.input_name = self.model.get_inputs()[0].name

    def pad2square(self, image, size:int):
        _, h, w = image.shape
        new_size = (
            (size, int(size * w / h))
            if h > w
            else (int(size * h / w), size)
        )
        image = TF.resize(image, new_size)

        padding = (
            (size - new_size[1]) // 2,
            (size - new_size[0]) // 2,
            (size - new_size[1] + 1) // 2,
            (size - new_size[0] + 1) // 2,
        )

        return TF.pad(image, padding, fill=0), padding, new_size

    def unpad_image(self, padded_image, padding, new_size):
        resized_h, resized_w = new_size

        # 패딩을 제거하여 리사이즈된 크기로 돌려놓음
        unpadded_image = padded_image[
                         :, padding[1]: padding[1] + resized_h, padding[0]: padding[0] + resized_w
                         ]

        return unpadded_image

    def load_and_resize_img(self, input_img_path: str, size=768):
        if not os.path.exists(input_img_path):
            raise FileNotFoundError(f"Image file not found: {input_img_path}")
        image = Image.open(input_img_path).convert("RGB")
        tf_image = TF.to_tensor(image)
        sq_image, padding, new_size = self.pad2square(tf_image, size)
        normalized_image = TF.normalize(
            sq_image, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
        )
        normalized_image = normalized_image.unsqueeze(0).cpu().numpy()

        resized_img = self.unpad_image(sq_image, padding, new_size)
        resized_img = TF.to_pil_image(resized_img)

        return normalized_image, resized_img, padding, new_size

    def mask2polygon(self, mask):
        # 이미지 형식을 CV_8UC1으로 변환
        mask = (mask * 255).astype(np.uint8)

        # 경계선 찾기 (OpenCV 사용)
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        count = np.count_nonzero(mask)

        fill = []
        transparent = []

        def process_contour(idx):
            if idx < len(contours):
                contour = contours[idx].squeeze()
                if len(contour.shape) == 1:
                    contour = contour.reshape(1, -1)

                if hierarchy[0][idx][3] == -1:
                    fill.append(contour.tolist())
                else:
                    transparent.append(contour.tolist())

                # 자식 경계선 처리
                child_idx = hierarchy[0][idx][2]
                while child_idx != -1:
                    process_contour(child_idx)
                    child_idx = hierarchy[0][child_idx][0]

        if hierarchy is not None:
            # 최상위 경계선 처리
            current_idx = 0
            while current_idx != -1:
                process_contour(current_idx)
                current_idx = hierarchy[0][current_idx][0]
        else:
            # hierarchy가 None인 경우를 처리
            print("경계선을 찾지 못했습니다.")

        return [fill, transparent, count]

    async def evaluate(self, input_img_path:str) -> Tuple[list, str, np.ndarray, int, int]:
        normalized_image, resized_img, padding, new_size = self.load_and_resize_img(input_img_path)

        resized_img_path = os.path.splitext(input_img_path)[0] + "_resized.jpg"
        resized_img.save(resized_img_path)

        inputs = {self.input_name: normalized_image}
        outs = self.model.run(None, inputs)

        # 1*1*N*768*768
        pred_mask = outs[0]
        
        # 디버깅: 실제 shape 확인
        print(f"[DEBUG] pred_mask shape after model.run: {pred_mask.shape}")
        print(f"[DEBUG] pred_mask dtype: {pred_mask.dtype}")
        
        pred_mask = (pred_mask >= 0.5).astype(float)  # Threshold the mask
        
        print(f"[DEBUG] pred_mask shape after threshold: {pred_mask.shape}")

        unpadded_masks = [self.unpad_image(mask, padding, new_size) for mask in pred_mask]

        ## ai part ##
        polygon_list = [self.mask2polygon(mask) for mask in unpadded_masks[0]]

        # 텐서 생성 (predict_volume 로직 참고)
        # pred_mask는 (1, 19, 768, 768) 형태이므로 첫 번째 차원만 제거하여 (19, 768, 768)로 변환
        print(f"[DEBUG] Before squeeze - pred_mask.shape: {pred_mask.shape}")
        pred_mask_for_tensor = np.squeeze(pred_mask, axis=0)  # (19, 768, 768) - 첫 번째 차원만 제거
        print(f"[DEBUG] After squeeze - pred_mask_for_tensor.shape: {pred_mask_for_tensor.shape}")
        
        # predict_volume의 crop 로직: pred_mask[:, 136:-136, :] -> (19, 496, 768)
        # 768에서 136*2=272를 빼면 496이 됨
        if pred_mask_for_tensor.shape[1] == 768:
            pred_mask_cropped = pred_mask_for_tensor[:, 136:-136, :]  # (19, 496, 768)
        else:
            # 이미 다른 크기인 경우 그대로 사용
            pred_mask_cropped = pred_mask_for_tensor
        
        print(f"[DEBUG] Final pred_mask_cropped.shape: {pred_mask_cropped.shape}")
        
        # 리사이즈된 이미지의 크기 가져오기 (width, height)
        width, height = resized_img.size
        
        # numpy array를 반환 (torch tensor로 변환하지 않고 numpy array 그대로 반환)
        # Save and display the prediction results
        return polygon_list, resized_img_path.rsplit('/', 1)[1], pred_mask_cropped, width, height


class CategorizationModel:
    """카테고리 분류 모델 (ONNX 방식)"""
    
    def __init__(self, config: Any):
        category_config = config['ai']['category_model']
        model_path = category_config['model_path']
        num_threads = config['ai'].get('num_threads', 4)
        sess_options = onnxruntime.SessionOptions()
        sess_options.intra_op_num_threads = num_threads
        self.model = onnxruntime.InferenceSession(model_path, sess_options=sess_options,
                                                  providers=["CPUExecutionProvider"])
        self.input_name = self.model.get_inputs()[0].name
    
    def predict(self, volume_tensor: np.ndarray) -> str:
        """
        Volume 텐서를 입력받아 카테고리 분류 수행
        
        Args:
            volume_tensor: (19, 496, 768) 형태의 numpy array
            
        Returns:
            REFERRAL_CTGR 값: 'O', 'R', 'S', 'U' 중 하나
        """
        # REFERRAL_CTGR 매핑: 0→'O', 1→'R', 2→'S', 3→'U'
        category_mapping = ['O', 'R', 'S', 'U']
        
        try:
            # numpy array를 float32로 변환 (ONNX는 float32를 사용)
            volume = volume_tensor.astype(np.float32)
            
            # 배치 차원 추가: (1, 19, 496, 768)
            volume = np.expand_dims(volume, axis=0)
            
            # ONNX 모델 입력 준비
            inputs = {self.input_name: volume}
            
            # 추론 수행
            outputs = self.model.run(None, inputs)
            y_hat = outputs[0]  # (1, 4) 형태의 logits
            
            # 확률 계산
            exp_logits = np.exp(y_hat - np.max(y_hat, axis=1, keepdims=True))  # numerical stability
            probs = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)
            
            # argmax로 예측 클래스 결정
            pred_idx = np.argmax(y_hat, axis=1)[0]
            probs_flat = probs[0]  # 배치 차원 제거
            
            # 로그 출력
            print(f"[DEBUG] Category prediction logits: {y_hat[0]}")
            print(f"[DEBUG] Category prediction probabilities: {probs_flat}")
            print(f"[DEBUG] Predicted index: {pred_idx}")
            print(f"[DEBUG] Predicted category: {category_mapping[pred_idx]} (prob: {probs_flat[pred_idx]:.4f})")
            
            # 인덱스를 REFERRAL_CTGR 값으로 매핑
            if 0 <= pred_idx < len(category_mapping):
                return category_mapping[pred_idx]
            else:
                print(f"Warning: Invalid prediction index {pred_idx}, returning 'O'")
                return 'O'
                
        except Exception as e:
            print(f"Error during category prediction: {e}")
            import traceback
            traceback.print_exc()
            return 'O'




