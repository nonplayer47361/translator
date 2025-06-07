import sys
import os
import hgtk
import cv2
import numpy as np
import re
from src.translator import text_to_braille, braille_to_text

# 점자 배열을 01문자열로 변환
def braille_list_to_str(braille_list):
    return ' '.join(''.join(str(dot) for dot in cell) for cell in braille_list)

# 점자 배열을 유니코드 점자문자로 변환
def braille_list_to_unicode(braille_list):
    # 셀 내부에 2셀 이상(겹받침, 약자 등)이 있으면 평탄화
    flat = []
    for cell in braille_list:
        if isinstance(cell[0], list):  # 2셀 이상
            flat.extend(cell)
        else:
            flat.append(cell)
    def dots_to_unicode(cell):
        value = 0
        for i, dot in enumerate(cell):
            if dot:
                value |= (1 << i)
        return chr(0x2800 + value)
    return ''.join(dots_to_unicode(cell) for cell in flat)

# 01문자열을 점자 배열로 변환
def str_to_braille_list(braille_str):
    return [[int(dot) for dot in cell] for cell in braille_str.strip().split()]

# 유니코드 점자문자열을 점자 배열로 변환
def unicode_to_braille_list(braille_unicode):
    braille_list = []
    for ch in braille_unicode:
        code = ord(ch) - 0x2800
        cell = [(code >> i) & 1 for i in range(6)]
        braille_list.append(cell)
    return braille_list

# 점자 배열로 이미지 생성 (OpenCV)
def braille_to_image(braille_list, text, cell_size=40, dot_radius=7, margin=20):
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
    cv2.imwrite(filename, img)
    return filename

# 점자 이미지에서 점자 배열 복원 (간단 버전, 실제 사용시 보정 필요)
def image_to_braille_list(img_path, cell_size=40, dot_radius=7, margin=20):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(img_path)
    cols = (img.shape[1] - 2 * margin) // cell_size
    braille_list = []
    dot_pos = [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2)]
    for idx in range(cols):
        x0 = margin + idx * cell_size
        y0 = margin
        cell = []
        for (dx, dy) in dot_pos:
            cx = x0 + dx * (cell_size//2) + cell_size//4
            cy = y0 + dy * (cell_size//3) + cell_size//6
            # 원 중심 픽셀값이 어두우면 점자
            if img[cy, cx] < 128:
                cell.append(1)
            else:
                cell.append(0)
        braille_list.append(cell)
    return braille_list

def safe_filename(text):
    return re.sub(r'[\\/:*?"<>| ]', '_', text)

def get_next_data_folder(base_dir="data"):
    os.makedirs(base_dir, exist_ok=True)
    existing = [int(name) for name in os.listdir(base_dir) if name.isdigit()]
    next_num = max(existing, default=0) + 1
    folder = os.path.join(base_dir, str(next_num))
    os.makedirs(folder, exist_ok=True)
    return folder, next_num

def save_braille_image_and_text(braille_list, text, base_dir="data", cell_size=40, dot_radius=7, margin=20):
    folder, num = get_next_data_folder(base_dir)
    img_w = len(braille_list) * cell_size + 2 * margin
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
    img_filename = os.path.join(folder, f"{num}_dot.png")
    txt_filename = os.path.join(folder, f"{num}.txt")
    cv2.imwrite(img_filename, img)
    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write(text)
    return img_filename, txt_filename

if __name__ == "__main__":
    print("모드 선택:")
    print("1: 텍스트 → 점자(약자 우선 변환)")
    print("2: 텍스트 → 점자(초/중/종 조합형 변환)")
    print("3: 점자(01문자열) → 텍스트")
    print("4: 점자(유니코드) → 텍스트")
    print("5: 점자 이미지 → 텍스트")
    mode = input("모드 번호 입력: ").strip()

    if mode == "1":
        text = input("변환할 텍스트 입력: ")
        braille = text_to_braille(text, use_abbreviation=True)  # 약자 우선
        print("점자(01문자열):", braille_list_to_str(braille))
        print("점자(유니코드):", braille_list_to_unicode(braille))
        img_path, txt_path = save_braille_image_and_text(braille, text)
        print(f"점자 이미지가 {img_path}로 저장되었습니다.")
        print(f"입력 텍스트가 {txt_path}에 기록되었습니다.")
    elif mode == "2":
        text = input("변환할 텍스트 입력: ")
        braille = text_to_braille(text, use_abbreviation=False)  # 초/중/종 조합형만
        print("점자(01문자열):", braille_list_to_str(braille))
        print("점자(유니코드):", braille_list_to_unicode(braille))
        img_path, txt_path = save_braille_image_and_text(braille, text)
        print(f"점자 이미지가 {img_path}로 저장되었습니다.")
        print(f"입력 텍스트가 {txt_path}에 기록되었습니다.")
    elif mode == "3":
        braille_str = input("점자(01문자열, 공백구분) 입력: ")
        braille = str_to_braille_list(braille_str)
        text = braille_to_text(braille)
        print("복원된 텍스트:", text)
    elif mode == "4":
        braille_unicode = input("점자(유니코드) 입력: ")
        braille = unicode_to_braille_list(braille_unicode)
        text = braille_to_text(braille)
        print("복원된 텍스트:", text)
    elif mode == "5":
        img_path = input("점자 이미지 파일 경로 입력: ")
        braille = image_to_braille_list(img_path)
        text = braille_to_text(braille)
        print("복원된 텍스트:", text)
    else:
        print("잘못된 입력입니다.")