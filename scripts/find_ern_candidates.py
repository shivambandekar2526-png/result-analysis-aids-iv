import json, re

missing_ids = [101410023, 101410033, 101410034, 101410047, 101410048, 101410052, 101410053, 101410057, 101410061, 101410062, 101410067, 101410068, 101410071, 101410072, 101410078, 101410080, 101410088, 101410927, 101410949, 101410954]

for p in range(47):
    fn = f'data/cache/ocr_cache/page_{p:03d}.json'
    with open(fn, 'r', encoding='utf-8') as f:
        data = json.load(f)
    boxes = data['boxes']
    seat_boxes = [b for b in boxes if re.search(r'\b1014\d{5}\b', b['text'])]
    for sb in seat_boxes:
        sid = int(re.search(r'\b1014\d{5}\b', sb['text']).group(0))
        if sid in missing_ids:
            print(f"\nPage {p+1} (page_{p:03d}.json) - Student {sid} (y={sb['ymin']:.1f})")
            for b in boxes:
                if abs(b['ymin'] - sb['ymin']) < 60:
                    t = b['text']
                    if any(k in t.upper() for k in ['MU', 'TERNA', 'TRUST', 'COLLEGE', '(', '0341', '2024', '2025', '2023', '2022', '2021', '2020']):
                        print(f"   CANDIDATE: y=[{b['ymin']:.1f}-{b['ymax']:.1f}] x=[{b['xmin']:.1f}-{b['xmax']:.1f}] txt='{t}'")
