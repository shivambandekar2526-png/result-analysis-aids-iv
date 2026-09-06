import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

from test_master_pipeline import SUBJECTS

targets = [
    (5, "101410028"),
    (12, "101410042"),
    (13, "101410043"),
    (32, "101410081"),
    (34, "101410085"),
    (36, "101410926"),
    (37, "101410928")
]

for p, seat in targets:
    with open(f"ocr_cache/page_{p:03d}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    boxes = data["boxes"]
    sb = [b for b in boxes if seat in b["text"]][0]
    s_y = sb["ymin"]
    print(f"\n==================== Page {p} Seat {seat} (s_y={s_y:.1f}) ====================")
    m_boxes = [b for b in boxes if 0 < (b["ymin"] - s_y) <= 170]
    m_boxes.sort(key=lambda b: (round(b["ymin"]/12)*12, b["xmin"]))
    for b in m_boxes:
        print(f"  y={b['ymin']:5.1f} x={b['xmin']:5.1f} : '{b['text']}'")
