import json, re

missing_ids = [101410023, 101410033, 101410034, 101410047, 101410048, 101410052, 101410053, 101410057, 101410061, 101410062, 101410067, 101410068, 101410071, 101410072, 101410078, 101410080, 101410088, 101410927, 101410949, 101410954]

for p in range(47):
    fn = f'data/cache/ocr_cache/page_{p:03d}.json'
    with open(fn, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for b in data['boxes']:
        txt = b['text']
        for sid in missing_ids:
            if str(sid) in txt:
                print(f"\n==========================================")
                print(f"Page {p+1} (page_{p:03d}.json): Student {sid}")
                sy = (b['ymin'] + b['ymax']) / 2
                # sort boxes near sy by xmin
                nearby = []
                for b2 in data['boxes']:
                    by = (b2['ymin'] + b2['ymax']) / 2
                    if abs(by - sy) < 40:
                        nearby.append(b2)
                nearby.sort(key=lambda x: (x['ymin'], x['xmin']))
                for b2 in nearby:
                    print(f"   y=[{b2['ymin']:.1f}-{b2['ymax']:.1f}] x=[{b2['xmin']:.1f}-{b2['xmax']:.1f}]: {b2['text']}")
