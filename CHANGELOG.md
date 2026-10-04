# CHANGELOG — MegaWheel Arena video engine

Dibuat otomatis oleh `tools/make_changelog.py` dari riwayat git (terbaru di atas). Setelan terbaik yang
berlaku: **CONFIG_BEST.md**. Kesalahan & pelajaran: **ERROR_LOG.md**.

## 2026-10-04
**📤 Upload / antrean / Drive**
- `90a5fa8` publish: daily run 2026-10-04 [cron daily_publish.sh]
- `c657eee` episodes.py unreject: a REJECTED render back to pending (MP4 restored from Drive) when the user changes their mind
**🏁 RACE (race25d)**
- `53a7710` race25d: zoom in on the star moment (the asked-about car was often tiny in a back lane)
- `3a65754` race25d camera: when hazard moments overlap, focus the title's star (S022 test: cold open framed the ice dragon while asking about the hammer)
- `2437c64` race25d crusher: the press stops on the victim's roof and follows the squash (tall trucks were pierced by the press/rod)
- `de29f8a` RACE cold open: question in the top band over a dark gradient (not over the action); title, cold open and replay share one star moment
- `d73348d` race25d: cars swerve around (or brake behind) a fresh wreck in their lane; camera glides with a speed cap instead of jumping
- `9ecbffa` race25d: title/hook question asks about the racer who really meets the most striking hazard (honest payoff)
- `9ea2ec7` race25d v4: class speeds F1 > sports > police > taxi > monster > icecream/firetruck > bus/bigrig, pickup per class, realistic-order check
**🔧 Lain-lain**
- `ce29c73` cold open 1.5 s -> 3.0 s for every Short (user: opening clip too fast, add 1-2 s); duration checks follow the uncapped-duration rule
- `970dfca` approve: SIM_POTHOLES_V2_S028, S029 (user 2026-10-04 changed mind) + plan
- `3d5a8f2` approve: SIM_POTHOLES_V2_S031, SIM_RACE25D_V4_S018 by user 2026-10-04 + plan
- `a4aaf65` reject: SIM_POTHOLES_V2_S028, S029 (user 2026-10-04)
- `8cd1793` potholes: a planned pit content (spikes/bomb/Pit Muncher/water) must be met by a failing car on screen
- `6312200` pits: trigger height per content = its drawn height (a truck touching the bomb must set it off)
- `f70f682` pits: contents trigger on any body corner / tyre near the floor (nose-dives), bigger spikes
- `5390778` variety director + potholes v2: 6 layout templates, 6 pit shapes, sizes S/M/L, per-pit contents (rubble, water, lava, spikes, bomb, Pit Muncher)
- `8d2d719` PROJECT_PROGRESS C13: potholes layout is one template (finding 2026-10-04)
- `c75a0a7` CONFIG_BEST: production stays 2.5D, Godot 3D lab-only (user 2026-10-04)
**🕳️ CHALLENGE (sim_engine)**
- `18b04dd` produce: SIM_RACE25D_V4_S025 (pending review) [Claude Code Opus]
- `db4a943` produce: SIM_RACE25D_V4_S024 (pending review) [Claude Code Opus]
- `54d2b75` produce: SIM_RACE25D_V4_S023 (pending review) [Claude Code Opus]
- `a56100a` produce: SIM_RACE25D_V4_S022 (pending review) [Claude Code Opus]
- `fe9e0d4` produce: SIM_RACE25D_V4_S021 (pending review) [Claude Code Opus]
- `2b4948d` produce: SIM_RACE25D_V4_S020 (pending review) [Claude Code Opus]
- `9d60907` produce: SIM_RACE25D_V4_S019 (pending review) [Claude Code Opus]
- `ac63241` produce: SIM_POTHOLES_V2_S031 (pending review) [Claude Code Opus]
- `775cfbf` produce: SIM_POTHOLES_V2_S029 (pending review) [Claude Code Opus]
- `08e6ed6` produce: SIM_RACE25D_V4_S018 (pending review) [Claude Code Opus]
- `5a378e7` produce: SIM_POTHOLES_V2_S028 (pending review) [Claude Code Opus]
- `9b1b3b3` produce.py (standard production command with SOP gates) + race25d hazard layouts from the variety director; duration not capped (user)
**🧪 Lab (eksperimen)**
- `2bfc0a1` lab hybrid: upload_sample.py (Drive lab/hybrid)
- `9a6e738` lab hybrid: darker sea with sun path, purple headlands, brighter clouds
- `ac6a7b8` lab hybrid: cairo screen-space sky + sun, visible sea, low dunes, fuller palms
- `4f5ad71` lab hybrid: Godot background project (beach sunset: theme sky, sun glow, waves + glitter, foam, dunes, palms, clouds, gulls)
- `a2d61b8` lab hybrid: exporter (aired 2.5D frames with transparent background + background camera)
- `2fe3bf8` lab: revert3d.py (review videos back to the 2.5D engine, user 2026-10-04) + ERROR_LOG for the 3D review batch
<details><summary>otomatis VM (21)</summary>

- `7a9701d` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `006c749` records
- `2c19b34` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `d5b8ea0` records
- `d5a788f` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `ceffc17` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `e43110c` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `5b450d9` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `3293e89` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `899f33f` records
- `4844468` records
- `cc72763` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `f39fb12` records
- `cb8cabd` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `6eee909` records: hybrid sample
- `834f290` records
- `de21c92` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `56ea272` records: modal ledger
- `16a2e04` records: modal ledger
- `372971c` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `ed4542b` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine

</details>

## 2026-10-03
**🔧 Lain-lain**
- `924d955` approve: 18 review videos (2.5D) by user 2026-10-04 + plan
- `a5ae239` audit3d: brightness samples skip the cold-open white flash (false alarm on RACE S011)
- `876f213` BENCHMARK_NICHE: top crash channels (content + marketing) vs MegaWheel, action list
- `abfe6f7` CONFIG_BEST: no-explosion rule is for CHALLENGE crashes; SMASH explosions stay (user)
- `f52fa4c` Shorts: unique hook titles (character + challenge + question), potholes = half of CHALLENGE
- `115d5f5` Shorts: 1.5 s cold open (own biggest moment + question) before the normal start
- `526bd56` RESEARCH_W3: week-1 Shorts data, 2.5D first / 3D optional, cold-open + potholes plan
- `d4dd29c` Shorts: no background music (narrator only), theme song faint after the win; lab 3d v6 fighter intros
- `13387d3` SCALE_STANDARD.md + Godot scale report; 3D arena 20x24 m at 50 px/m
**🧪 Lab (eksperimen)**
- `e9f4369` lab 3D converters: 3D preview sheet includes outro.png (production audit 5.2)
- `5fb2e92` lab 3D: rigid metal damage for all 3 formats + --redo in every converter
- `5a5b6fa` lab 3D SMASH: no sun shadow map (dark wedge on the floor with the lens-shifted camera), scenery casts no shadow, debris pieces sized in metres (Titan gave 3 m shards), darker steel floor like the aired one
- `49fd526` lab 3D SMASH converter: --redo re-renders a 3D video (2.5D _25d.mp4 stays the reference)
- `8c18d7b` lab 3D SMASH: night headlights + floodlit paint; brightness audit relative to the aired 2.5D (night themes are dark there too)
- `51b623c` lab 3D SMASH: meta title + cold-open fallback = production (winner finish)
- `aa9834a` lab 3D SMASH from the aired engine (smash25d v5) + converter
- `bc9e4a3` lab 3D RACE renderer + converter; night headlights; Modal renderer for any project
- `25f4e7b` lab 3D: forced narrator switches voice C on (like cb_pick); RACE exporter
- `38c637d` lab 3D: Modal GPU (Vulkan on a T4), colour parity, exact sim replay for conversions
- `22536a5` lab 3D CHALLENGE v3 + convert3d: review videos re-drawn in 3D, audit3d gate
- `f76a3ba` lab 3D: Modal renderer (one 16-vCPU container per level, parallel) + all wheels drawn
- `c8cd97b` lab 3D CHALLENGE: drop the glass chips (rendered as big white squares)
- `1ff63a2` lab 3D CHALLENGE v2: dents, lava = fire + explosion, water splash, walls/puddles/lava vents
- `393a336` lab: 3D CHALLENGE sample driven by the aired sim_engine; crash damage without explosions
- `cc1108f` lab 3d v6: tyre squeal (own synth) on wheelspin at GO and when a car turns around to attack
- `c4e73ca` lab 3d smash v5: aired end card + replay overlay, commentators, crowd, sonic logo, smoother explosions
- `ce44122` lab 3d v4: midday sun from the camera side (stand shadows fall behind the stands), contact shadows under cars
- `be29dc4` lab 3d v4: stands cast no shadow, stop 8 s after the winner (end card 5 s)
- `d096aa5` lab 3d smash v4: smash25d camera geometry + smash25d win logic
- `2301885` lab 3d: no double KO from a late finishing hit, replay concat setsar, smaller scorch marks
- `48f957a` lab 3d smash v2: bigger/deeper arena, steeper camera, reclined cards, 30-40 s pacing
- `891d5d7` lab 3d smash v2: water + shark, progressive damage, chaos themes, Sonniss SFX, replay
- `ac64206` lab 3d: white rounded end card
- `d947d78` lab 3d: low friction (fast cars), balanced damage, chaos later
- `e0c080f` lab 3d: ram AI (charge / back off / charge), no pushing stalemate; Kraggor 70 dmg
- `84c1720` lab 3d: collision box from wheel bottom to roof (cars floated, drive never engaged)
- `d0118b0` lab 3d: cars never sleep (drive force was ignored)
- `d8c5884` lab 3d: debug position print
- `97d359c` lab 3d: framing like smash25d (arena lower in frame), darker floor, no stands banner
- `4fd9b09` lab 3d: darker floor, banner fixed, camera params, cheaper lights/shadows; mix NaN guard
- `5fb211c` lab plan B: SMASH ARENA in real 3D (paper cast, lit lava arena, rigid-body battle, missiles, Kraggor foot, fracture, HUD)
- `9632ecd` lab fx: soft round particles, gentler local lights, subtle shockwave, no FX over end card; runner reuses capture
- `84a3a4f` lab fx: bigger lava ring-out burst + SFX
- `64c9f38` lab: method A - Godot FX layer over cairo SMASH frames (capture cues without touching production, explosions, fracture, shockwave)
- `696048f` lab: move Godot prototype out of generators/ into lab/ (experiments separated from production)
- `aab4abd` godot: speed-controller drive (reliable pacing), challenge crash threshold for pit landings
- `a271f63` godot samples v2: single short slow-mo, close/auto-fit camera, CCD, staggered spawns, reliable hammer, deferred fracture, arena stands; godot_mix.py SFX
- `a9ffd8a` godot: untyped locals (fix type-inference parse errors)
- `c290925` godot: showcase samples challenge/race/smash (fracture, explosions, slow-mo, real collisions, meteors)
**🕳️ CHALLENGE (sim_engine)**
- `758980a` CHALLENGE: shift manifest times by the cold open; audit duration bound 58 -> 59.5 s
- `f406421` CHALLENGE: new series lava_potholes (potholes track, every pit full of lava)
**📤 Upload / antrean / Drive**
- `adadaa9` publish: daily run 2026-10-03 [cron daily_publish.sh]
- `f82dce5` episodes.py swap <EP> <NEW_VIDEO_ID>: replace a queued, not-uploaded episode with a newer render
**💥 SMASH (smash25d)**
- `a886d64` smash25d v5: sea arena + shark, POW + hit-stop, parts fly off, smoke/fire by HP
**📚 Dokumen**
- `d891009` docs: CONFIG_BEST (approved settings, single source) + auto CHANGELOG from git (daily via analytics cron)
- `5c66ee0` docs: GODOT_PLAYBOOK (techniques, references, production rules, roadmap) + SFX_PLAN (pro SFX bank research)
**📊 Analytics**
- `cd00dae` analytics: Telegram text + JSON outputs, daily cron script, agent guide (no credentials in outputs)
<details><summary>otomatis VM (32)</summary>

- `31ffd83` records: 18 review videos back to 2.5D (user 2026-10-04)
- `4abffd3` records: 3D redo
- `767b474` records: 3D redo batch
- `e3d69d6` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `937c0e7` records
- `4fa8ae2` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `d765bcc` records: SMASH 3D redo
- `6ccbbdc` records: SMASH 3D S004
- `1c0ee98` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `e8fd4e7` records: SMASH 3D batch
- `50e2593` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `a84e02f` records
- `eec84a7` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `edddcd7` records
- `28261bc` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `b676941` records
- `63e5724` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `0badbb7` records
- `cb1b85d` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `792b807` records
- `5bcca42` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `e9ffd92` records
- `0b23381` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `1289ede` records
- `fd5d3c6` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `33ab47b` analytics: daily report 2026-10-03
- `e9f4045` records before analytics
- `41bc962` records: batch A+B renders
- `f9471e9` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `ec8d817` records: batch renders
- `9c98d12` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `49b12e8` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine

</details>

## 2026-10-02
**🧪 Lab (eksperimen)**
- `cafc266` lab 3d run.sh sheet times
- `dd1436f` godot_race: prototype (cairo cast sprites + Godot rigid-body cars, sunset light/shadows, parallax, dust, hook)
**📊 Analytics**
- `b5ecea4` analytics: first report
- `8c37a0b` analytics: yt_analytics.py (own read-only token, weekly report per series/video)
**📚 Dokumen**
- `279915f` gitignore: generated Godot sprites/cache
- `655fd4e` docs: audience path A (general audience) production rules
- `eb98e4a` docs: RESEARCH_W2 (titles/hooks, lighting & sound, story structure, lip-sync, theme song review, week 2-3 roadmap)
- `212c565` docs: PRODUCTION_STANDARD (research: retention, environment, transitions, 5-layer sound, gap analysis); S01E02 outline proposal
- `0a0b069` error log: stale-code render guard
- `df53f5d` docs: IP protection plan for characters; error log hung modal process
**🎵 Musik / lagu tema**
- `d1e9bf7` music: sonic logo jingle (Mega, Mega, MegaWheel - 3.8 s)
- `561f668` music: intro remix3 (band x1.7, vocals x0.55, wider stereo) per user
- `ad7acca` songs: intro v4 per user review of v3_alt2 (shorter lyrics, complete ending, pop not rock, -1 semitone, gentle band lift); ending check in take ranking
- `b35d9f7` modal_yue: torch 2.6 (transformers torch.load guard)
- `01d7340` modal_yue: newer protobuf for the Modal runtime (image build error)
- `4911d80` songs: intro v3 spec (user lyrics + verse 2, v1 style, no remix); modal_song keeps top-N takes for a human pick
- `c62b811` songs v2: 56-60 s full structure (intro/inst/outro), Demucs vocal/music rebalance + fades; docs: music model licenses, Tilly/Nitro voices
**🏁 RACE (race25d)**
- `fcb76ce` race25d v3: curved circuit, giant hammer / falling container / oil slick, question hook title + on-screen question, sonic logo on the win
**🎬 Story / episode panjang**
- `c9d1d1d` story: phoneme lip-sync (Rhubarb Lip Sync, 8 Preston Blair mouths) + body bounce on stressed syllables
- `2615ea5` story: S01E01 trailer shot list (scene 90, vertical Shorts)
- `f0a824e` story: black gaps long enough for their fades; assemble checks part vs transition length
- `845633e` story: clean black gaps (no overlap) between cold open, ident, theme song and story
- `37de661` story: ambience beds per location/time (crowd, birds, night crickets, garage room tone)
- `5e00c89` story v9: episode order (cold open first) in edit.json
- `6110bf4` story v9 (research): cold open before ident + theme, eyes-in-the-dark teaser, YouTube chapters, 14 s end-screen area
- `7dc40e7` story: theme songs mixed in stereo (extrastereo widening), voices centred; intro remix with louder band
- `4d39f33` story: scene 10 rivals drive away over the hill, wider hilltop; closer Zippy shot
- `4c4b6e2` story: wide/track cameras follow hill height; scene 10 framing on Sprinkles at the top
- `0a4eabb` story: glide settles by mid-shot; scene 10 drives the hill (no roll); foot on Zippy's nose; staging fixes 2/12/14
- `71e73c5` story: one truck tune in scene 2
- `20c675a` story: v7 review shot-list fixes (transition sounds per edit.json, poster, flashback, foot, scenes 12/14)
- `b2b11d9` story: user review v7 — signs over trees, hill-aware rolling camera (no rewind), low-shot framing, slower pacing, truck tune instead of ding, no shock hits, cinematic whoosh/memory swell, foot on Zippy's front half, staging scenes 12/14
- `22023a7` story: note sits under a caption when both show
- `9782d3d` story: note below letterbox, Kraggor feet on the road edge, wink lid on the eye
- `34b4af5` story: scene 2 Buster face clear
- `f0e284d` story: roll scrolls the world per shot (cars keep place, wheels spin) instead of moving cars; staging fixes
- `bdc05f1` story: fix audit findings (echelon staging so faces stay visible, framing, #13, context)
- `965dec5` story: user review v6 — camera glide, whole-vehicle framing, notes, mud, reverse, roll, jingle, softer hits, Kraggor on ground + wink, cast name cards, ident, slower transitions; audit_story.py; song remix mode
- `a10a6e8` story: low-RAM transition assembly (pairwise xfade pieces + concat); modal_yue pins YuE v1 (Apache) not YuE2 (CC BY-NC); license table
- `fd6c6e4` story: S01E01 draft v6 (transitions) + intro candidates (ACE v3, YuE) + ledger
- `31f3dca` story: drama transitions (xfade per edit.json, whoosh), no per-scene black fades; modal_yue.py (YuE on L40S) + intro spec
- `4584eaf` story: drama pacing (scene gap/tail), fix QA-failing line 'Name?'
- `3207668` story25d drama toolkit (crash zoom, triple-take, freeze-frame cliffhanger, sting/heartbeat); S01E01 drama pass
- `5ee5375` story: S01E01 draft v4 (Tilly/Nitro voice refs, theme songs mono, voice ledger)
- `559467d` story25d hills/glowing eyes/song scenes; S01E01 v3 shot lists (intro + 16 scenes + outro); modal_song pins torch 2.5.1 (torchcodec error)
- `0ee037a` story25d v1 fixes (rain, framing, booth, Grandpa look, eased motion, squash/dizzy/plaster, jumbo cone, Kraggor body + smile, podium height, loudnorm); modal_song.py (ACE-Step theme songs with lyric QA); intro/outro song specs
- `bbd755b` story25d: camera lift for Kraggor wide shots
- `77b7ed7` story25d: shorter stands (sky visible), Kraggor rises from the real stands top line
- `cdc4da7` story25d: Kraggor head drawn behind the stands (front only for close-ups); scene tweaks
- `4a5eb5d` story25d: race tracking cam, finish line, Kraggor head/foot, ice cream toss, confetti, crown, cards, end card; S01E01 shot lists for all 15 scenes
- `eb54477` story25d: world centre CX=540 (shared drawing), stands banner per scene; voice QA: digits == number words
- `6202467` story25d v0: cinematic story scene renderer (shots, drama faces, lip flap, subtitles, sepia, two framings); S01E01 scene 2 + 5 shot lists
**🔧 Lain-lain**
- `93b1c95` trailer: exact air time on the end card, card held longer
- `e946e55` ledger: manual entry for timed-out YuE run; error log
- `ec0bcfa` drive_sync.upload: correct MIME for mp3/wav (Drive preview plays audio)
- `f21a6b8` S01E01 v3 approved; separate outro song (See You Next Time); Tilly & Nitro approved in CHARACTERS.md
- `996ddd0` S01E01 script v3: 15 mini-episodes with hooks, 3 training lessons, setups/payoffs, intro/outro + theme song lyrics (awaiting approval)
- `f2c712f` CHARACTERS.md: character bible (gender, personality, voice, catchphrase); Siren = female (user decision)
- `f3ca0a2` ERROR_LOG: untracked bot script blocked VM pull (excluded locally)
**📤 Upload / antrean / Drive**
- `2835fe7` publishing: long-form episodes (no #Shorts, own numbering 1000+) and trailer Shorts with a fixed extra slot; register_story.py
- `7ea2c3c` publish: daily run 2026-10-02 [cron daily_publish.sh]
**🎨 Branding**
- `c16eaae` branding: Infrasoft logo files
- `d227595` branding: YouTube Studio watermark (round mascot badge, transparent corners, 150/300 px)
- `2466f56` branding: transparent Infrasoft logo variants; long-video ident shows the logo (user approved proposal)
- `038611f` branding: no burned-in watermark (YouTube Studio branding), 'Produced by Infrasoft Media & Tech' credit in every description at upload
- `7fbe5c1` branding: play tip exits between gear teeth
- `9f56ea3` branding: Infrasoft logo generator (vector gear + play, Montserrat OFL)
<details><summary>otomatis VM (17)</summary>

- `0cb0626` records before lab fx
- `9e07d8e` records before lab fx
- `af3e2c3` analytics: daily report 2026-10-02
- `bfe572e` records before godot prototype
- `7596780` queue: Story Ep. 1 approved (story 1001) -> Sun 2026-10-04 13:00 ET
- `65fea3f` queue: S01E01 trailer approved (story 1501) -> Sat 2026-10-03 17:00 ET; Story Ep. 1 registered pending
- `fbdb8ba` music: intro remix3 (band x1.7) + ledger
- `347b392` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `6bb293b` music: intro remix2 (stereo, band louder) + ledger
- `ffdf6e3` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `ca705c0` music: intro v1 remix (band +) + ledger
- `eb7c66d` music: intro v4 candidates + ledger
- `26c1e54` music: YuE v1 intro candidates + ledger
- `37630ba` story: S01E01 draft v5 (drama pass) + voice ledger
- `45502d3` music: theme songs v2 (longer, remixed) + ledger
- `c2e2278` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `d55ac0a` music: intro + outro theme songs (ACE-Step) + ledger

</details>

## 2026-10-01
**🎙️ Suara / narasi**
- `20e0bc2` voice: S01E01 dialogue (ledger)
- `919f04f` voice: story test lines (ledger)
- `60c8cdc` voice: story test lines (ledger)
- `f68827c` voice: S01E01 character voice references (synthetic, en-US) + casting ledger
- `bc0c017` voice: S01E01 character voice references (synthetic, en-US) + casting ledger
- `8c7375b` voice: S01E01 character voice references (synthetic, en-US) + casting ledger
- `7db30f8` announcer: story character refs (branding/voice/characters) + drama emotion styles; S01E01 script v2 approved (15 scenes, MANY YEARS AGO caption)
- `71a6b75` Voice QA: letter-level match (made-up names pass), 2nd Modal round for failed takes; SMASH skips failed reaction lines, Edge only if a must-say line fails
- `2c11459` voice: QA'd voice C cache rebuild (ledger)
- `83c125e` voice: QA'd voice C cache rebuild (ledger)
- `289029a` voice: QA'd voice C cache rebuild (ledger)
- `ad8986e` Voice C QA: every take is transcribed (faster-whisper) and re-taken until it says the line; garbled takes never cached; READY... SET... GO! as one phrase with GO pop at the detected onset; duration limits 40-58 s
- `9639419` voice: READY-GO lines (ledger)
- `696e378` voice: narrator C lines for race/challenge test (ledger)
- `0006837` voice: Chatterbox duo announcer lines (ledger)
- `9064619` voice: synthetic announcer references m1 (male) + f1 (female) for Chatterbox
- `dec1620` voice: Chatterbox announcer module (cache, multi-speaker); smash25d: two commentators (m1 play-by-play, f1 colour), Edge fallback
- `31ee662` voice: Modal Chatterbox announcer sample (ledger) [Claude Code Opus]
- `15d370d` voice: Modal Chatterbox TTS sample generator with budget guard
**🔧 Lain-lain**
- `51d8cd1` S01E01 script v2: clear timeline (opening = flash-forward of race day, story starts one month earlier, 4-week training montage)
- `b72f633` Long-form slot -> Sunday 13:00 ET; S01E01 script draft 'Sprinkles' First Race' (awaiting user approval)
- `de165cc` SOP: user bot verifies daily at 14:00 WIB
- `260fd15` ERROR_LOG: dirty VM tree would block cron pull
- `8550bc6` daily_publish: commit leftover records before pulling (a stray plan run must not block the daily upload)
- `d7c82dd` AGENT_UPLOAD_SCHEDULER: official cron with daily_publish.sh
- `5c12e99` daily_publish.sh: the one cron/agent entry point for scheduled uploads (lock, stop on failed pull, plan, upload max 5, drive sync, push)
- `28ba7f3` STORY15_PLAN: decisions (2 aspect ratios, Part N replaces one slot/day alternating CHALLENGE/SMASH, first episode)
- `234e6c6` STORY15_PLAN.md: weekly 15-min story series plan (dracin 15x1-min scenes, cinematic, voiced characters, voice age rule); BLUEPRINT voice rules; tracker C9
- `08a8b29` drive_sync fetch: VM downloads an archived video on demand (no mount)
- `52307f3` SOP: Google Drive as the single review/archive location (drive_sync), producer + scheduler steps
- `0b35633` drive_sync: Google Drive API review/approved/archive flow (one place), hooks in approve/reject/mark_uploaded
- `2dc8b7e` Approve SMASH V4 S014 + S015 (user: layak tayang) + plan
- `b3fc129` Tracker: C13 random obstacles, C14 week-2 arenas, C15 story arcs; log
- `29baa42` Long-form gets its own slot (Sat 13:00 ET); Shorts keep 11/15/19 every day incl. Saturday SMASH
- `5abaa5e` Approve 6 CHALLENGE + 6 SMASH (user: semua layak tayang) + strict queue plan
- `642a709` Upload rule: 11 CHALLENGE / 15 RACE / 19 SMASH strictly (Sat 19 long > SMASH), 7-day stock check per type; docs
- `3217893` READY... SET... LET'S GO! (GO alone was garbled), Edge style for clear
- `1162859` reject: SMASH v3 x6 + CHALLENGE (Edge voice) x6 superseded by voice C versions
- `1551326` Spoken READY... GO! in CHALLENGE (before every level intro), RACE and SMASH; RACE end card fits the CTA
- `9914a4f` Narrator voice C for RACE + CHALLENGE (m1/f1 alternating, cache, one Modal call + restart, Edge fallback); studio vs arena FX; O(N) ducking in 2D
- `ccf6fe8` Approve race25d v2 S002-S007 (user: semua layak tayang) + queue plan
**📤 Upload / antrean / Drive**
- `fd1f7c3` publish_queue: UPLOADING marker before each upload + reconcile with the channel on the next run (no duplicate uploads after a crash); stop run on upload error
- `fb0bdc6` drive: first sync (videos placed in Drive review/approved/archive)
- `14131be` queue: long-form own slot; produce: 2 extra SMASH v4 (pending review) [Claude Code Opus]
- `fcaf326` publish_queue: slot roles (15:00 ET race25d daily, Sat 19:00 ET weekly long-form, 11/19 other Shorts) + standard warning; BLUEPRINT/agent docs; DEV_HISTORY v3.2
**🕳️ CHALLENGE (sim_engine)**
- `5272072` produce: SMASH v4 complete (6, voice C duo QA-checked) (pending review) [Claude Code Opus]
- `6232d86` produce: SMASH v4 x6 re-rendered with QA-checked voice C (pending review) [Claude Code Opus]
- `e733079` produce: CHALLENGE with narrator voice C + READY-GO hold (pending review) [Claude Code Opus]
- `d94d30d` CHALLENGE pacing window 44-57 s, level caps + READY-GO hold (voice C is slower)
- `0d60978` CHALLENGE: car holds on the line for spoken READY... GO! (GO pop on the spoken Go), RACE/SMASH GO pop synced; no empty pending folders on STOP
- `0660d06` produce: SMASH v4 x6 with voice C duo (pending review) [Claude Code Opus]
- `c49a081` sim_engine: import sys
- `c577238` produce: smash25d v3 batch complete (pending review) [Claude Code Opus]
- `3764485` produce: SMASH ARENA smash25d v3 batch (pending review) [Claude Code Opus]
- `3501aef` produce: SMASH ARENA smash25d v2 batch (pending review) [Claude Code Opus]
- `bcddf0f` produce: SMASH ARENA smash25d v1 batch (pending review) [Claude Code Opus]
- `47c139c` produce: CHALLENGE 2D batch lava/splash/potholes/bumps (pending review) [Claude Code Opus]
**📚 Dokumen**
- `0528ea1` Docs v3.9: voice C everywhere, READY-SET-LETS-GO, voice QA, ERROR_LOG
- `067b27a` Docs v3.8: Chatterbox announcer + SMASH duo commentators
- `bd2307d` Docs v3.7: SMASH v3 intros + winner showcase, fixes, ERROR_LOG
- `19d34b2` Docs v3.6: SMASH audio v2 analysis + fixes, ERROR_LOG
- `00f60e4` Docs v3.5: SMASH ARENA v2 (chaos + announcer), CHALLENGE batch, ERROR_LOG
- `8ad7731` Docs v3.4: dodge AI tuning results, ERROR_LOG (VM pull on dirty tree)
- `e8f5a70` Docs v3.3: daily lineup, hazard library, Smash Arena / Kraggor / league in tracker, ERROR_LOG
**💥 SMASH (smash25d)**
- `8988d83` smash25d engine v4
- `60de2e9` smash25d: v2 S001-S004 REJECTED (superseded by v3), v3 folders carry the version, crashed leftovers removed
- `297ce26` smash25d: last car can never be eliminated; render folders carry the engine version; episodes.reject avoids name collisions
- `75b3827` smash25d engine v3
- `8aea729` smash25d: drawn speed stars on fighter cards
- `cda6a72` smash25d: fighter introductions (spotlight, cards, calls) + winner showcase (spotlight, crown, hops, The winner is...)
- `645ff5d` smash25d v1 S001-S004 REJECTED (superseded by v2)
- `4de9e9a` smash25d engine v2
- `54f6cc3` smash25d: announcer scheduler (anchors + droppable calls), styled delivery, replay commentary, CTA fit, arena crowd mix, kaiju roar/steps, low engine
- `47975ad` smash25d: --dry-run seed search
- `1d60a58` smash25d: flip hysteresis (no thin-card flicker), Kraggor head further right
- `f9ef5be` smash25d: frame lower, bigger/lower UFO, one banner at a time (chaos first)
- `8537809` smash25d: chaos cut short by the winner stops drawing at its impact time
- `a11f55a` smash25d v2: wider arena, CHAOS (missile, KRAGGOR, UFO, lava crack), arena announcer narration
- `72686a7` smash25d: freeze after winner, closer camera, bigger HP bars; queue: 19:00 SMASH role with CHALLENGE fallback; docs
- `52bf37a` smash25d: tyre barriers until first shrink, push-only ring-outs, grinding damage, balanced mass
- `7d14b99` smash25d v1: SMASH ARENA generator (2.5D battle, last car standing)
**🏁 RACE (race25d)**
- `b1990a7` race25d/smash25d: O(N) moving average for narration ducking (np.convolve took minutes)
- `a8a7bde` race25d: blocked racers sprint past a level neighbour or brake behind one ahead
- `90b183a` race25d: blocked racers brake to tuck in behind the neighbour, look 40 m ahead
- `0d8afc2` race25d: agile racers always try to dodge, big vehicles only sometimes
- `392bc2b` race25d: dodge AI keeps looking for a gap (agility rolled once), 6 m clearance
- `adfc6ad` race25d: every hazard set has a dodgeable ground hazard, higher agility; docs v3.4
- `e3580ee` race25d engine v2 (hazard library, dodge AI, YouTube end card)
- `0e72e62` race25d: end card sits below the winner title
- `2e5e060` race25d: log dodges
- `66716a1` race25d v3.4: lane-change dodge AI, YouTube-style LIKE/SUBSCRIBE end card
- `2ab0056` race25d: camera frames car + dragon together
- `72c3d18` race25d: dragon hovers close to its target so it is always in frame
- `5897f89` race25d: laser zap sound overlays arrays of different length
- `c65a8c2` race25d: hazard library (pothole, lava, wall, crusher squash, laser split, meteor, UFO, fire dragon tire change, ice dragon freeze) + per-hazard sfx/narration/replay
- `caa304f` race25d: hard cuts on scene change, key car always in frame, check: no frame without a car
<details><summary>otomatis VM (2)</summary>

- `a329be8` records: queue/index after reconcile test
- `d338b29` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine

</details>

## 2026-09-30
**🏁 RACE (race25d)**
- `23216e2` race25d v2 S002-S007 rendered (pending approval)
- `6527b6b` race25d v1 S002-S007 REJECTED (superseded by engine v2)
- `7fff27c` race25d in smoke test, BLUEPRINT, producer guide, DEV_HISTORY v3.1, PROJECT_PROGRESS
- `6b9294e` race25d: camera keeps the winner in frame at the finish and centres the jumper
- `40cc568` race25d: registry._active needs exclude_id
- `d5680e6` race25d: full 2.5D Shorts series generator (seed variety, rotation, narration, synth audio, replay, CTA, checks, registry)
- `6a8243b` lanes25d: road wider than screen, zoom floor, tighter pack, scene lifted mid-frame, foreground bushes, bubbles follow zoom
- `e42b573` lanes25d: stronger depth (higher camera, wider lane spread), pack-fitting camera with zoom-out, bubbles above cars
- `ce0b10c` lanes25d: 2.5D paper-cutout race prototype reusing the exact 2D cast drawings (lanes, parallax, cross-lane hydroplane spin, jump)
**🕳️ CHALLENGE (sim_engine)**
- `4e36618` produce: SIM_RACE25D_V1_S003-S007 (pending review) [Claude Code Opus]
- `e0e072e` produce: SIM_RACE25D_V1_S002 re-render, camera fix, 0 empty frames (pending review) [Claude Code Opus]
- `4b7c460` produce: SIM_RACE25D_V1_S001 (pending review) [Claude Code Opus]
**📤 Upload / antrean / Drive**
- `58266c9` publish: re-plan with slot roles (Ep. 9 race25d at 15:00 ET)
- `b636605` publish: re-plan queue in episode order (Ep. 1 before Ep. 7-8)
- `5ec0e4a` publish_queue: re-slot all QUEUED items in episode order; git_sync push lists staged files; docs
- `3c1143b` episodes: pending/approve/publish workflow, clean start, first Arena batch
**🔧 Lain-lain**
- `c7325e0` approve: SIM_RACE25D_V1_S001 -> Ep. 9 (user: siap tayang)
- `495bd77` PROJECT_PROGRESS: 2.5D approved; C1c arena/camera variations, C9 weekly story format
- `51aa2b5` PROJECT_PROGRESS: C1 new direction 2.5D paper-cutout (3D on hold)
- `ec32f94` DEV_HISTORY v3.0 (3D mode: Blender + Modal, cast3d, director3d stage 1); PROJECT_PROGRESS C5
- `cbbd243` modal: director3d demo render logged (900 frames h+v, 8x L4, 0.235 USD)
- `0874de3` director3d: follow cams aim at the real pack centre (ignore stragglers), steeper vertical cam
- `ec2ca83` director3d: motion (race sim -> smooth 30fps motion + follow cams), Blender scene builder, Modal renderer; cast3d wheel pivots + spokes
- `bcac23d` PROJECT_PROGRESS: C1b cast v2 fixes done
- `aba051e` cast3d: centred bigger eyes, visible smile with tongue, Sprinkles cone in a roof holder; frontal preview camera
- `abbd0da` PROJECT_PROGRESS: C1b more cartoon 3D cast (user review of cast3d v1)
- `8e6011d` PROJECT_PROGRESS: weekly 3D plan + Modal cost math (C4); ERROR_LOG: PowerShell $ in commit message
- `b94304c` modal: first GPU benchmark logged (90 frames, 3x L4, $0.032)
- `5220544` Blender CPU benchmark results (PROJECT_PROGRESS C1); ERROR_LOG: VM is arm64
- `95de2ce` .gitignore: venv-modal/ (Modal client venv)
- `02a51ba` git_sync.sh: status always exits 0 (informational)
- `384725f` PC clone workflow (PC -> GitHub -> VM); ERROR_LOG: Google Drive stale index lock, inline ssh quoting
- `a3f534f` git_sync.sh: author email mu.aliwardana@gmail.com
- `5420a9d` git_sync.sh: single git workflow VM 99.3 <-> GitHub
- `393c385` v2.9: no-replay level variants (pacing), test_all.sh smoke test, top-down pseudo-3D prototype
- `ea358b4` EPISODES_INDEX.md: auto identity card per episode for agents; per-model notes
- `bf2a29f` PROJECT_PROGRESS.md: shared task/progress tracker for all agents
- `8578205` Agent video producer guide + PRODUCTION_LOG (history tracking)
- `61906a9` Approve Ep. 7-8 (splash s007, lava s003); agent upload scheduler guide for VM 99.2
- `7ed3758` v2.8: distinct water/lava audio, melting cars, hydroplaning spins, publish queue
- `8dc6df6` v2.7: Splash Zone + Lava Road series, flexible champions, theme rotation, hazard SFX
- `d7ee5b2` v2.6 anti-monotony: environment themes, rotating en-US narrator, clearer audio
- `f6b5dfd` rebrand: MegaWheel Kids -> MegaWheel Arena (all-ages), adult female narrator
- `06e5995` cast: 10 characters (Nitro, Tilly, Titan, Sprinkles) + role fallback, banner update
- `5de420c` MegaWheel Kids video engine: physics_2d generator merged into video-engine
**🧪 Lab (eksperimen)**
- `ae90e07` blender3d: procedural 3D models of the 10-character cast (cast3d.py); Modal budget cap 29 USD
- `2f2ec30` blender3d: animated benchmark scene (fixed lighting/orientation/camera) + Modal GPU renderer with monthly budget guard
- `52cc5a8` blender3d: benchmark scene (Kenney CC0 cars, road, puddle, sky) + asset fetch script; ignore assets/
**📚 Dokumen**
- `aa7b598` docs(channel): Film & Animation category, banned tags, upload defaults
- `60844b5` docs: ERROR_LOG.md with every mistake so far and how to prevent it
- `9b2b3e1` docs(blueprint): add GitHub repo and commit/push workflow
- `21f7f67` docs: record permanent cleanup after the merge
**🎨 Branding**
- `83e9c43` branding: YouTube profile picture, banner and channel setup guide
