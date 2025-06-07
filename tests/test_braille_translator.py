import sys
import os

# src 디렉터리를 모듈 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from braille_translator import text_to_braille, braille_to_text
from braille_utils import flatten_braille_cell, validate_braille_str

def test_hangul_round_trip():
    text = "안녕"
    braille = text_to_braille(text)
    recovered = braille_to_text(braille)
    assert recovered == text

def test_number_round_trip():
    text = "123"
    braille = text_to_braille(text)
    recovered = braille_to_text(braille)
    assert "123" in recovered

def test_english_round_trip():
    text = "Hello"
    braille = text_to_braille(text)
    recovered = braille_to_text(braille)
    assert recovered.lower() == text.lower()

def test_symbol_round_trip():
    text = "!@#"
    braille = text_to_braille(text)
    recovered = braille_to_text(braille)
    for c in "!@#":
        assert c in recovered

def test_abbreviation():
    text = "그래서"
    braille = text_to_braille(text, use_abbreviation=True)
    # 약자가 적용되어 보통 더 짧아집니다.
    assert len(braille) < len(text) * 3  # 한글 점자 2~3셀 기준
    recovered = braille_to_text(braille)
    assert "그래서" in recovered

def test_invalid_braille_input_length():
    assert not validate_braille_str("11011 001100")  # 5자리 셀

def test_invalid_braille_input_content():
    assert not validate_braille_str("110110 002100") # 0/1 이외 값

def test_flatten_braille_cell_list_and_listoflists():
    cell1 = [1,0,0,1,0,1]
    cell2 = [[1,0,0,1,0,1],[0,1,1,0,0,1]]
    assert flatten_braille_cell(cell1) == [[1,0,0,1,0,1]]
    assert flatten_braille_cell(cell2) == [[1,0,0,1,0,1],[0,1,1,0,0,1]]

def test_mixed_text():
    text = "한글ABC123!@#테스트"
    braille = text_to_braille(text)
    recovered = braille_to_text(braille)
    # 한글/영문/숫자/특수문자 roundtrip이 제대로 되는지 확인
    assert recovered.replace(" ", "").lower() == text.replace(" ", "").lower()