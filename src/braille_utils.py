import re
from typing import List, Union, Tuple

def flatten_braille_cell(cell: Union[List[int], List[List[int]]]) -> List[List[int]]:
    """
    점자셀을 항상 2차원 리스트로 평탄화.
    - [0,1,0,1,0,0] -> [[0,1,0,1,0,0]]
    - [[0,1,0,1,0,0], ...] -> 그대로
    """
    if isinstance(cell, list):
        if len(cell) > 0 and isinstance(cell[0], list):
            return [list(row) for row in cell]
        else:
            return [list(cell)]
    raise ValueError("cell must be a list of int or list of list of int")

def tupleize(cell: Union[List[int], List[List[int]]]) -> Union[Tuple[int, ...], Tuple[Tuple[int, ...], ...]]:
    """
    점자 배열을 dict key로 쓰기 위한 튜플화
    """
    if isinstance(cell, list):
        if len(cell) > 0 and isinstance(cell[0], list):
            return tuple(tuple(c) for c in cell)
        else:
            return tuple(cell)
    raise ValueError("cell must be a list of int or list of list of int")

def safe_filename(text: str) -> str:
    """
    파일명에 쓸 수 없는 문자(\\ / : * ? " < > | 공백)를 언더바(_)로 변환
    """
    return re.sub(r'[\\/:*?"<>| ]+', '_', text)

def validate_braille_str(s: str) -> bool:
    """
    점자(01문자열) 입력이 올바른지 검증 (6자리 0/1, 공백구분)
    """
    cells = s.strip().split()
    if not cells:
        return False
    for cell in cells:
        if len(cell) != 6 or not all(c in "01" for c in cell):
            return False
    return True