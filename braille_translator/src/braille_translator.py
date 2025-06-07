import hgtk
import re
import numpy as np
import cv2
from typing import List, Union
from braille_translator.src.braille_table import (
    INITIAL_TO_BRAILLE, MEDIAL_TO_BRAILLE, FINAL_TO_BRAILLE,
    ALPHABET_TO_BRAILLE, ENGLISH_TO_BRAILLE, NUMBER_TO_BRAILLE,
    SYMBOL_TO_BRAILLE, HANGUL_BRAILLE_ABBREVIATION,
    REVERSE_INITIAL_TO_BRAILLE, REVERSE_MEDIAL_TO_BRAILLE, REVERSE_FINAL_TO_BRAILLE,
    REVERSE_ALPHABET_TO_BRAILLE, REVERSE_ENGLISH_TO_BRAILLE, REVERSE_NUMBER_TO_BRAILLE,
    REVERSE_SYMBOL_TO_BRAILLE, REVERSE_HANGUL_BRAILLE_ABBREVIATION
)
from src.braille_utils import flatten_braille_cell, tupleize

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
        # 1. 숫자 처리 (숫자가 연속될 경우 수표는 한 번만)
        if char.isdigit():
            if i == 0 or not text[i-1].isdigit():
                braille_output.extend(flatten_braille_cell(NUMBER_TO_BRAILLE[char])[0:1])
            braille_output.extend(flatten_braille_cell(NUMBER_TO_BRAILLE[char])[1:])
            i += 1
            continue

        # 2. 한글 음절 분리
        if hgtk.checker.is_hangul(char):
            try:
                cho, jung, jong = hgtk.letter.decompose(char)
                if cho in INITIAL_TO_BRAILLE:
                    braille_output.extend(flatten_braille_cell(INITIAL_TO_BRAILLE[cho]))
                if jung in MEDIAL_TO_BRAILLE:
                    braille_output.extend(flatten_braille_cell(MEDIAL_TO_BRAILLE[jung]))
                if jong and jong in FINAL_TO_BRAILLE:
                    braille_output.extend(flatten_braille_cell(FINAL_TO_BRAILLE[jong]))
            except hgtk.exception.NotHangulException:
                braille_output.append([0,0,0,0,0,0])
        elif char.isupper():
            braille_output.append([0,0,0,0,0,1])
            braille_output.extend(flatten_braille_cell(ENGLISH_TO_BRAILLE[char.lower()]))
        elif char in ENGLISH_TO_BRAILLE:
            braille_output.extend(flatten_braille_cell(ENGLISH_TO_BRAILLE[char]))
        elif char in SYMBOL_TO_BRAILLE:
            braille_output.extend(flatten_braille_cell(SYMBOL_TO_BRAILLE[char]))
        else:
            braille_output.append([0,0,0,0,0,0])
        i += 1

    return braille_output

# --- 역변환 통합 및 최장매칭 우선 ---
REVERSE_ALL = {
    **REVERSE_HANGUL_BRAILLE_ABBREVIATION,
    **REVERSE_NUMBER_TO_BRAILLE,
    **REVERSE_SYMBOL_TO_BRAILLE,
    **REVERSE_ALPHABET_TO_BRAILLE,
}
SORTED_REVERSE_ALL = sorted(REVERSE_ALL.items(), key=lambda item: len(flatten_braille_cell(list(item[0]))), reverse=True)

def braille_to_text(braille: List[List[int]]) -> str:
    """
    점자 배열을 텍스트로 복원 (최장매칭 우선)
    """
    text_output = ""
    i = 0
    n = len(braille)
    CAPITAL_PREFIX = tuple([0,0,0,0,0,1])
    NUMBER_PREFIX = tuple([0,0,1,1,1,1])

    while i < n:
        # 1. 대문자 처리
        if tuple(braille[i]) == CAPITAL_PREFIX and i + 1 < n:
            next_cell = tuple(braille[i+1])
            if next_cell in REVERSE_ALPHABET_TO_BRAILLE:
                text_output += REVERSE_ALPHABET_TO_BRAILLE[next_cell].upper()
                i += 2
                continue

        # 2. 숫자 처리 (수표 다음부터는 연속된 숫자 문자로 변환)
        if tuple(braille[i]) == NUMBER_PREFIX:
            i += 1
            while i < n:
                found_num = False
                for num_char, braille_val in NUMBER_TO_BRAILLE.items():
                    num_braille_part = tuple(flatten_braille_cell(braille_val)[1])
                    if tuple(braille[i]) == num_braille_part:
                        text_output += num_char
                        i += 1
                        found_num = True
                        break
                if not found_num:
                    break
            continue

        # 3. 약자, 기호, 영문(소문자) 등 통합 테이블에서 최장 길이 우선 매칭
        matched = False
        for pattern_tuple, char in SORTED_REVERSE_ALL:
            pattern_list = flatten_braille_cell(list(pattern_tuple))
            pattern_len = len(pattern_list)
            if i + pattern_len <= n and all(braille[i+j] == pattern_list[j] for j in range(pattern_len)):
                text_output += char
                i += pattern_len
                matched = True
                break
        if matched:
            continue

        # 4. 한글 초성/중성/종성 조합
        try:
            if i + 1 < n and tuple(braille[i]) in REVERSE_INITIAL_TO_BRAILLE and tuple(braille[i+1]) in REVERSE_MEDIAL_TO_BRAILLE:
                cho = REVERSE_INITIAL_TO_BRAILLE[tuple(braille[i])]
                jung = REVERSE_MEDIAL_TO_BRAILLE[tuple(braille[i+1])]
                i += 2
                jong = ''
                if i < n and tuple(braille[i]) in REVERSE_FINAL_TO_BRAILLE:
                    jong = REVERSE_FINAL_TO_BRAILLE[tuple(braille[i])]
                    i += 1
                text_output += hgtk.letter.compose(cho, jung, jong if jong else None)
                continue
        except Exception:
            pass

        # 5. 매칭되는 것이 아무것도 없을 경우, 인덱스를 1 증가시켜 무한 루프 방지
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