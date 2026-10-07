# AGENTS.md — operating manual for ANY AI agent (Claude, Gemini, OpenAI/Codex, DeepSeek, Kimi, …)

> Owner decision 2026-10-06: "usahakan buat standar agar Gemini, OpenAI, DeepSeek, bahkan Kimi pun bisa membuat
> video yang sama kualitasnya." Quality must come from the **machine** (fixed scripts, linters, QA sensors), never from
> how clever the model is. Your job is narrow: write/repair JSON, run the fixed commands, read the reports, fix what
> they say. If a step here is unclear, STOP and ask the owner — do not improvise.
> Language: talk to the owner in **Bahasa Indonesia**; video content is **en-US**.

## 1. Golden rules (breaking one = the work is rejected)
1. **Never upload to YouTube** and never approve/reject/swap episodes yourself. Uploads run only from the cron
   (`daily_publish.sh`) after the owner approves. You may upload review copies to Google Drive.
2. **Never commit or print secrets**: `credentials/`, `modal.txt`, tokens. Never open `modal.txt`.
3. Git author is always `kokoali-bima <mu.aliwardana@gmail.com>`. On the VM sync ONLY with `bash git_sync.sh pull|push`.
   The Modal usage ledger (`modal_usage.json`) is dirty after every run: `git_sync.sh status` prints `ledger: BERSIH|KOTOR`, `pull` commits+pushes a dirty ledger itself (loud `!! LEDGER ... KOTOR` line) and produce_story3d commits it when it ends. Never `git checkout -- modal_usage.json` (deletes cost records). If `status` says behind or the ledger is dirty, run `pull` BEFORE any render.
4. **Production never imports `lab/`.** Experiments live in `lab/` (PC) / `/root/lab` (VM).
5. **Never re-draw characters in 3D.** Characters come from story25d / sim_engine exactly as aired.
6. Run renders on the VM **one at a time** (OOM). Heavy work goes to Modal through the scripts below.
7. Budget: Modal $29/month — the scripts check `modal_usage.json`; never bypass the guard.
8. Do not change QA thresholds, sensors or approved engines (Shorts 2.5D) without the owner.
9. Log every exchange with the owner in `ipandu-video/claude/agent_claude.md` (append, Indonesian).

## 2. Where things are
| What | Where |
|---|---|
| Production VM | 192.168.99.3 → `/root/video-engine` (public SSH: `-p 22022 root@2.28.128.77`, key from the owner) |
| Shorts engines (2.5D, approved) | `generators/physics_2d/sim_engine.py` (CHALLENGE), `generators/lanes25d/race25d.py`, `smash25d.py`, `generators/produce.py` |
| Long story episodes (Ep.2+) | **story3d** = `generators/story3d/` (Godot world + story25d characters, Modal) — SOP: `generators/story3d/SOP_STORY3D.md` |
| Characters & voices | `CHARACTERS.md` (fixed identities), `branding/voice/characters/*.wav` |
| Music cue library | `branding/music/cues_<ep>.json` → `branding/music/cues/*.wav` |
| Story files | `stories/<episode>/outline.md`, `script.md` (owner-approved), `scene_NN.json` |
| Standards | `BLUEPRINT.md`, `CONFIG_BEST.md`, `PRODUCTION_STANDARD.md`, `SCALE_STANDARD.md` |
| Defects & sensors | `QA_DEFECT_TRACKER.md`, `ERROR_LOG.md` |

## 2b. The style contract (fix once, never again)
`generators/story3d/STYLE_CONTRACT.json` holds EVERY lesson from owner reviews as a numbered rule (C01 talking heads,
C02 bumper-to-bumper, C04 J-cuts, J01 rushed transitions, A01 empty silence, …) with the numbers the linter, the QA
sensors and the assembler use. A new owner note = a new rule there + a tracker row, never a one-off hand fix.
`golden` scenes are re-linted on every produce run (regression).

## 3. Making a story scene (story3d) — the only allowed procedure
```
# on the VM
cd /root/video-engine && bash git_sync.sh pull
# 1) write/edit stories/<ep>/scene_NN.json  (copy the structure of the golden examples, §4)
# 2) lint — free, no render cost; repeat until 0 errors
venv/bin/python generators/story3d/validate_scene.py --episode <ep> --scenes NN
# 3) render + QA (+ Drive upload for the owner's review)
venv/bin/python generators/story3d/produce_story3d.py --episode <ep> --scenes NN --upload
# 4) commit the scene JSON:  bash git_sync.sh push "S01E0X scene NN: <what changed>"
```
Exit codes of produce_story3d: 0 ok · 2 lint/preflight · 3 voices · 4 Modal render · 5 **QA FAIL** (never upload a
FAIL; fix with the playbook in SOP_STORY3D §5 and run again). Report to the owner: scene, QA verdict, warnings, cost,
Drive link — in Indonesian, short.

## 3b. Episode bookends (owner 2026-10-07)
The whole episode = cold open (scene 1) -> ident + theme song (aired Ep.1 clips, scene 0) -> "Previously" recap (scene 21) -> scenes 2..N -> outro (scene 20). `venv/bin/python generators/story3d/tools/make_bookends.py --episode <ep>` builds 0/21/20 into the Modal volume; then `assemble --order 1,0,21,2,...,N,20`. Scene JSON with `"no_card": true` gets no PART card.

## 4. Writing scene JSON (what models get wrong)
- Start from the **golden examples**: `stories/S01E02_who_is_kraggor/scene_01.json` (night, song, reveal) and
  `scene_02.json` (day, ensemble dialogue). Same keys, same style. Unknown keys are rejected by the linter.
- **Film coverage, not talking heads** (owner 2026-10-06): establish the group, play exchanges in `group` / `two`
  shots (several lines in ONE shot; the group camera leans toward the speaker, listeners look at them), use single
  close-ups only for an emotional / comic beat or a reaction. The linter rejects ≥ 3 close-ups in a row switching
  speaker, > 50 % of lines in single close-ups, and a 3+ character dialogue without a group/two shot carrying ≥ 2 lines.
  Let characters move while talking (walk-and-talk) and add silent reaction shots.
- Vocabulary (exact strings): cam `wide|group|two|medium|close|ecu|low|track` (`group` takes `"group": [ids]`); camera `move` keys
  `push|pull|pan|crane|dutch|handheld|whip`; emotions `normal|happy|laugh|proud|excited|scared|surprised|sad|cry|
  angry|worried|determined|shy|whisper` (+ `calm` for lines); effects = names in `story25d.SFX`; music = cue files.
- A line is `[speaker, "text", emotion]` — short spoken English (≤ 140 chars, one emotion, "..." for pauses).
  One line per shot for close-ups; give the speaker the shot (`"on": speaker`).
- Variety: ≥ 3 shot sizes, never 3 identical sizes in a row, ≥ 2 kinds of camera move, end the scene on a hook
  (`push`/`low`/`punch`).
- Music is **spotting**: `score` ranges per moment (`from`/`to` shot), stings on beats, silence is allowed. Scary
  music only when the threat is seen. Never one cue for the whole scene.
- Effects after lines: `["honk", "end+0.1"]`. Effects must be phone-audible (the sensor checks).
- Staging: cars stay on the road band `z` −0.6…3.2; a car closer to the camera (smaller `z`) must not stand in front
  of the speaker (the linter computes it). Props that appear later: `from_shot`.
- Night in town = `ambience: city_night` (no crickets); day = `birds`.

## 5. What "same quality" means (acceptance)
A scene is acceptable only when: lint 0 errors → produce_story3d exit 0 → QA verdict PASS/WARN with every WARN
explained to the owner → the owner approves the Drive copy. The sensors (SOP_STORY3D §4) measure camera smoothness,
Godot/cairo alignment (no tilted road / floating cars), occlusion, variety, light/contrast/shadows, noise/hiss, dead
air, music masking voices, phone audibility, music monotony, loudness (−16 LUFS) and reveal timing — identically for
every agent. Pinned: Godot 4.4.1, rhubarb 1.13.0, Luckiest Guy font, seeded worlds, cached voices.

## 6. When the owner reports a new problem
1. Reproduce it from the frames/audio (extract frames with ffmpeg, measure, do not guess).
2. Fix the root cause in the engine (not by hand-editing a video).
3. Add or extend a **sensor** so it can never pass silently again, and a row in `QA_DEFECT_TRACKER.md`.
4. Update `SOP_STORY3D.md` / this file if a rule changed. Commit with a clear message.

## 7. Shorts (CHALLENGE / RACE / SMASH)
Use `generators/produce.py` exactly as documented in `AGENT_VIDEO_PRODUCER.md` (variety director, SOP gates,
registry). Do not touch Shorts engines for story work.

## 8. Challenge Shorts on story3d (owner 2026-10-07)
Rotate the 10 characters (least used first), never reuse an obstacle, title carries "NEW 3D Graphics" while the graphics are new,
A10 music (fail runs + win only), outcome simulated in the generator. Details: stories/CH01_dungeon_axes/HANDOVER_CHALLENGE.md.
Git/VM pitfalls (never repeat): never `git checkout -- modal_usage.json`; merge/push from a fresh clone of origin/main (Drive CRLF
noise); validate ALL scenes before pushing; stop VM processes only via stop_story3d.sh; read ERROR_LOG.md section Z.
