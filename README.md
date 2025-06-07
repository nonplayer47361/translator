import sys
import os
from src.braille_translator import text_to_braille, braille_to_text
from src.braille_image import image_to_braille_list, braille_to_image
from src.braille_utils import safe_filename
import numpy as np

def braille_list_to_str(braille_list):
    """점자 배열을 01문자열(공백구분)로 변환"""
    return ' '.join(''.join(str(dot) for dot in cell) for cell in braille_list)

def braille_list_to_unicode(braille_list):
    """점자 배열을 유니코드 점자문자(⠁~)로 변환"""
    flat = []
    for cell in braille_list:
        if isinstance(cell[0], list):
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

def str_to_braille_list(s):
    """01문자열(공백구분) → 점자 배열"""
    cells = s.strip().split()
    return [[int(c) for c in cell] for cell in cells]

def unicode_to_braille_list(braille_unicode):
    """유니코드 점자문자 → 점자 배열"""
    braille_list = []
    for ch in braille_unicode:
        code = ord(ch) - 0x2800
        cell = [(code >> i) & 1 for i in range(6)]
        braille_list.append(cell)
    return braille_list

def get_next_data_folder(base_dir="data"):
    """data/폴더 내에서 다음 순번 폴더 경로 반환 및 생성"""
    os.makedirs(base_dir, exist_ok=True)
    existing = [int(name) for name in os.listdir(base_dir) if name.isdigit()]
    next_num = max(existing, default=0) + 1
    folder = os.path.join(base_dir, str(next_num))
    os.makedirs(folder, exist_ok=True)
    return folder, next_num

def save_braille_image_and_text(braille_list, text, base_dir="data", cell_size=40, dot_radius=7, margin=20):
    """
    data/순번/ 폴더에 점자이미지와 텍스트파일 저장, 경로 반환
    """
    from src.braille_image import braille_to_image
    folder, num = get_next_data_folder(base_dir)
    fname_base = safe_filename(text)
    img_filename = os.path.join(folder, f"{fname_base}_dot.png")
    txt_filename = os.path.join(folder, f"{fname_base}.txt")
    braille_to_image(braille_list, text, cell_size, dot_radius, margin, save_path=img_filename)
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
        braille = text_to_braille(text, use_abbreviation=True)
        print("점자(01문자열):", braille_list_to_str(braille))
        print("점자(유니코드):", braille_list_to_unicode(braille))
        img_path, txt_path = save_braille_image_and_text(braille, text)
        print(f"점자 이미지가 {img_path}로 저장되었습니다.")
        print(f"입력 텍스트가 {txt_path}에 기록되었습니다.")
    elif mode == "2":
        text = input("변환할 텍스트 입력: ")
        braille = text_to_braille(text, use_abbreviation=False)
        print("점자(01문자열):", braille_list_to_str(braille))
        print("점자(유니코드):", braille_list_to_unicode(braille))
        img_path, txt_path = save_braille_image_and_text(braille, text)
        print(f"점자 이미지가 {img_path}로 저장되었습니다.")
        print(f"입력 텍스트가 {txt_path}에 기록되었습니다.")
    elif mode == "3":
        s = input("점자(01문자열, 공백구분) 입력: ")
        braille = str_to_braille_list(s)
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