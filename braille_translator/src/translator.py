import hgtk
import re
import numpy as np
import cv2
from typing import List, Union
from src.braille_tabble import (
    INITIAL_TO_BRAILLE, MEDIAL_TO_BRAILLE, FINAL_TO_BRAILLE,
    ALPHABET_TO_BRAILLE, ENGLISH_TO_BRAILLE, NUMBER_TO_BRAILLE,
    SYMBOL_TO_BRAILLE, HANGUL_BRAILLE_ABBREVIATION,
    REVERSE_INITIAL_TO_BRAILLE, REVERSE_MEDIAL_TO_BRAILLE, REVERSE_FINAL_TO_BRAILLE,
    REVERSE_ALPHABET_TO_BRAILLE, REVERSE_ENGLISH_TO_BRAILLE, REVERSE_NUMBER_TO_BRAILLE,
    REVERSE_SYMBOL_TO_BRAILLE, REVERSE_HANGUL_BRAILLE_ABBREVIATION
)
from src.braille_utils import flatten_braille_cell

def text_to_braille(text: str, use_abbreviation: bool = True) -> List[List[int]]:
    """
    텍스트(한글/영문/숫자/특수문자)를 점자 배열로 변환
    use_abbreviation: True면 약자 우선, False면 무조건 초/중/종 조합형
    """
    braille_output = []
    i = 0
    while i < len(text):
        matched = False
        # 약자(최장매칭) 우선 처리
        if use_abbreviation:
            for abbr in sorted(HANGUL_BRAILLE_ABBREVIATION.keys(), key=len, reverse=True):
                if text.startswith(abbr, i):
                    braille_output.extend(flatten_braille_cell(HANGUL_BRAILLE_ABBREVIATION[abbr]))
                    i += len(abbr)
                    matched = True
                    break
            if matched:
                continue

        char = text[i]
        # 2. 한글 음절 분리
        if hgtk.checker.is_hangul(char):
            try:
                cho, jung, jong = hgtk.letter.decompose(char)
                if cho in INITIAL_TO_BRAILLE:
                    braille_output.extend(flatten_braille_cell(INITIAL_TO_BRAILLE[cho]))
                if jung in MEDIAL_TO_BRAILLE:
                    braille_output.extend(flatten_braille_cell(MEDIAL_TO_BRAILLE[jung]))
                if jong != ' ' and jong in FINAL_TO_BRAILLE:
                    braille_output.extend(flatten_braille_cell(FINAL_TO_BRAILLE[jong]))
            except hgtk.exception.NotHangulException:
                braille_output.append([0,0,0,0,0,0])
        elif char in ENGLISH_TO_BRAILLE:
            braille_output.extend(flatten_braille_cell(ENGLISH_TO_BRAILLE[char]))
        elif char in INITIAL_TO_BRAILLE:
            braille_output.extend(flatten_braille_cell(INITIAL_TO_BRAILLE[char]))
        elif char in MEDIAL_TO_BRAILLE:
            braille_output.extend(flatten_braille_cell(MEDIAL_TO_BRAILLE[char]))
        elif char in FINAL_TO_BRAILLE:
            braille_output.extend(flatten_braille_cell(FINAL_TO_BRAILLE[char]))
        elif char in SYMBOL_TO_BRAILLE:
            braille_output.extend(flatten_braille_cell(SYMBOL_TO_BRAILLE[char]))
        elif char in NUMBER_TO_BRAILLE:
            braille_output.extend(flatten_braille_cell(NUMBER_TO_BRAILLE[char]))
        elif char.isupper():
            # 대문자 접두점(예시, 필요시 추가)
            braille_output.append([0,0,0,0,0,1])  # 대문자 접두점 예시
            braille_output.extend(flatten_braille_cell(ENGLISH_TO_BRAILLE[char.lower()]))
        else:
            braille_output.append([0,0,0,0,0,0])
        i += 1

    return braille_output

def braille_to_text(braille: List[List[int]]) -> str:
    """
    점자 배열을 텍스트로 복원
    """
    text_output = ""
    i = 0
    while i < len(braille):
        # 1. 약자(최장매칭) 역변환
        matched = False
        for abbr, v in HANGUL_BRAILLE_ABBREVIATION.items():
            v_flat = flatten_braille_cell(v)
            if i + len(v_flat) <= len(braille) and all(tuple(braille[i+j]) == tuple(v_flat[j]) for j in range(len(v_flat))):
                text_output += abbr
                i += len(v_flat)
                matched = True
                break
        if matched:
            continue

        # 2. 한글 초성/중성/종성 조합
        if i+1 < len(braille) and tuple(braille[i]) in REVERSE_INITIAL_TO_BRAILLE and tuple(braille[i+1]) in REVERSE_MEDIAL_TO_BRAILLE:
            cho = REVERSE_INITIAL_TO_BRAILLE[tuple(braille[i])]
            jung = REVERSE_MEDIAL_TO_BRAILLE[tuple(braille[i+1])]
            i += 2
            jong = ''
            if i < len(braille) and tuple(braille[i]) in REVERSE_FINAL_TO_BRAILLE:
                jong = REVERSE_FINAL_TO_BRAILLE[tuple(braille[i])]
                i += 1
            text_output += hgtk.letter.compose(cho, jung, jong)
            continue

        # 3. 영문/특수문자/숫자
        if tuple(braille[i]) in REVERSE_ENGLISH_TO_BRAILLE:
            text_output += REVERSE_ENGLISH_TO_BRAILLE[tuple(braille[i])]
            i += 1
            continue
        if tuple(braille[i]) in REVERSE_NUMBER_TO_BRAILLE:
            text_output += REVERSE_NUMBER_TO_BRAILLE[tuple(braille[i])]
            i += 1
            continue
        if tuple(braille[i]) in REVERSE_SYMBOL_TO_BRAILLE:
            text_output += REVERSE_SYMBOL_TO_BRAILLE[tuple(braille[i])]
            i += 1
            continue

        # 알 수 없는 점자
        i += 1

    return text_output

def braille_list_to_unicode(braille_list):
    def dots_to_unicode(cell):
        value = 0
        for i, dot in enumerate(cell):
            if dot:
                value |= (1 << i)
        return chr(0x2800 + value)
    return ''.join(dots_to_unicode(cell) for cell in braille_list)

def safe_filename(text):
    # 파일명에 사용할 수 없는 문자 제거
    return re.sub(r'[\\/:*?"<>| ]', '_', text)

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