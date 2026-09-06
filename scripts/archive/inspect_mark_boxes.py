import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

for p in [2, 3, 12, 14]:
    with open(f"ocr_cache/page_{p:03d}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    boxes = data["boxes"]
    seat_boxes = [b for b in boxes if re.search(r"\b1014\d{5}\b", b["text"])]
    seat_boxes.sort(key=lambda b: b["ymin"])
    
    for s_idx, sb in enumerate(seat_boxes):
        seat = re.search(r"\b1014\d{5}\b", sb["text"]).group(0)
        s_y = sb["ymin"]
        print(f"\n==================== Page {p} Seat {seat} (s_y={s_y:.1f}) ====================")
        m_boxes = [b for b in boxes if 0 < (b["ymin"] - s_y) <= 160]
        m_boxes.sort(key=lambda b: (round(b["ymin"]/15)*15, b["xmin"]))
        
        # Print grouped by approximate line
        current_line_y = None
        line_items = []
        for b in m_boxes:
            grid_y = round((b["ymin"] - s_y) / 10) * 10
            if current_line_y is None or abs(grid_y - current_line_y) > 8:
                if line_items:
                    print(f"  dy~{current_line_y:3d} : " + " | ".join(line_items))
                current_line_y = grid_y
                line_items = []
            line_items.append(f"x={b['xmin']:.0f}:{b['text']}")
        if line_items:
            print(f"  dy~{current_line_y:3d} : " + " | ".join(line_items))
