import cv2
import numpy as np
import os
from typing import List, Optional
from .braille_utils import safe_filename

def braille_to_image(
    braille_list: List[List[int]], 
    cell_size: int = 40, 
    dot_radius: int = 7, 
    margin: int = 20,
    save_path: Optional[str] = None
) -> str:
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
                cx = x0 + dx * (cell_size // 2) + cell_size // 4
                cy = y0 + dy * (cell_size // 3) + cell_size // 6
                cv2.circle(img, (cx, cy), dot_radius, (0,0,0), -1)
    if save_path is None:
        filename = "dot.png"
    else:
        filename = save_path
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    cv2.imwrite(filename, img)
    return filename

def image_to_braille_list(
    img_path: str, 
    cell_size: int = 40, 
    margin: int = 20,
    patch: int = 1
) -> List[List[int]]:
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(img_path)
    cols = (img.shape[1] - 2 * margin) // cell_size
    braille_list = []
    dot_pos = [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2)]
    for idx in range(cols):
        x0 = margin + idx * cell_size
        y0 = margin
        cell = []
        for (dx, dy) in dot_pos:
            cx = x0 + dx * (cell_size // 2) + cell_size // 4
            cy = y0 + dy * (cell_size // 3) + cell_size // 6
            px = img[max(0, cy-patch):cy+patch+1, max(0, cx-patch):cx+patch+1]
            if px.mean() < 128:
                cell.append(1)
            else:
                cell.append(0)
        braille_list.append(cell)
    return braille_list

def save_braille_sample(
    braille_list: List[List[int]],
    text: str,
    data_dir: str = "data",
    cell_size: int = 40,
    dot_radius: int = 7,
    margin: int = 20
) -> str:
    os.makedirs(data_dir, exist_ok=True)
    existing = [int(name) for name in os.listdir(data_dir) if name.isdigit()]
    next_idx = max(existing, default=0) + 1
    sample_dir = os.path.join(data_dir, str(next_idx))
    os.makedirs(sample_dir, exist_ok=False)

    img_path = os.path.join(sample_dir, "dot.png")
    txt_path = os.path.join(sample_dir, f"{safe_filename(text)}.txt")

    braille_to_image(
        braille_list=braille_list,
        cell_size=cell_size,
        dot_radius=dot_radius,
        margin=margin,
        save_path=img_path
    )
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)

    return sample_dir