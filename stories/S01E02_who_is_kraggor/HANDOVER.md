# HANDOVER — S01E02 "Who Is Kraggor?" (story3d) — status 2026-10-06

> Read this first in a new session. Then: `AGENTS.md`, `generators/story3d/SOP_STORY3D.md`,
> `generators/story3d/STYLE_CONTRACT.json`, `stories/S01E02_who_is_kraggor/script.md`.
> Full chat history (Indonesian): `ipandu-video/claude/agent_claude.md`. Keep appending to it after every exchange.

## Decisions in force (owner)
- Long story episodes from Ep.2 = **story3d (option C)**: Godot 3D world + original story25d characters, rendered on Modal.
  Shorts stay on the 2.5D engines. Ep.1 stays as aired (never re-render or "fix" it).
- Script `script.md` v1 approved implicitly ("gas"). Outline approved.
- Every owner note → a numbered rule in `STYLE_CONTRACT.json` (+ `QA_DEFECT_TRACKER.md` row), never a one-off fix.
  Owner hates repeated fix loops: batch research + fixes, self-review frames/audio/joins BEFORE delivering.
- Film language: no talking-heads close-up ping-pong; group/two shots; J-cuts; ≤2 marked close-ups; no wide→close jumps
  (push in instead); joins across time = fade out 1.0 + black hold 0.5 (room tone) + fade in 1.3 (dracin style).
- Sound: no empty silence (A01), no hiss (A02), effects phone-audible (A03), no noise-like crowd SFX (A07; cheer/laugh
  banned → `honk_cheer`, only 2 horn types A08), Kraggor = roar/motif, never noise.
- Continuity K01: the Ep.1 wall photo (Grandpa at the beach) never contains Kraggor. The torn photo is a NEW album photo
  "Mountain Road" (tear seed 7); the scene 13 piece = `photo_piece` with the same seed (edges + tail match).
- Ad-break idea (dracin-style mid-roll gaps after scenes 3/7/10) proposed; owner did not confirm yet.

## Done (Drive: ipandu-video/story3d/S01E02_who_is_kraggor/)
| Scene | State |
|---|---|
| 1 Cold open "Footprints" (town night) | approved ("perfect"), tension bed added before the footprints |
| 2 Town Panic (town day) | approved after coverage/staging/honk fixes |
| 3 Town Meeting (arena sunset) | approved after Siren-floating + zoom-in fixes (stage ramps, G04) |
| 4 Grandpa's Old Box (garage night) | delivered: album + torn Mountain Road photo; awaiting owner review |
| episode_01-02-03-04.mp4 | assembled with smooth joins |

## In progress (not committed yet when this was written)
Scenes 5-8 in one batch to save tokens:
- **Branch `wip-scenes-5-8` (pushed to GitHub; main does NOT have it)**: `generators/story3d/project/story3d.gd` with NEW locations written but UNTESTED — `forest` (storm), `mountain` (night road,
  rockslide prop), `cave` (crystals, `treasure`, `sign`, `key` props, moonbeam), `mountains: true` backdrop, `rain: true`
  + `lightning: [t...]`. Test with a short Godot render (modal_godot --count 20) BEFORE merging the branch into main (a GDScript parse error breaks EVERY scene): `git checkout wip-scenes-5-8` / merge only after it passes.
- Still to do: little Kraggor as a world-anchored prop (real drawing, small; modes scared/munch/smile/sleep), sepia grade in
  compose (scene `grade: "sepia"`, disable story25d `sepia()` in the exporter to avoid double), `storm` ambience + tonal
  thunder + `rockslide` SFX (phone-audible, not noise), scene JSONs 5-8, validator PROPS for the new props, render all 4 in
  one run, review sheets, fix once, upload, assemble 1-8.
- Young Grandpa in the flashback: `vk icecream`, color [0.93,0.86,0.7], accent [0.62,0.42,0.25], mustache false (Ep.1 used
  mustache true for the older Grandpa).

## How to run (VM 192.168.99.3, SSH -p 22022 root@2.28.128.77, key from the owner)
```
cd /root/video-engine && bash git_sync.sh pull
venv/bin/python generators/story3d/validate_scene.py --episode S01E02_who_is_kraggor --scenes 5,6,7,8
venv/bin/python generators/story3d/produce_story3d.py --episode S01E02_who_is_kraggor --scenes 5,6,7,8 [--upload]
venv-modal/bin/modal run generators/story3d/modal_story3d.py::assemble --episode S01E02_who_is_kraggor --order 1,2,3,4,5,6,7,8 --out work/story3d/S01E02_who_is_kraggor
bash generators/story3d/tools/stop_story3d.sh      # stop renders safely (never pgrep a pattern inside the ssh command)
```
PC repo: `F:\drive-aliwardana\My Drive\me\ai-develop\ipandu-video\megawheel-video-engine` (git via
`/c/Program Files/Git/cmd/git.exe`, author kokoali-bima <mu.aliwardana@gmail.com>, push = fetch + merge origin/main
(Drive touches file stats: `git checkout -- modal_usage.json` before merging), never rebase (it sticks here).
After PC push: on the VM `bash git_sync.sh push "records"` if dirty, then `bash git_sync.sh pull`.

## Known pitfalls (already fixed — do not reintroduce)
- Modal client can hang after "Created objects" → produce_story3d has a 6-min watchdog + unbuffered log.
- New drawing code must pass the SMOKE preflight (story25d `SMOKE`) — produce runs it automatically on the VM.
- Narrator voice needs `branding/voice/announcer_ref.wav` → the whole `branding/voice` is mounted on Modal.
- `se.draw_text(..., stroke=None)` crashes; pass a colour.
- Returned values from Modal functions must be plain Python types (no numpy) — the local modal env has no numpy.
- Linter body lengths = exact `BODY` table (not estimates); moves are eased (x1.5 time).
- Budget: Modal $29/month (≈ $8.4 used by 2026-10-06); ±$0.05 per scene render.
