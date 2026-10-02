"""Register a long story episode (series story15) and/or its trailer Short (story15_trailer) as PENDING videos,
so the normal flow applies: user approval -> episodes.py approve -> publish_queue plan/upload.

  venv/bin/python generators/story/register_story.py --episode S01E01_sprinkles_first_race --story-ep 1 \
      --trailer-at 2026-10-03T17:00

Writes renders/megawheel_arena/pending/<date>_story15_e01/ (+ _trailer) with the mp4 and a manifest
(title, description with YouTube chapters + credit, tags). Never uploads anything.
"""
import argparse
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "physics_2d"))
import registry  # noqa: E402

BASE = "/root/video-engine"
TAGS = ["MegaWheel Arena", "cartoon cars", "animated story", "car cartoon", "ice cream truck", "monster truck",
        "kaiju", "racing cartoon", "Sprinkles", "Kraggor", "animation"]


def meta_long(ep_dir, story_ep, chapters):
    title = f"Sprinkles' First Race 🍦🏁 | MegaWheel Arena Story Ep. {story_ep}"
    desc = ("Everyone said she was too slow, too heavy... too sweet. One month before the MegaWheel Grand Race, "
            "Sprinkles the ice cream truck decides to race anyway: four weeks of training, a promise to her Grandpa, "
            "and a race day nobody will ever forget... because KRAGGOR is coming. 🦖\n\n"
            "Who is the real champion? Watch till the end! 🏆\n\n"
            "⏱️ Chapters\n" + chapters.strip() + "\n\n"
            "🔔 Subscribe to MegaWheel Arena: a new story episode every Sunday, new car races every day.\n\n"
            "#MegaWheelArena #CartoonCars #AnimatedStory")
    return title, desc


def meta_trailer(story_ep):
    title = f"Sprinkles' First Race 🍦 Full Episode This Sunday!"
    desc = ("An ice cream truck in the Grand Race? Everyone laughed... until KRAGGOR appeared. 🦖\n"
            f"The full story episode premieres this Sunday on MegaWheel Arena. Turn on notifications! 🔔\n\n"
            "#MegaWheelArena #CartoonCars")
    return title, desc


def register(series, story_ep, video, title, desc, extra):
    date = time.strftime("%Y-%m-%d")
    name = f"{date}_{series}_e{story_ep:02d}"
    folder_rel = f"renders/megawheel_arena/pending/{name}"
    folder = f"{BASE}/{folder_rel}"
    if registry.get(name):
        raise SystemExit(f"[story] STOP: {name} sudah terdaftar ({registry.get(name)['status']})")
    os.makedirs(folder, exist_ok=True)
    out = f"{folder}/{name}.mp4"
    shutil.copy2(video, out)
    manifest = dict(video_id=name, status="RENDERED_PENDING_APPROVAL", series=series, story_episode=story_ep,
                    engine="story25d", title_base=title, title=title, description=desc, tags=TAGS,
                    video_path=out, assets="100% procedurally generated (cairo 2.5D render + synthesized audio), "
                    "voices Chatterbox TTS (open source) synthetic, theme songs ACE-Step (Apache-2.0)", **extra)
    with open(f"{folder}/{name}.json", "w") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
    with open(f"{folder}/{name}_audit.md", "w") as fh:
        fh.write(f"# {name}\n\nStory episode {story_ep} ({series}). Audit: generators/story/audit_story.py (0 ERROR "
                 f"before render). Review drafts on Drive review/story_S01E{story_ep:02d}/.\n")
    registry.upsert(dict(video_id=name, series=series, engine_version="story25d", seed=story_ep, created=date,
                         render_date=date, vehicles=["icecream", "sports", "bus", "monster", "police", "taxi", "f1"],
                         track_id=f"story_e{story_ep:02d}", outcomes=[series], duration=None,
                         status="RENDERED_PENDING_APPROVAL", folder=folder_rel, audit=f"{folder_rel}/{name}_audit.md",
                         episode=None, season=None, upload_date=None, youtube_url=None, story_episode=story_ep,
                         **{k: v for k, v in extra.items() if k == "publish_at_et"}))
    print(f"[story] PENDING {name}: {title}")
    return name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", required=True)
    ap.add_argument("--story-ep", type=int, required=True)
    ap.add_argument("--trailer-at", help="ET, e.g. 2026-10-03T17:00 (extra fixed slot)")
    a = ap.parse_args()
    wd = f"{BASE}/work/story/{a.episode}"
    with open(f"{wd}/{a.episode}_h_chapters.txt") as fh:
        chapters = fh.read()
    t, d = meta_long(wd, a.story_ep, chapters)
    register("story15", a.story_ep, f"{wd}/{a.episode}_h.mp4", t, d, {})
    if a.trailer_at:
        t, d = meta_trailer(a.story_ep)
        register("story15_trailer", a.story_ep, f"{wd}/scene_90_v.mp4", t, d, {"publish_at_et": a.trailer_at})


if __name__ == "__main__":
    main()
