import hgtk
from typing import List, Union
from braille_table import (
    ALPHABET_TO_BRAILLE, HANGUL_BRAILLE_ABBREVIATION, INITIAL_TO_BRAILLE,
    MEDIAL_TO_BRAILLE, FINAL_TO_BRAILLE, SYMBOL_TO_BRAILLE, NUMBER_TO_BRAILLE,
    CAPITAL_PREFIX, NUMBER_PREFIX, SYMBOL_PREFIX,
    INV_ABBREV, INV_NUMBER, INV_SYMBOL, INV_ALPHA,
    INV_INITIAL, INV_MEDIAL, INV_FINAL,
)
from braille_utils import flatten_braille_cell, tupleize

# ambiguous symbol 목록 확장
AMBIGUOUS_SYMBOLS = {
    (0, 1, 1, 0, 0, 1): ("“", "?"),           # 여는 큰따옴표 / 물음표
    (1, 1, 1, 0, 0, 1): ("”", "!"),           # 닫는 큰따옴표 / 느낌표
    (0, 1, 0, 0, 0, 1): ("‘", ","),           # 여는 작은따옴표 / 쉼표
    (1, 1, 0, 0, 0, 1): ("’", ";"),           # 닫는 작은따옴표 / 세미콜론
    (0, 0, 1, 0, 0, 1): (".", ":"),           # 마침표 / 쌍점
    (1, 0, 0, 0, 0, 1): ("-", "~"),           # 하이픈 / 물결
    (0, 1, 0, 1, 0, 1): ("/", "\\"),          # 슬래시 / 백슬래시
    # 필요시 계속 추가
}

OPENING_CONTEXT_CHARS = {
    '', ' ', '\n', '\t', '\r',
    '(', '[', '{', '<',
    '"', "'", '“', '‘',
    ',', '.', '!', '?', ';', ':',
}
CLOSING_CONTEXT_CHARS = {
    ')', ']', '}', '>',
    '"', "'", '”', '’',
    '.', ',', '!', '?', ';', ':',
}

def is_korean_letter(c: str) -> bool:
    return '\uAC00' <= c <= '\uD7A3' or (len(c) == 1 and hgtk.checker.is_hangul(c))

def is_letter_or_digit(c: str) -> bool:
    return c.isalpha() or c.isdigit() or is_korean_letter(c)

def resolve_ambiguous_symbol(symbolkey, prev_char, next_cell, next_is_end):
    # 각 ambiguous symbol에 맞는 문맥 해석 규칙 적용
    # 큰따옴표/작은따옴표류
    if symbolkey == (0, 1, 1, 0, 0, 1):  # “ or ?
        if prev_char in OPENING_CONTEXT_CHARS:
            return "“"
        else:
            return "?"
    if symbolkey == (1, 1, 1, 0, 0, 1):  # ” or !
        # 닫는따옴표는 보통 직전이 글자/숫자/닫는괄호/마침표 등. 느낌표는 문장 끝/강조
        if prev_char and (is_letter_or_digit(prev_char) or prev_char in CLOSING_CONTEXT_CHARS):
            return "”"
        else:
            return "!"
    if symbolkey == (0, 1, 0, 0, 0, 1):  # ‘ or ,
        # 여는작은따옴표는 앞이 공백/기호류, 쉼표는 단어 뒤/숫자 뒤 등
        if prev_char in OPENING_CONTEXT_CHARS:
            return "‘"
        else:
            return ","
    if symbolkey == (1, 1, 0, 0, 0, 1):  # ’ or ;
        if prev_char and (is_letter_or_digit(prev_char) or prev_char in CLOSING_CONTEXT_CHARS):
            return "’"
        else:
            return ";"
    if symbolkey == (0, 0, 1, 0, 0, 1):  # . or :
        # 마침표: 문장 끝/숫자 뒤, 쌍점: 시각·비율 등에서 앞뒤 숫자
        if next_cell is not None:
            key = tupleize(next_cell)
            # 쌍점 앞뒤가 숫자면 쌍점, 아니면 마침표
            if key in INV_NUMBER and prev_char.isdigit():
                return ":"
        # 기본값은 마침표
        return "."
    if symbolkey == (1, 0, 0, 0, 0, 1):  # - or ~
        # 하이픈은 단어/숫자 사이, 물결은 반복/범위/강조
        if prev_char and prev_char.isdigit() and next_cell is not None:
            key = tupleize(next_cell)
            if key in INV_NUMBER:
                return "-"
        return "~"
    if symbolkey == (0, 1, 0, 1, 0, 1):  # / or \
        # 수식·경로 등에서 앞뒤 맥락으로 구분
        # (여기서는 기본적으로 / 반환, 필요시 확장)
        return "/"
    return None

def text_to_braille(text: str, use_abbreviation: bool = True) -> List[List[int]]:
    braille_output: List[List[int]] = []
    i = 0
    mode = None
    while i < len(text):
        matched = False
        if use_abbreviation:
            for abbr in sorted(HANGUL_BRAILLE_ABBREVIATION.keys(), key=len, reverse=True):
                if text.startswith(abbr, i):
                    braille_output.extend(flatten_braille_cell(HANGUL_BRAILLE_ABBREVIATION[abbr]))
                    i += len(abbr)
                    matched = True
                    mode = None
                    break
            if matched:
                continue
        char = text[i]
        if char.isdigit():
            if mode != "number":
                braille_output.append(NUMBER_PREFIX)
                mode = "number"
            braille_output.extend(flatten_braille_cell(NUMBER_TO_BRAILLE.get(char, [0,0,0,0,0,0])))
            i += 1
            continue
        elif char.isalpha() and char.isascii():
            if mode != "alpha":
                braille_output.append(CAPITAL_PREFIX)
                mode = "alpha"
            braille_output.extend(flatten_braille_cell(ALPHABET_TO_BRAILLE.get(char.lower(), [0,0,0,0,0,0])))
            i += 1
            continue
        elif char in SYMBOL_TO_BRAILLE:
            braille_output.extend(flatten_braille_cell(SYMBOL_TO_BRAILLE[char]))
            mode = None
            i += 1
            continue
        elif hgtk.checker.is_hangul(char):
            try:
                cho, jung, jong = hgtk.letter.decompose(char)
                if cho in INITIAL_TO_BRAILLE:
                    braille_output.extend(flatten_braille_cell(INITIAL_TO_BRAILLE[cho]))
                if jung in MEDIAL_TO_BRAILLE:
                    braille_output.extend(flatten_braille_cell(MEDIAL_TO_BRAILLE[jung]))
                if jong and jong in FINAL_TO_BRAILLE:
                    braille_output.extend(flatten_braille_cell(FINAL_TO_BRAILLE[jong]))
                elif not jong:
                    braille_output.extend(flatten_braille_cell(FINAL_TO_BRAILLE['']))
                mode = None
            except Exception as e:
                print(f"[점자 변환 에러 - 한글 조합 실패]: {e}")
                braille_output.append([0,0,0,0,0,0])
            i += 1
            continue
        else:
            braille_output.append([0,0,0,0,0,0])
            mode = None
            i += 1
            continue
    return braille_output

def braille_to_text(braille: List[List[int]]) -> str:
    text_output = ""
    i = 0
    n = len(braille)
    mode = None
    while i < n:
        cell = braille[i]
        if cell == NUMBER_PREFIX:
            mode = "number"
            i += 1
            continue
        elif cell == CAPITAL_PREFIX:
            mode = "alpha"
            i += 1
            continue
        elif cell == SYMBOL_PREFIX:
            mode = "symbol"
            i += 1
            continue
        found = False
        if mode == "number":
            numkey = tupleize(cell)
            if numkey in INV_NUMBER:
                text_output += INV_NUMBER[numkey]
                i += 1
                continue
            else:
                mode = None
        if mode == "alpha":
            alphakey = tupleize(cell)
            if alphakey in INV_ALPHA:
                text_output += INV_ALPHA[alphakey]
                i += 1
                continue
            else:
                mode = None
        if mode == "symbol":
            symbolkey = tupleize(cell)
            if symbolkey in INV_SYMBOL:
                text_output += INV_SYMBOL[symbolkey]
                i += 1
                continue
            else:
                mode = None
        for length in [3, 2, 1]:
            if i + length <= n:
                key = tupleize(braille[i:i+length])
                if key in INV_ABBREV:
                    text_output += INV_ABBREV[key]
                    i += length
                    found = True
                    break
        if found:
            mode = None
            continue
        if i + 2 < n:
            ini_key = tupleize(braille[i])
            med_key = tupleize(braille[i+1])
            fin_key = tupleize(braille[i+2])
            if ini_key in INV_INITIAL and med_key in INV_MEDIAL and fin_key in INV_FINAL:
                try:
                    cho = INV_INITIAL[ini_key]
                    jung = INV_MEDIAL[med_key]
                    jong = INV_FINAL[fin_key]
                    text_output += hgtk.letter.compose(cho, jung, jong)
                    i += 3
                    mode = None
                    continue
                except Exception as e:
                    text_output += f"[오류: 한글 조합 실패({e})]"
                    i += 3
                    mode = None
                    continue
        if i + 1 < n:
            ini_key = tupleize(braille[i])
            med_key = tupleize(braille[i+1])
            if ini_key in INV_INITIAL and med_key in INV_MEDIAL:
                try:
                    cho = INV_INITIAL[ini_key]
                    jung = INV_MEDIAL[med_key]
                    text_output += hgtk.letter.compose(cho, jung)
                    i += 2
                    mode = None
                    continue
                except Exception as e:
                    text_output += f"[오류: 한글 조합 실패({e})]"
                    i += 2
                    mode = None
                    continue
        symbolkey = tupleize(cell)
        if symbolkey in AMBIGUOUS_SYMBOLS:
            prev_char = text_output[-1] if text_output else ""
            next_cell = braille[i+1] if (i+1) < n else None
            next_is_end = (i+1) >= n
            resolved = resolve_ambiguous_symbol(symbolkey, prev_char, next_cell, next_is_end)
            if resolved is not None:
                text_output += resolved
                i += 1
                mode = None
                continue
        alphakey = tupleize(cell)
        if alphakey in INV_ALPHA:
            text_output += INV_ALPHA[alphakey]
            i += 1
            mode = None
            continue
        symbolkey = tupleize(cell)
        if symbolkey in INV_SYMBOL:
            text_output += INV_SYMBOL[symbolkey]
            i += 1
            mode = None
            continue
        numkey = tupleize(cell)
        if numkey in INV_NUMBER:
            text_output += INV_NUMBER[numkey]
            i += 1
            mode = None
            continue
        text_output += "[알 수 없는 점자: {}]".format(''.join(str(dot) for dot in cell))
        i += 1
        mode = None
    return text_output