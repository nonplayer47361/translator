import cv2
import numpy as np
from typing import List, Tuple

def preprocess_braille_image(img_path: str, show_steps: bool = False, cell_size: int = 40, dot_radius: int = 7, margin: int = 20) -> Tuple[np.ndarray, List[List[Tuple[float, float]]]]:
    """
    점자 이미지에서 점(원의 중심좌표)들을 추출하고, 행/열로 정렬하여 반환
    :param img_path: 이미지 파일 경로
    :param show_steps: 각 단계 시각화 여부
    :param cell_size, dot_radius, margin: 생성 이미지와 동일하게 맞추면 추출 정확도 ↑
    :return: (원본이미지, [ [row1 dots], [row2 dots], ... ])
    """
    src = cv2.imread(img_path)
    if src is None:
        raise FileNotFoundError(f"이미지를 불러올 수 없습니다: {img_path}")
    if show_steps: cv2.imshow("0. Original", src)

    # 1. Grayscale
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    if show_steps: cv2.imshow("1. Grayscale", gray)

    # 2. Median Blur
    blur = cv2.medianBlur(gray, 3)
    if show_steps: cv2.imshow("2. Blur", blur)

    # 3. Otsu Threshold (Binary Inverse)
    _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    if show_steps: cv2.imshow("3. Binary", binary)

    # 4. Morphology - Opening
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    morph = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    if show_steps: cv2.imshow("4. Morphology", morph)

    # 5. Contour 찾기
    contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    centers = []
    visual = src.copy()
    max_area = max([cv2.contourArea(c) for c in contours]) if contours else 0
    min_area = max_area * 0.05

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area >= min_area:
            (x, y), radius = cv2.minEnclosingCircle(cnt)
            centers.append((x, y))
            cv2.circle(visual, (int(x), int(y)), 5, (0, 0, 255), -1)
    if show_steps: cv2.imshow("5. Contours + Centers", visual)

    # 6. 중심점 정렬 및 라벨링 (y기준 행 그룹핑, x기준 내부 정렬)
    centers.sort(key=lambda p: p[1])  # y로 정렬
    line_threshold = cell_size // 2  # 생성시 셀 크기의 절반 정도로 조정
    lines = []
    current_line = []
    for pt in centers:
        if not current_line or abs(pt[1] - current_line[-1][1]) < line_threshold:
            current_line.append(pt)
        else:
            lines.append(current_line)
            current_line = [pt]
    if current_line:
        lines.append(current_line)

    # 각 줄 내부도 x좌표 기준 정렬
    for line in lines:
        line.sort(key=lambda p: p[0])

    # 시각화 및 디버그
    line_mapped = src.copy()
    for i, line in enumerate(lines):
        for j, pt in enumerate(line):
            cv2.circle(line_mapped, (int(pt[0]), int(pt[1])), 5, (0, 255, 0), -1)
            cv2.putText(line_mapped, f"{i}-{j}", (int(pt[0])+5, int(pt[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
            print(f"[{i}-{j}] x: {int(pt[0])}, y: {int(pt[1])}")
    if show_steps: cv2.imshow("6. Pattern Mapping", line_mapped)

    if show_steps:
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return src, lines

def lines_to_braille_array(lines: List[List[Tuple[float, float]]], cell_shape=(2,3)) -> List[List[int]]:
    """
    점 중심 좌표의 2차원 배열을 점자 0/1배열로 변환 (기본 2x3)
    :param lines: [ [row1 dots], [row2 dots], ... ] (y/x 정렬된 좌표)
    :param cell_shape: 점자 한셀의 (가로 점 개수, 세로 점 개수)
    :return: 0/1 리스트 (셀 순서대로)
    """
    braille_cells = []
    if len(lines) < cell_shape[1]:
        print("경고: 점자 줄 수가 부족합니다.")
        return braille_cells

    num_cells = min(len(line) for line in lines)
    for col in range(num_cells):
        cell = []
        for row in range(cell_shape[1]):
            # 이 예시는 단순히 점이 있으면 1, 없으면 0로 처리
            cell.append(1)
        braille_cells.append(cell)
    return braille_cells

def image_to_braille_list(img_path: str, show_steps: bool = False, cell_size: int = 40, dot_radius: int = 7, margin: int = 20) -> List[List[int]]:
    _, lines = preprocess_braille_image(img_path, show_steps=show_steps, cell_size=cell_size, dot_radius=dot_radius, margin=margin)
    braille_cells = lines_to_braille_array(lines, cell_shape=(2, 3))
    return braille_cells