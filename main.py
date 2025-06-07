import sys
import os
from src.braille_translator import text_to_braille, braille_to_text
from src.braille_image import image_to_braille_list, save_braille_sample
from src.braille_utils import safe_filename, validate_braille_str
import numpy as np

def braille_list_to_str(braille_list):
    return ' '.join(''.join(str(dot) for dot in cell) for cell in braille_list)

def braille_list_to_unicode(braille_list):
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
    cells = s.strip().split()
    if not validate_braille_str(s):
        raise ValueError("점자(01문자열) 입력은 6자리 0/1만 공백으로 구분해야 합니다.")
    return [[int(c) for c in cell] for cell in cells]

def unicode_to_braille_list(braille_unicode):
    braille_list = []
    for ch in braille_unicode:
        code = ord(ch) - 0x2800
        cell = [(code >> i) & 1 for i in range(6)]
        braille_list.append(cell)
    return braille_list

def prompt_with_example(prompt, example):
    return input(f"{prompt}\n(예시: {example})\n입력: ")

if __name__ == "__main__":
    while True:
        print("모드 선택:")
        print("1: 텍스트 → 점자(약자 우선 변환)")
        print("2: 텍스트 → 점자(초/중/종 조합형 변환)")
        print("3: 점자(01문자열) → 텍스트")
        print("4: 점자(유니코드) → 텍스트")
        print("5: 점자 이미지 → 텍스트")
        print("q: 종료")
        mode = input("모드 번호 입력: ").strip()

        if mode == "1":
            while True:
                try:
                    text = prompt_with_example("변환할 텍스트를 입력하세요.", "안녕하세요 123 Hello!")
                    braille = text_to_braille(text, use_abbreviation=True)
                    sample_dir = save_braille_sample(braille, text)
                    print(f"dot.png와 텍스트가 {sample_dir}에 저장되었습니다.")
                    print("점자(01문자열):", braille_list_to_str(braille))
                    print("점자(유니코드):", braille_list_to_unicode(braille))
                    break
                except Exception as e:
                    print(f"에러: {e}\n다시 시도하세요.")

        elif mode == "2":
            while True:
                try:
                    text = prompt_with_example("변환할 텍스트를 입력하세요.", "반갑습니다")
                    braille = text_to_braille(text, use_abbreviation=False)
                    sample_dir = save_braille_sample(braille, text)
                    print(f"dot.png와 텍스트가 {sample_dir}에 저장되었습니다.")
                    print("점자(01문자열):", braille_list_to_str(braille))
                    print("점자(유니코드):", braille_list_to_unicode(braille))
                    break
                except Exception as e:
                    print(f"에러: {e}\n다시 시도하세요.")

        elif mode == "3":
            while True:
                try:
                    s = prompt_with_example(
                        "점자(01문자열, 공백구분) 입력", "100000 110000 100100 100110 100010"
                    )
                    braille = str_to_braille_list(s)
                    text = braille_to_text(braille)
                    print("복원된 텍스트:", text)
                    break
                except Exception as e:
                    print(f"에러: {e}\n다시 시도하세요.")

        elif mode == "4":
            while True:
                try:
                    braille_unicode = prompt_with_example(
                        "점자(유니코드) 입력", "⠉⠕⠙⠑"
                    )
                    braille = unicode_to_braille_list(braille_unicode)
                    text = braille_to_text(braille)
                    print("복원된 텍스트:", text)
                    break
                except Exception as e:
                    print(f"에러: {e}\n다시 시도하세요.")

        elif mode == "5":
            while True:
                try:
                    img_path = prompt_with_example(
                        "점자 이미지 파일 경로 입력", "data/1/dot.png"
                    )
                    braille = image_to_braille_list(img_path)
                    text = braille_to_text(braille)
                    print("복원된 텍스트:", text)
                    break
                except Exception as e:
                    print(f"에러: {e}\n다시 시도하세요.")

        elif mode.lower() == "q":
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 입력입니다. 다시 선택해주세요.")