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


def register(series, story_ep, video, title, desc, extra, tags=None, engine="story25d"):
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
                    engine=engine, title_base=title, title=title, description=desc, tags=tags or TAGS,
                    video_path=out, assets="100% procedurally generated (cairo 2.5D render + synthesized audio), "
                    "voices Chatterbox TTS (open source) synthetic, theme songs ACE-Step (Apache-2.0)", **extra)
    with open(f"{folder}/{name}.json", "w") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
    with open(f"{folder}/{name}_audit.md", "w") as fh:
        fh.write(f"# {name}\n\nStory episode {story_ep} ({series}). Audit: generators/story/audit_story.py (0 ERROR "
                 f"before render). Review drafts on Drive review/story_S01E{story_ep:02d}/.\n")
    registry.upsert(dict(video_id=name, series=series, engine_version=engine, seed=story_ep, created=date,
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
    ap.add_argument("--meta", help="story3d episodes: stories/<ep>/publish.json (title, description with {chapters}, tags, "
                                   "language) - needs --video and --chapters")
    ap.add_argument("--video", help="the final episode mp4 (story3d)")
    ap.add_argument("--chapters", help="the assembler's _chapters.txt (story3d)")
    ap.add_argument("--only-trailer", action="store_true", help="register just the trailer (the episode is already registered)")
    ap.add_argument("--trailer-video", help="the trailer Short mp4 (story3d); registered as story15_trailer, pending")
    ap.add_argument("--thumb", help="thumbnail jpg/png (< 2 MB), copied next to the video and set on upload")
    a = ap.parse_args()
    if a.meta:                                                    # story3d (S01E02+): everything from publish.json
        pub = json.load(open(os.path.join(BASE, a.meta) if not os.path.isabs(a.meta) else a.meta, encoding="utf-8"))
        name = None
        if not a.only_trailer:
            chapters = open(a.chapters, encoding="utf-8").read().strip()
            extra = {"language": pub.get("language", "en-US")}
            name = register("story15", a.story_ep, a.video, pub["title"], pub["description"].replace("{chapters}", chapters),
                            extra, tags=pub["tags"], engine="story3d")
        if a.trailer_video:                                           # the trailer Short: PENDING too (own fixed time)
            tr = pub["trailer"]
            register("story15_trailer", a.story_ep, a.trailer_video, tr["title"], tr["description"],
                     {"publish_at_et": a.trailer_at or tr["publish_at_et"], "language": pub.get("language", "en-US")},
                     tags=pub["tags"], engine="story3d")
        if a.thumb and name:
            dst = f"{BASE}/renders/megawheel_arena/pending/{name}/{name}_thumb{os.path.splitext(a.thumb)[1]}"
            shutil.copy2(a.thumb, dst)
            mp = f"{BASE}/renders/megawheel_arena/pending/{name}/{name}.json"
            m = json.load(open(mp, encoding="utf-8"))
            m["thumbnail"] = dst
            json.dump(m, open(mp, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
            print(f"[story] thumbnail -> {dst}")
        return
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
