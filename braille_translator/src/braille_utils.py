import re
from typing import List, Union

def flatten_braille_cell(cell: Union[list, List[list]]) -> List[list]:
    """복합셀(2셀 이상)을 평탄화하여 1차원 셀 리스트로 변환"""
    if isinstance(cell[0], list):
        return cell
    return [cell]

def safe_filename(text: str) -> str:
    """파일명에 사용할 수 없는 문자만 남긴다(한글,영문,숫자,언더스코어)"""
    return re.sub(r'[^a-zA-Z0-9가-힣_]', '_', text)

def dots_to_decimal(dots):
    """
    [점1, 점2, 점3, 점4, 점5, 점6] 배열을 10진수(0~63)로 변환
    점 번호: 1 4
            2 5
            3 6
    dots: [점1, 점2, 점3, 점4, 점5, 점6]
    """
    return sum((1 << i) if dot else 0 for i, dot in enumerate(dots))

def decimal_to_dots(num):
    """
    10진수(0~63)를 [점1, 점2, 점3, 점4, 점5, 점6] 배열로 변환
    """
    return [(num >> i) & 1 for i in range(6)]

def dots_to_unicode(dots):
    """
    [점1, 점2, 점3, 점4, 점5, 점6] 배열을 점자 유니코드 문자로 변환
    """
    return chr(0x2800 + dots_to_decimal(dots))

def unicode_to_dots(uchar):
    """
    점자 유니코드 문자(⠁ 등)를 [점1, 점2, 점3, 점4, 점5, 점6] 배열로 변환
    """
    num = ord(uchar) - 0x2800
    return decimal_to_dots(num)

def make_braille_unicode_table(table):
    """
    {문자: [점1, 점2, 점3, 점4, 점5, 점6]} 형식의 테이블을
    {문자: 점자유니코드}로 변환
    """
    return {k: dots_to_unicode(v) if isinstance(v[0], int) else [dots_to_unicode(cell) for cell in v] for k, v in table.items()}

# 예시 사용
if __name__ == "__main__":
    # 예시: 초성 'ㄱ'의 점자 배열
    dots = [0,0,0,1,0,0]  # 4번 점만 볼록
    print("10진수:", dots_to_decimal(dots))      # 4
    print("유니코드:", dots_to_unicode(dots))     # ⠄

    # 테이블 변환 예시
    INITIAL_TO_BRAILLE = {
        'ㄱ': [0,0,0,1,0,0],
        'ㄴ': [0,1,0,0,0,0],
        'ㄷ': [0,0,0,1,1,0],
    }
    unicode_table = make_braille_unicode_table(INITIAL_TO_BRAILLE)
    print(unicode_table)  # {'ㄱ': '⠄', 'ㄴ': '⠂', 'ㄷ': '⠔'}