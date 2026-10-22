"""Independent pixel comparison of fixed S021 before/after lighting fixtures.

Regions are interior body paint, not HUD/background. This scoped regression probe
is not an absolute quality classifier for arbitrary scenes.
"""
import hashlib
import json
import sys
from pathlib import Path
from PIL import Image, ImageStat

root = Path(sys.argv[1])
regions = {'siren': (175, 1165, 235, 1190), 'sprinkles': (365, 1145, 430, 1190),
           'buster': (120, 1210, 195, 1240)}
checks = []
for name, box in regions.items():
    before = Image.open(root / f'before_{name}.png').convert('RGB')
    after = Image.open(root / f'after_{name}.png').convert('RGB')
    b = ImageStat.Stat(before.crop(box).convert('L')).mean[0]
    a = ImageStat.Stat(after.crop(box).convert('L')).mean[0]
    sky_same = before.crop((0, 0, 1080, 100)).tobytes() == after.crop((0, 0, 1080, 100)).tobytes()
    highlights = after.crop(box).convert('L').histogram()[250:]
    clipped = sum(highlights) / ((box[2]-box[0])*(box[3]-box[1]))
    checks.append(dict(cast=name, region=list(box), before_mean=round(b, 2), after_mean=round(a, 2),
                       ratio=round(a/b, 3), sky_pixels_identical=sky_same, bright_pixel_fraction=clipped,
                       passed=a > b * 1.2 and sky_same and clipped < 0.01))
day_before = hashlib.sha256((root / 'before_day.png').read_bytes()).hexdigest()
day_after = hashlib.sha256((root / 'after_day.png').read_bytes()).hexdigest()
report = dict(passed=all(c['passed'] for c in checks) and day_before == day_after,
              scope='S021 fixed body-paint regions, first-frame fixtures; S013 daytime first frame',
              checks=checks, day_pixels_identical=day_before == day_after, day_sha256=day_after)
(root / 'NIGHT_READABILITY_QA.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
assert report['passed'], 'Night pixel regression failed'
