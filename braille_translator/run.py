import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.translator import text_to_braille, braille_to_text

def braille_list_to_str(braille_list):
    # 점자 배열을 01문자열로 변환 (예: [1,0,0,0,0,0] -> "100000")
    return ' '.join(''.join(str(dot) for dot in cell) for cell in braille_list)

def braille_list_to_unicode(braille_list):
    # 점자 배열을 유니코드 점자문자(⠁ 등)로 변환
    def dots_to_unicode(cell):
        # 6점식 점자: 유니코드 U+2800 + (점 위치별 비트값)
        # 점자 배열: [1,0,0,0,0,0] (점1~6)
        value = 0
        for i, dot in enumerate(cell):
            if dot:
                value |= (1 << i)
        return chr(0x2800 + value)
    return ''.join(dots_to_unicode(cell) for cell in braille_list)

def str_to_braille_list(braille_str):
    # 01문자열을 점자 배열로 변환 (예: "100000 110000" -> [[1,0,0,0,0,0],[1,1,0,0,0,0]])
    return [[int(dot) for dot in cell] for cell in braille_str.strip().split()]

if __name__ == "__main__":
    mode = input("모드 선택 (1: 텍스트→점자, 2: 점자→텍스트): ").strip()
    if mode == "1":
        text = input("변환할 텍스트 입력: ")
        braille = text_to_braille(text)
        print("점자(01문자열):", braille_list_to_str(braille))
        print("점자(유니코드):", braille_list_to_unicode(braille))
    elif mode == "2":
        braille_str = input("변환할 점자(01문자열, 공백구분) 입력: ")
        braille = str_to_braille_list(braille_str)
        text = braille_to_text(braille)
        print("변환된 텍스트:", text)
    else:
        print("잘못된 입력입니다.")