import os
import tempfile
from src.translator import text_to_braille, braille_to_text
from src.braille_utils import braille_list_to_unicode, safe_filename
from src.braille_image import image_to_braille_list
import cv2
import numpy as np

def generate_braille_image(
    braille_list,
    text,
    cell_size=40,
    dot_radius=7,
    margin=20,
    debug_dir=None
):
    """
    점자 배열로 점자 이미지를 생성하고 경로를 반환합니다.
    debug_dir가 지정되면 이미지를 해당 폴더에 저장합니다.
    """
    cols = len(braille_list)
    img_w = cols * cell_size + 2 * margin
    img_h = cell_size + 2 * margin
    img = np.ones((img_h, img_w, 3), dtype=np.uint8) * 255

    dot_pos = [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2)]
    for idx, cell in enumerate(braille_list):
        x0 = margin + idx * cell_size
        y0 = margin
        for i, (dx, dy) in enumerate(dot_pos):
            if cell[i]:
                cx = x0 + dx * (cell_size//2) + cell_size//4
                cy = y0 + dy * (cell_size//3) + cell_size//6
                cv2.circle(img, (cx, cy), dot_radius, (0,0,0), -1)
    filename = f"{safe_filename(text)}_dot.png"
    if debug_dir:
        file_path = os.path.join(debug_dir, filename)
    else:
        file_path = filename
    cv2.imwrite(file_path, img)
    return file_path

def run_e2e_test(
    text,
    cell_size=40,
    dot_radius=7,
    margin=20,
    debug=True,
    show_steps=False
):
    """
    텍스트 → 점자배열 → 점자이미지 → 점자이미지 인식 → 점자배열 → 텍스트 end-to-end 테스트
    파라미터(cell_size 등)를 생성/인식에 모두 사용 (동기화)
    """
    print("원본 텍스트:", text)
    # 1. 텍스트 → 점자 배열
    braille = text_to_braille(text)
    print("점자 배열:", braille)
    print("점자 유니코드:", braille_list_to_unicode(braille))

    # 2. 점자 배열 → 이미지 생성
    with tempfile.TemporaryDirectory() as debug_dir:
        img_path = generate_braille_image(
            braille, text,
            cell_size=cell_size, dot_radius=dot_radius, margin=margin,
            debug_dir=debug_dir if debug else None
        )
        print("생성된 이미지:", img_path)

        if debug or show_steps:
            img = cv2.imread(img_path)
            cv2.imshow("생성된 점자 이미지", img)
            cv2.waitKey(500)
            cv2.destroyAllWindows()

        # 3. 점자 이미지 → 점자배열 (파라미터 자동 동기화)
        braille_from_img = image_to_braille_list(
            img_path,
            show_steps=show_steps,
            cell_size=cell_size,
            dot_radius=dot_radius,
            margin=margin
        )
        print("이미지에서 추출된 점자 배열:", braille_from_img)
        print("이미지→유니코드:", braille_list_to_unicode(braille_from_img))

        # 4. 점자 배열 → 텍스트 복원
        text_restored = braille_to_text(braille_from_img)
        print("복원된 텍스트:", text_restored)

        # 5. 디버그용 시각화 및 비교
        if debug or show_steps:
            print("원본과 복원 텍스트가 같은가?", text == text_restored)
            print("원본 점자 배열 == 이미지 추출 점자 배열?", braille == braille_from_img)
            img = cv2.imread(img_path)
            cv2.imshow("최종 점자 이미지", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return {
            "original_text": text,
            "braille_array": braille,
            "braille_unicode": braille_list_to_unicode(braille),
            "image_path": img_path,
            "braille_from_img": braille_from_img,
            "braille_unicode_from_img": braille_list_to_unicode(braille_from_img),
            "restored_text": text_restored,
            "success": (text == text_restored)
        }

if __name__ == "__main__":
    cell_size = 40
    dot_radius = 7
    margin = 20
    texts = [
        "한글abc123",
        "가나다라마바사",
        "hello world",
        "점자 변환 테스트!"
    ]
    for text in texts:
        print("="*40)
        result = run_e2e_test(
            text,
            cell_size=cell_size,
            dot_radius=dot_radius,
            margin=margin,
            debug=True,
            show_steps=True
        )
        print(f"테스트 결과: {'성공' if result['success'] else '실패'}")
        print("="*40)