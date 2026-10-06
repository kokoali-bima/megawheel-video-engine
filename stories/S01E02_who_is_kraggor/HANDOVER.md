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
- Ads: none for now (owner 2026-10-06). But every scene join has a dracin-style episode card (J03): fade out 1.0 + black hold 1.8 with "PART N" + chapter title + soft bell + fade in 1.2 (contract `joins.time_jump`). That card is also where mid-roll ads can go later.

## Done (Drive: ipandu-video/story3d/S01E02_who_is_kraggor/)
| Scene | State |
|---|---|
| 1-3 | approved |
| 4 Grandpa's Old Box | delivered, awaiting owner review |
| 5 Flashback "The Little Monster" (sepia storm, little Kraggor) | delivered 2026-10-06, QA WARN (flash jumps = lightning, dark night luma, 2 light masking) |
| 6 The Plan (town + giant mountains) | delivered, QA WARN (lightning jump only) |
| 7 Into the Mountains (mud, Rocky, rockslide) | delivered, QA WARN (night contrast) |
| 8 The Cave (crystals, treasure, Grandpa's sign, key, eyes) | delivered, QA WARN (dark cave) |
| episode_01..08.mp4 | assembled, all 7 joins pass (cub fade-out curve) |

## Engine added for 5-8 (all on main, tested)
- Godot locations `forest` (storm: `rain`, `lightning:[[shot,sec]]`), `mountain` (+`rockslide` prop), `cave` (+`treasure`, `sign`, `key`, `beam_x`, `wall_z`), scene key `mountains:true`.
- Little Kraggor: prop `kraggor_small` (x,z,face,height,mode scared|munch|smile|sleep|calm, `cone:{from,secs}`, `sway`, from_shot/to_shot) = baby head of the real Kraggor drawing (story25d `kraggor_baby_head`). Reuse in scene 13 (photo piece / net).
- SFX: thunder_roll, rockslide, munch, whimper, snore, drip, key_glint, breath_big; sfx entry may carry a 3rd element = gain, e.g. ["thunder_roll", 1.5, 0.6]. Ambience: `storm`, `cave`.
- Sepia: scene `"tint":"sepia"` (applied once in compose). Test tool for new Godot code: `modal_story3d.py::smoke --scenes N` (run with the branch checked out BEFORE merging); `tools/contact_sheet.py` for the self-review sheet.

## Next: scenes 9-15 (see script.md). Needs: big Kraggor in the cave (scenes 9,10: face to face, chalk wall drawings), gate + crane net (11-13), party plaza (14), old speedway gate at dawn (15).

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
