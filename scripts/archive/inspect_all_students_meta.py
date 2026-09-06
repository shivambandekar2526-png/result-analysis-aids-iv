import json, re, glob, os, sys
sys.stdout.reconfigure(encoding="utf-8")

students_meta = []

for p in range(2, 47):
    fpath = f"ocr_cache/page_{p:03d}.json"
    if not os.path.exists(fpath):
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)
    boxes = data["boxes"]
    
    # Let's find seat numbers
    # A seat number is a 9 digit number starting with 1014
    for b in boxes:
        m = re.findall(r"\b1014\d{5}\b", b["text"])
        for seat in m:
            # Find name, status, gender, ERN around this y-coordinate
            y = b["ymin"]
            # Look for row of metadata: y within [y-15, y+15]
            row_boxes = [b2 for b2 in boxes if abs(b2["ymin"] - y) < 20]
            row_boxes.sort(key=lambda x: x["xmin"])
            
            # Look for ERN
            ern = ""
            for rb in row_boxes:
                ern_m = re.search(r"\(?(MU\d+)\)?", rb["text"])
                if ern_m:
                    ern = ern_m.group(1)
            if not ern:
                # search in a wider range y-30 to y+30
                near_boxes = [b2 for b2 in boxes if abs(b2["ymin"] - y) < 40]
                for nb in near_boxes:
                    ern_m = re.search(r"\(?(MU\d+)\)?", nb["text"])
                    if ern_m:
                        ern = ern_m.group(1)

            # Look for gender
            gender = ""
            for rb in row_boxes:
                if "FEMALE" in rb["text"].upper():
                    gender = "FEMALE"
                elif "MALE" in rb["text"].upper():
                    gender = "MALE"

            # Look for status
            status = ""
            for rb in row_boxes:
                if "Regular" in rb["text"]:
                    status = "Regular"
                elif "Repeater" in rb["text"]:
                    status = "Repeater"

            # Look for name: between seat and gender/status
            # usually x in [200, 550]
            name_parts = []
            for rb in row_boxes:
                if 180 <= rb["xmin"] <= 550 and not re.search(r"\b1014\d{5}\b", rb["text"]):
                    name_parts.append(rb["text"])
            name = " ".join(name_parts)

            students_meta.append({
                "page": p,
                "y": y,
                "seat_no": seat,
                "name": name,
                "gender": gender,
                "status": status,
                "ern": ern
            })

print(f"Total students metadata detected: {len(students_meta)}")
for i, s in enumerate(students_meta):
    print(f"{i+1:2d}. Page {s['page']:2d} y={s['y']:5.1f} | Seat: {s['seat_no']} | Name: {s['name']:30s} | Gender: {s['gender']:6s} | Status: {s['status']:7s} | ERN: {s['ern']}")
