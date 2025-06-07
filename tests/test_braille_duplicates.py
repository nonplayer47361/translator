import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from collections import defaultdict
from braille_table import (
    INITIAL_TO_BRAILLE, MEDIAL_TO_BRAILLE, FINAL_TO_BRAILLE,
    NUMBER_TO_BRAILLE, ALPHABET_TO_BRAILLE, SYMBOL_TO_BRAILLE,
    HANGUL_BRAILLE_ABBREVIATION,
    NUMBER_PREFIX, CAPITAL_PREFIX
)
from braille_utils import flatten_braille_cell

def get_prefix_group(table_name):
    if table_name == "NUMBER_TO_BRAILLE":
        return "number"
    elif table_name == "ALPHABET_TO_BRAILLE":
        return "alpha"
    elif table_name == "SYMBOL_TO_BRAILLE":
        return "symbol"
    else:
        return "hangul"

def test_no_confusing_duplicates():
    all_tables = {
        "INITIAL_TO_BRAILLE": INITIAL_TO_BRAILLE,
        "MEDIAL_TO_BRAILLE": MEDIAL_TO_BRAILLE,
        "FINAL_TO_BRAILLE": FINAL_TO_BRAILLE,
        "NUMBER_TO_BRAILLE": NUMBER_TO_BRAILLE,
        "ALPHABET_TO_BRAILLE": ALPHABET_TO_BRAILLE,
        "SYMBOL_TO_BRAILLE": SYMBOL_TO_BRAILLE,
        "HANGUL_BRAILLE_ABBREVIATION": HANGUL_BRAILLE_ABBREVIATION,
    }

    # (group, length, cell_tuple) -> [(table, key, value), ...]
    group_cell_map = defaultdict(list)
    for table_name, table in all_tables.items():
        group = get_prefix_group(table_name)
        for k, v in table.items():
            cells = flatten_braille_cell(v)
            # 길이 1 셀만 등록(진짜 혼동 가능성 있는 경우만)
            if len(cells) == 1:
                group_cell_map[(group, 1, tuple(cells[0]))].append((table_name, k, v))
            # 길이 2 이상 점자(약자, 겹자음 등)는 한 셀 점자와 혼동 불가! (중복 체크 X)
                # 만약 연속 셀 점자끼리의 완전한 중복(같은 그룹, 같은 길이, 값까지 같음)이 있으면 아래에서 추가 검사

    # 혼동 가능한 중복 찾기 (한 셀 점자만, 같은 테이블 내에서만 중복 체크)
    conflicts = []
    for (group, length, cell), keylist in group_cell_map.items():
        # 테이블(매핑 종류)이 동일한 것만 중복으로 간주
        table_to_keys = defaultdict(list)
        for table_name, k, v in keylist:
            table_to_keys[table_name].append((k, v))
        for table_name, kvs in table_to_keys.items():
            if len(kvs) > 1:
                # 같은 테이블 내에서만 중복 보고
                conflicts.append((group, cell, [(table_name, k, v) for k, v in kvs]))

    # 2개 이상의 셀(연속 점자)은 서로 완전히 같을 때만 별도 경고 (테이블 동일한 경우만)
    multi_cell_map = defaultdict(list)
    for table_name, table in all_tables.items():
        group = get_prefix_group(table_name)
        for k, v in table.items():
            cells = flatten_braille_cell(v)
            if len(cells) > 1:
                multi_cell_map[(group, len(cells), tuple(tuple(cell) for cell in cells), table_name)].append((k, v))
    for (group, length, cells, table_name), keylist in multi_cell_map.items():
        if len(keylist) > 1:
            conflicts.append((f"{group}-multi({length})", cells, [(table_name, k, v) for k, v in keylist]))

    report_fname = "braille_duplicates_report_strict.txt"
    with open(report_fname, "w", encoding="utf-8") as f:
        if not conflicts:
            f.write("구분점자 기준 혼동 가능한 중복 점자 셀 없음\n")
        else:
            f.write("구분점자 기준 혼동 가능한 중복 점자 셀:\n")
            for group, cell, keylist in conflicts:
                f.write(f"[{group}] {cell} -> {[(k, v) for k, v, _ in keylist]}\n")

    print(f"중복 점자 셀 검사 결과: {report_fname}")
    assert not conflicts, (
        f"구분점자 기준 혼동 가능한 점자 셀 충돌 있음! {report_fname} 파일을 확인하세요."
    )

if __name__ == "__main__":
    test_no_confusing_duplicates()