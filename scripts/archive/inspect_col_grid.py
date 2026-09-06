import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

# Let's inspect the exact x-coordinates of the headers:
# On page 3:
with open("ocr_cache/page_003.json", "r", encoding="utf-8") as f:
    data = json.load(f)

boxes = data["boxes"]
# Subject codes are in header:
sub_boxes = [b for b in boxes if re.match(r"^\d{7}$", b["text"]) and b["ymin"] < 800]
sub_boxes.sort(key=lambda b: (b["ymin"]//300, b["xmin"]))

print("Subject code header positions on Page 3:")
for b in sub_boxes:
    print(f"  y=[{b['ymin']:.1f}] x=[{b['xmin']:.1f}-{b['xmax']:.1f}] : {b['text']}")

# Let's also look at all boxes in student 1 (y in [500, 630]) and student 2 (y in [880, 1020])
print("\n--- Student 1 Marks (y in [510, 635]) sorted by y then x ---")
s1_boxes = [b for b in boxes if 510 <= b["ymin"] <= 635]
s1_boxes.sort(key=lambda b: (b["ymin"], b["xmin"]))
for b in s1_boxes:
    print(f"  y=[{b['ymin']:5.1f}-{b['ymax']:5.1f}] x=[{b['xmin']:5.1f}-{b['xmax']:5.1f}] : {b['text']}")
