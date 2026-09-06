import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

with open("ocr_cache/page_005.json", "r", encoding="utf-8") as f:
    data = json.load(f)
boxes = data["boxes"]
sb = [b for b in boxes if "101410027" in b["text"]][0]
s_y = sb["ymin"]
print(f"Seat 101410027 s_y={s_y}")
m_boxes = [b for b in boxes if 0 <= (b["ymin"] - s_y) <= 170]
m_boxes.sort(key=lambda b: (b["ymin"], b["xmin"]))
for b in m_boxes:
    print(f"  dy={b['ymin']-s_y:5.1f} x=[{b['xmin']:5.1f}-{b['xmax']:5.1f}] text='{b['text']}'")
