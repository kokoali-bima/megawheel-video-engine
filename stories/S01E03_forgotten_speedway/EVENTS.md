# S01E03 EVENTS — rescue, finish, collapse (document revision 4, answers Codex gate v1.4)
Package hashes: builder 4b786da215fc9453, real_shot_times.json f1aa3ff18b6efb30, engine_all.diff acd9243069cf2212 (sha256, first 16 hex). Earlier labels v2/v3 and the v1.3 hashes are history only.

Evidence types used below: **table** = shot start/end read from the exported render timeline (`real_shot_times.json`, signed per scene by a structural sha; the builder refuses a stale table); **authored** = offsets/delays chosen in the builder; **calculated** = from the engine formulas; **sampled** = read from preview stills (NOT per-frame measurements). Shot starts are NOT the old estimator and NOT `ST.build()` t0. Real audio mix/assembly is not measured and nobody has watched the voiced film.
Source of truth: `build_s01e03.py` (shot_start() reads `real_shot_times.json`). Lint: 0 errors in all 10 scenes.

## (a) RESCUE — Scene 9 (render length 62.8 s)
Design chosen (answers Codex v1.3): **UNHOOK BEFORE LEAVING**. The cable endpoint stays at Zippy's tow ring (x 24.8, z 1.3) while he is stationary; the hook is released while the car is still at the ring, and only after release does he drive away. There is NO moving-hook / follow transform in the engine and none is claimed.
| event | shot | scene time | evidence type | what is visible | JSON field |
|---|---:|---:|---|---|---|
| Start = end state of S8: outer lane tilted, hole/strut damage already finished, Zippy already tipped (static, no re-sink), claws raised | 0 | 0.0 | authored | bridge keys final, holes `[[-3.0..]]`, diag `[25,-3.0]` (damage clock already past), `zippy.sink{dur 0}` | `bridge.holes/diag`, `sink dur 0` |
| Nitro leaves the span and stops to keep the exit open (x 43.5), speaks only afterwards | 0–1 | 0–3.0, line 3.0–7.6 | authored + lint | outside x 38 plus margin | `moves.nitro.to_x=43.5` |
| Sprinkles answers the offer: "Hold the exit, Nitro. We finish together, or not at all." | 2 | 7.6 | dialogue | medium shot | shot line (replaces "No, Nitro...") |
| Sprinkles braces Zippy: moves into Zippy's lane (z 1.3) to bumper contact (centre distance 4.9 m = 2.8 + 2.1) | 2–5 | 7.6–26.0 | authored; contact declared | Sprinkles against Zippy's raised end | `moves.sprinkles{to_x 29.1,to_z 1.3}`, `contact [sprinkles,zippy]` |
| Winch pays out slack from Hydro's drum (x 49.2, z 3.2) to the ring | — | 0.5–1.3 | authored | dark cable, diagonal in depth, hook at the ring | `rescue.winch t0 .5, dur .8, from_z 3.2, to_z 1.3, sag 1.2` |
| Hydro "Cable is on Zippy's tow ring..." + Rocky "Not budging" | 3 | 12.03–19.03 | dialogue | slack cable | shot lines |
| Cable starts to tension (taut ramp 0.5 s) / fully taut | 4 | 19.23 / 19.73 | calculated from `_rescue_update` | sag gone | `winch.taut_t 19.23`; chain_rattle sfx at shot 4 + 0.4 = 19.43 |
| Roar of the unseen giant (claws stay) | 5 | 22.03 | sfx | low shot | sfx `roar` |
| Hydro order "Zippy first, then Sprinkles, then Rocky" | 6 | 26.03–34.07 | dialogue | wide | shot line |
| Sprinkles steps back out of Zippy's lane (z 1.3 to 0.2), before Zippy leaves | 6 | about 29–30 | authored (delay 3.0) | frees the lane | `moves.sprinkles{to_z 0.2, delay 3}` |
| Zippy is righted GRADUALLY: sink recovers from the tipped pose (depth 0.5, tilt -0.55) to upright over 0.6 s while the cable is still taut and the claws hold | 7 | 34.07–34.67 | authored; engine interpolation (new `from_depth`/`from_tilt`) | tilted car levels out on the span; stable at 34.67 | `zippy.sink{at 0, dur .6, from_depth .5, from_tilt -.55, depth 0, tilt 0}` |
| **Cable released (hook off the ring) only AFTER Zippy is stable, BEFORE he moves** | 7 | 34.87 (0.2 s after upright; reel-back ends 35.67) | authored | hook reels back, car still at the ring | `winch.release_t 34.87` (= shot 7 start + 0.8) |
| Zippy drives away 0.2 s after the reel-back ends: inner lane z 2.4, x 41 (delay 1.8 s, speed 8) | 7–8 | starts 35.87; rear clears x 38 at about 38.47 (calculated: easing T=1.25*d/speed+0.4, start+2.60); centre reaches x 41 about 38.90 | authored + calculated | car leaves the span on the inner lane | `moves.zippy{to_x 41,to_z 2.4,delay 1.8,speed 8}` then `{to_x 47,to_z 1.3}` (shot 7 hold 5.4) |
| Sprinkles second, then Rocky third, one at a time on the inner lane, parking at x 51 z 0.2 / x 56 z 2.1 | 9–12 | 41.37–54.77 | authored | one mover at a time | `moves.sprinkles`, `moves.rocky` |
| Claws stay until Rocky has left the span | 3–11 | until 51.77 | authored | none in shot 12 | `claw` |
Open for media (not claimed): hook position on the real truck winch; ring HEIGHT while the pose changes (the endpoint is fixed at y 0.9, only x/z are matched; the pose change is small); the cable behind the overlay cars; whether Sprinkles' brace reads as support.

## (b) FINISH — Scene 10 (render length 43.5 s)
| event | shot | scene time | what is visible | JSON field |
|---|---:|---:|---|---|
| Four cars accelerate abreast in a diagonal (far lane slightly ahead) | 0 | 0.0–6.0 | Sprinkles z -0.2 nearest ... Nitro z 3.1 | `shots[0].moves` (to_x 35.7 / 39.4 / 42.35 / 45.2, speed 22) |
| All four noses cross the line (x 60) within about 0.5 s | 1 | calculated nose times at x 60: Nitro 6.98, Rocky 7.14, Zippy 7.31, Sprinkles 7.50 (spread 0.52 s); stills only sampled, frames not measured | chequered line, diagonal photo finish | `shots[1].moves` (to_x 60.7 / 64.4 / 67.35 / 70.2, speed 20) |
| Scoreboard "MEMORIAL LAP COMPLETE" AFTER the crossing | 1 | 7.75 | board text swaps | `scoreboard.texts [[0,..],[7.75,"..COMPLETE"]]` |
| Announcer "Four cars hit the old finish line as one!" | 1 | 6.0–10.2 | crossing | shot line |
| Siren "Memorial Lap complete..." only after COMPLETE | 2 | 10.2 | wide | shot line |
| Trophy case drawer opens AFTER the key-click | 4 | 24.2 (key_click at 0.8 in shot 4) | drawer opens, then blueprint | `trophy_case.drawer_t 24.2`; sfx key_click/key_glint |
| Blueprint only visible in the last shot | 7 | 37.0 | blueprint beside the case | `blueprint.from_shot 7 to_shot 7` |

## (c) COLLAPSE — Scene 1 vs Scene 8 (same cause-and-effect, same final state)
| event | S1 (shot 1) | S8 (shot 11) | JSON field |
|---|---|---|---|
| Shot start (bridge timeline T0) | 1.6 | 52.13 | `bridge.keys/outer_keys[0][0]` |
| Diagonal strut breaks | T0+0.6 (2.2) | T0+0.6 (52.73) |
| Rockslide sfx | T0+0.0 | T0+0.0 | sfx `rockslide` |
| Outer deck at +1.2 is already tilted/dropped (interpolation starts after +0.4); hole opens at +1.2 | T0+1.2 (2.8) | T0+1.2 (53.33) | `outer_keys[1..2]` |
| Hole opens | T0+1.2 | T0+1.2 | `holes[0]` |
| Zippy loses footing and tips AFTER the hole (1.5 s into the shot) | 3.1 | 53.63 | `zippy.sink{at 1.5, dur 1.0, noclip}` |
| End state (outer .7/.8, inner .3/.4, claws) reached at T0+2.6 | 4.2 | 54.73 (= S9 start state) | `outer_keys[3]`, `keys[1]` |
| Real shot length | 3.2 s (ends 4.83, then dialogue shot) | 3.2 s | `real_shot_times.json` |
Note: in S8 the preceding wide (shot 10) brings Nitro/Sprinkles/Zippy/Rocky to the formation at walking pace (speed 4); no overtaking on the span. S8 re-pass of Sprinkles by Nitro happens in shot 7 (before "Nice try, ice cream!").

## (d) Other revised events (Codex v1.3 items)
| scene | change | evidence | JSON field |
|---|---|---|---|
| S4 | Grandpa and Buster in the SAME lane (z 2.2) with bumper contact; centre distance 6.5 m = bus half 3.7 + ice-cream half 2.8 during the whole tow (6.50 in frames.json from the approach end, through the reverse pull, to the final shot) | frames.json (measured) | `to_z 2.2`, `contact [grandpa_cone,buster]`, to_x -2.5 / 6.5 |
| S6 | bridge intact during the inspection: no strut/hole event | authored | `diag [25, 999]` |
| S7 | Kraggor walks along the access road to the gorge side and out of frame; arms appear only in bridge shots (no descent animation is claimed) | stills | `kraggor.walk {to_sx 1.3, dur 3}` |
| S7 | Hydro anchor: ground bollard at winch from.x plus drum on the truck | authored | `rescue.winch from [49.2,1.4]` |
| S8 | Zippy's line now says "right behind YOU" (Sprinkles x 18 is behind Nitro x 24 and ahead of Zippy x 8) | dialogue | shot 9 line |

## (e) Timing evidence and limits (Codex v1.4/v1.5 items)
- Shot starts/ends come from the exported render timeline (frames.json) after the real voices existed; the table is rewritten only by a fresh export (refresh script), then signed. The builder REFUSES a missing/unsigned/incomplete/mismatching table (S01E03_ALLOW_ESTIMATE=1 is an explicit experiment mode). `--write-sigs` refreshes the checksum only; it does not measure anything and was not used to re-sign a stale timeline (the S9 hold change was followed by a full re-export first).
- The signature covers only per-shot hold + speaker + text. It does NOT cover voice model/reference/audio hash, lead/gap/tail/J-cut/freeze settings or the engine version, so a voice change with the same text is NOT detected automatically. `_meta` in real_shot_times.json records the voice-cache file count (63) and the engine diff hash (acd9243069cf2212) of the export.
- Evidence types: table, authored, calculated, sampled (stills). Nothing here is a per-frame measurement of the voiced film; nobody has listened to or watched it.
- Global table check (Codex v1.5): before ANY scene file is written the builder validates the table for ALL scenes 1..10: key present, entry count equals the built scene's shot count, every entry a [t0,t1] pair with t1 > t0, first t0 = 0, consecutive entries contiguous (0.002 s), `_sig` complete and matching. `--selftest-table` proves it in memory: the real table passes; deleting scene 4, dropping the last shot of scene 7, dropping a middle shot of scene 9, breaking contiguity in scene 2 and deleting a `_sig` key each RAISE (6/6 PASS). A real-file mutation (scene 4 key deleted) was also refused with zero files written. Only S01E03_ALLOW_ESTIMATE=1 skips it.
