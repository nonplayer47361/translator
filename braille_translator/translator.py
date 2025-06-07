import hgtk
from typing import List, Union
from src.braille_table import (
    ENGLISH_TO_BRAILLE, HANGUL_BRAILLE_ABBREVIATION, INITIAL_TO_BRAILLE,
    MEDIAL_TO_BRAILLE, FINAL_TO_BRAILLE, SPECIAL_TO_BRAILLE,
    CAPITAL_PREFIX, NUMBER_PREFIX, NUM_TO_BRAILLE_LETTER,
    BRAILLE_TO_INITIAL, BRAILLE_TO_MEDIAL, BRAILLE_TO_FINAL,
    BRAILLE_TO_HANGUL_ABBREVIATION, BRAILLE_TO_ENGLISH, BRAILLE_TO_SPECIAL
)
from src.braille_utils import flatten_braille_cell

def text_to_braille(text: str) -> List[List[int]]:
    """
    텍스트(한글/영문/숫자/특수문자)를 점자 배열로 변환
    """
    braille_output = []
    i = 0
    while i < len(text):
        matched = False
        # 약자(최장매칭)
        for abbr in sorted(HANGUL_BRAILLE_ABBREVIATION.keys(), key=len, reverse=True):
            if text.startswith(abbr, i):
                braille_output.append(HANGUL_BRAILLE_ABBREVIATION[abbr])
                i += len(abbr)
                matched = True
                break
        if matched:
            continue

        char = text[i]
        # 한글 음절 분리
        if hgtk.checker.is_hangul(char):
            try:
                cho, jung, jong = hgtk.letter.decompose(char)
                if cho in INITIAL_TO_BRAILLE:
                    braille_output.append(INITIAL_TO_BRAILLE[cho])
                if jung in MEDIAL_TO_BRAILLE:
                    braille_output.append(MEDIAL_TO_BRAILLE[jung])
                if jong != ' ' and jong in FINAL_TO_BRAILLE:
                    value = FINAL_TO_BRAILLE[jong]
                    braille_output.extend(flatten_braille_cell(value))
            except hgtk.exception.NotHangulException:
                braille_output.append([0,0,0,0,0,0])
        elif char in ENGLISH_TO_BRAILLE:
            braille_output.append(ENGLISH_TO_BRAILLE[char])
        elif char.isupper():
            braille_output.append(CAPITAL_PREFIX)
            braille_output.append(ENGLISH_TO_BRAILLE[char.lower()])
        elif char.isdigit():
            braille_output.append(NUMBER_PREFIX)
            braille_output.append(ENGLISH_TO_BRAILLE[NUM_TO_BRAILLE_LETTER[char]])
        elif char in SPECIAL_TO_BRAILLE:
            braille_output.append(SPECIAL_TO_BRAILLE[char])
        else:
            braille_output.append([0,0,0,0,0,0])
        i += 1
    return braille_output

def braille_to_text(braille: List[List[int]]) -> str:
    """
    점자 배열을 텍스트(한글/영문/숫자/특수문자)로 복원
    """
    text_output = ""
    i = 0
    n = len(braille)
    while i < n:
        matched = False
        # 약자(최장매칭) 역변환
        for abbr, v in HANGUL_BRAILLE_ABBREVIATION.items():
            v_cells = [tuple(cell) for cell in flatten_braille_cell(v)]
            if i + len(v_cells) <= n and all(tuple(braille[i+j]) == v_cells[j] for j in range(len(v_cells))):
                text_output += abbr
                i += len(v_cells)
                matched = True
                break
        if matched:
            continue

        # 한글 초성/중성/종성 조합
        if (
            i+1 < n and
            tuple(braille[i]) in BRAILLE_TO_INITIAL and
            tuple(braille[i+1]) in BRAILLE_TO_MEDIAL
        ):
            cho = BRAILLE_TO_INITIAL[tuple(braille[i])]
            jung = BRAILLE_TO_MEDIAL[tuple(braille[i+1])]
            i += 2
            jong = ''
            if i < n and tuple(braille[i]) in BRAILLE_TO_FINAL:
                jong = BRAILLE_TO_FINAL[tuple(braille[i])]
                i += 1
            text_output += hgtk.letter.compose(cho, jung, jong)
            continue

        # 영문/특수문자/숫자
        if tuple(braille[i]) == tuple(CAPITAL_PREFIX):
            if i+1 < n and tuple(braille[i+1]) in BRAILLE_TO_ENGLISH:
                text_output += BRAILLE_TO_ENGLISH[tuple(braille[i+1])].upper()
                i += 2
                continue
        if tuple(braille[i]) == tuple(NUMBER_PREFIX):
            if i+1 < n and tuple(braille[i+1]) in BRAILLE_TO_ENGLISH:
                letter = BRAILLE_TO_ENGLISH[tuple(braille[i+1])]
                for k, v in NUM_TO_BRAILLE_LETTER.items():
                    if v == letter:
                        text_output += k
                        break
                i += 2
                continue
        if tuple(braille[i]) in BRAILLE_TO_ENGLISH:
            text_output += BRAILLE_TO_ENGLISH[tuple(braille[i])]
            i += 1
            continue
        if tuple(braille[i]) in BRAILLE_TO_SPECIAL:
            text_output += BRAILLE_TO_SPECIAL[tuple(braille[i])]
            i += 1
            continue
        # 알 수 없는 점자
        i += 1
    return text_output