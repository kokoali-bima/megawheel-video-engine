# CHANGELOG — MegaWheel Arena video engine

Dibuat otomatis oleh `tools/make_changelog.py` dari riwayat git (terbaru di atas). Setelan terbaik yang
berlaku: **CONFIG_BEST.md**. Kesalahan & pelajaran: **ERROR_LOG.md**.

## 2026-10-10
**📤 Upload / antrean / Drive**
- `8e312a3` publish: daily run 2026-10-10 [cron daily_publish.sh]

## 2026-10-09
**🔧 Lain-lain**
- `310dc90` uploader: add youtube.force-ssl scope (metadata updates on own videos)
**📤 Upload / antrean / Drive**
- `a084217` publish: daily run 2026-10-09 [cron daily_publish.sh]
<details><summary>otomatis VM (1)</summary>

- `3ac9b1f` analytics: daily report 2026-10-09

</details>

## 2026-10-08
**🔧 Lain-lain**
- `bfd0498` RESEARCH_CHANNEL2: niche scan + recommendation (3D engineering explainers, US)
- `9369f08` niche_scan.py: read-only niche research (demand, competition, young/small-channel outliers)
- `cf857f0` feat: record audited Race 3D review
- `feaed78` fix: replay Race 3D from manifest timeline
- `a6522f8` fix: preserve Race 3D voice cache restart args
- `878e54b` fix: resume Race 3D exporter after voice cache
- `94233d9` fix: watchdog Modal TTS and targeted smoke tests
- `7334860` auto: records left uncommitted before daily run
- `19df8ac` ops: refresh episode indexes
**🕳️ CHALLENGE (sim_engine)**
- `ddaba80` produce: SIM_RACE25D_V4_S047 (pending review) [Claude Code Opus]
**📤 Upload / antrean / Drive**
- `9a32ff0` publish: daily run 2026-10-08 [cron daily_publish.sh]
<details><summary>otomatis VM (1)</summary>

- `fc41fdd` analytics: daily report 2026-10-08

</details>

## 2026-10-07
**🔧 Lain-lain**
- `a34f805` approve Ep. 52 dungeon + queue plan
- `7fd3bbd` tracker #53 black dot
- `78febd3` godot3d: hide idle smoke/fire/spray emitters (parked particles drew a black disc on the car)
- `b822710` godot3d: clear smoke/fire particles on a new level (black dot on the next car)
- `7f552a3` audit: size window 8-35 MB for 3D (render3d) videos
- `e481521` Handover: dungeon series done, S015 pending review; tracker #52; AGENTS section 9
- `f89db9a` godot3d dungeon: stone cross-section, darker lava, brighter axe blade
- `fadb04d` dungeon: ramp+lava pit earlier (melt signature mandatory like the lava series)
- `d1a8813` dungeon: signature = axe/ogre crash or lava plunge
- `ddf0a59` dungeon: first hazard later
- `2ca5e1f` dungeon: less lethal axes/ogre windows
- `c050558` tune_dungeon.py
- `18d5e98` Handover: CH01 v3
- `629100f` Crumple pass recorded once; G04 allows intentional jump/fling/sink
- `981fed2` Save history/tracking: challenge handover, tracker #42-47, error log, contract H01, resume prompt
- `3d778e8` register_story: --only-trailer
- `6aa88f3` Trailer metadata + register_story --trailer-video (pending)
- `c12bfc9` trailer: duck the score under the narrator (sidechain)
- `d310482` trailer: fade the second cue before delaying it (it faded out the moment it started)
- `b572e2e` trailer: audible score bed
- `3f3c380` trailer: captions fit the width
- `ba9c01e` trailer: setsar=1 (concat refused a 5120:5121 SAR)
- `7a48558` thumbnail art: open eyes
- `6712a91` thumbnail art: layout
- `dd6aef9` Thumbnail artwork tool (drawn with the real character drawings)
- `6af38f7` Trailer Short tool (9:16, cut from the finished scenes)
- `b31fc00` S01E02 publishing pack (US English)
- `fb38f3f` thumbnail: crop the letterbox, badge position, Kraggor face frame
- `c336c6d` S01E02 publish metadata (US English) + thumbnail tool
- `cb4ede7` Scene 10: quieter Kraggor hum after each narrated sentence (masking)
- `e3bea95` Scene 10: the narrator tells what Kraggor's chalk drawings show (voice + subtitle), Kraggor's hum as the reaction after each sentence
- `008c7b2` AGENTS/HANDOVER: ledger self-heal indicator, bookends procedure, 2026-10-07 owner notes
- `b222cb9` bookends: audible, silence-free score bed under the recap narration
- `1954ac9` assemble: lossless (pcm/mkv) intermediate pieces, AAC once at the end (no piece-boundary gaps, no cumulative A/V drift), tracker #40
- `13c8651` bookends: recap clip B without the aired caption box
- `a4dbed7` bookends: crop the recap clear of the aired subtitles
- `27fc1c0` Bookends: ident + theme (aired Ep.1), Previously recap, outro with the S01E02 teaser; assembler skips the PART card for scenes marked no_card
- `9037086` Owner notes 2026-10-07: net fitted to Kraggor and drawn behind the cars, Kraggor silhouette option (ghost), Kraggor's own hum voice for his story (no bell tones), dry cave air; git_sync ledger self-heal + indicator, produce commits the ledger
- `abedd17` HANDOVER: scenes 9-15 delivered, engine added, pitfalls
- `338071c` Scene 15: audible wind ambience and a quicker music entry (opening was -39 dB after the party)
- `97f6de2` Join card on every scene join (J04), longer tail on scene 11's last line, tracker #39
- `1738723` Scenes 9-15 review fixes: tonal arm_slide instead of whoosh (A07), Kraggor head visible in wide shots, rope net, sign visible on the speedgate, two-shots in scene 15 (C11), A01 gap in scene 9
- `89fbf2c` S01E02 scenes 9-15 (face to face, Kraggor's story, town gate, trap, stand up, party, old key) + props to_shot
**🧪 Lab (eksperimen)**
- `4be98fb` lab godot3d_challenge: dungeon hall, 3D axes, ogre, crushed car; exporter sends axes/ogres/crush
- `697be65` Godot: no z-fighting snow caps, bigger stars (sparkling peaks / shimmering night sky), tracker #41
**🕳️ CHALLENGE (sim_engine)**
- `393c821` sim_engine: new CHALLENGE series 'dungeon' (axes, ogre, ramp + lava pit) with physics, drawing and sounds
- `b77946d` Challenge handover: new direction (follow aired sim_engine format), evaluation + plan
- `fbaa432` CHALLENGE: course like earlier challenges (ramp 6 m / pit 8 m, ~120 m), no J-cut over the crash
- `e0105c3` CHALLENGE: announcer after the crash sounds settle
- `ecdd2f8` CHALLENGE: result lines lead after the crash; longer cold open
- `3984cac` CHALLENGE v4: 124 m course, launch ramp + jump over the lava pit, three axes, ogre
- `6e7def9` CHALLENGE: fail badge after the impact word; tracker rows 48-51
- `58594e5` CHALLENGE: wider lava stripe, bigger ogre, closer run camera
- `a796629` CHALLENGE: lava pit as a floor stripe, car sinks behind the near rim, hop allowed in G04
- `50fd1a5` CHALLENGE v3: Mario-style gauntlet (axe, lava pit, ogre), fast cars, BeamNG-style crumple/debris/launch, impacts + shake
- `3274df7` CHALLENGE axes: floor under the 9:16 camera, axe that reads as an axe, brighter dungeon, music on the fail runs + win only
- `160f907` CHALLENGE: NEW 3D GRAPHICS tag in the cold open; music spotted on the runs and the win only (A10)
- `451d155` CHALLENGE Short on story3d (vertical): dungeon location, chopping axes (cairo, simulated outcomes), CHALLENGE HUD, new SFX, vertical Godot resolution + QA sample aspect; scene generator for 'Cars VS Dungeon Axes'
**📤 Upload / antrean / Drive**
- `0f733f2` publish: trailer Ep. 1502 moved to Wed 2026-10-07 08:00 ET (owner: it should air right away) [Claude Sonnet 5.5]
- `97709e8` publish: Ep. 1002 thumbnail swapped to the custom artwork; trailer Ep. 1502 approved by the owner 2026-10-07 and queued [Claude Sonnet 5.5]
- `e3c444f` publish: Ep. 2 trailer Short registered as PENDING (review), thumbnail artwork ready [Claude Sonnet 5.5]
- `efb8757` publish: Ep. 1002 (Who Is Kraggor?) approved by the owner 2026-10-07 and queued for Sun 2026-10-11 13:00 ET [Claude Sonnet 5.5]
- `ba22cab` Publishing: register story3d episodes from publish.json (title/description/tags/language/thumbnail), optional custom thumbnail on upload (never fails the upload)
<details><summary>otomatis VM (42)</summary>

- `06d413f` records: modal usage
- `6af5dc7` records: dungeon S015 3D redo (no black dot)
- `3f7ede8` records: dungeon S015 convert redo
- `d577d35` records: dungeon S015 audit (3D size window)
- `7610697` records: dungeon S015 (pending) + 3D convert
- `fdbe5e1` records: modal usage (auto)
- `16c04a3` records: modal usage (auto)
- `0f869e5` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `c6c1f46` records: modal usage (auto)
- `f1f6637` records: modal usage
- `f6591b2` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `a65bbd7` records: modal usage
- `b060492` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `8689a22` records: modal usage
- `3a463bb` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `3ca22fb` records: modal usage
- `f32a768` analytics: daily report 2026-10-07
- `2c12a82` records before analytics
- `3151544` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `2808823` records: modal usage
- `25d844d` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `5cbcc77` records: modal usage
- `fbd9fe7` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `ed4bbe3` records: modal usage
- `baffaf1` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `e5744b4` records: modal usage
- `ca54771` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `13330c4` records: modal usage
- `d07ee56` records: modal usage
- `27d1744` records: modal usage
- `50edf78` records: modal usage (auto)
- `0c901f3` records: modal usage (auto)
- `fd4d869` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `3116683` records: modal usage (auto)
- `480e30f` records: modal usage
- `1da145d` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `23e5ef4` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `80bdeef` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `acbe52e` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `036d8a3` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `b59d70a` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `44aa02b` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine

</details>

## 2026-10-06
**🔧 Lain-lain**
- `196e190` Scenes 2,3,5,7: fill the A01 gap in scene 3, move the sting off the line, lower memory/drone levels
- `f0e71e9` Scenes 2-3: re-apply the A10 spotting (an earlier copy restored the old scores) + A01 gap fixes
- `879a956` Scenes 2,3,5,7: fix A01 gaps after the A10 respot (nervous honk, theme cue from shot 3) and masking levels
- `15067d2` A10 music standard (silence is part of the score: <=60% of shots, gain 0.24, duck 0.75, sensors + lint), scenes 2-8 respotted; engine for scenes 9-15 (claw, chalk, net, sad Kraggor, SFX, wind, Godot towers/party lights/speedgate/ruins) UNTESTED on Godot
- `dbd79d6` HANDOVER: scenes 5-8 delivered, engine added, next 9-15
- `1cf43d7` assemble: join fade-out curve cub (qsin ends too steeply in dB on loud ambience), tracker #37
- `6ee5e0b` Scene 5: let the final thunder end before the fade-out (join 5->6 drop sensor), tracker #37
- `30c795e` Scenes 5-8 review fixes: cone in front of the baby head, brighter forest/mountain/cave, no moon dot on the mountain road, sign text fit, scene 6 framing, sfx gain + music levels; contract A09/L02/K02, tracker #34-36
- `4d09629` S01E02 scenes 5-8 (flashback, plan, mountain road, cave) + shot-relative lightning + modal smoke test (short Godot render of new world code)
- `9bb582d` Merge main into wip-scenes-5-8
- `05f2c99` story3d engine for scenes 5-8: little Kraggor (baby head, world-anchored prop), tonal thunder/rockslide/munch/whimper/snore/drip/key/breath SFX, storm + cave ambience, one-shot sepia grade in compose, cave tint, linter vocabulary
- `4ae6b57` RESUME_PROMPT.md (paste-in prompt for a new session), tracker #29-33, HANDOVER: episode cards instead of ads
- `a7e3f06` Merge remote-tracking branch 'origin/main'
- `e7ac2ca` assemble: do not shadow the scenes folder variable with the card fade width
- `afa2936` J03: dracin-style episode card on every time-jump join (fade out 1.0, black hold 1.8 with 'PART N' + chapter title and a soft bell, fade in 1.2); contract-driven (label, hold, chime) so it is also where mid-roll ads can go later
- `e6afe3d` HANDOVER: scenes 5-8 Godot code lives on branch wip-scenes-5-8 (untested)
- `ffbeebe` WIP (untested): story3d Godot locations for scenes 5-8 - forest storm (rain, lightning), mountain road + rockslide, cave (crystals, treasure, sign, key, moonbeam), mountain backdrop. Kept off main until a short Godot render passes.
- `d28c050` Merge remote-tracking branch 'origin/main'
- `66288c3` S01E02 HANDOVER.md (resume point for a new session: decisions, status, in-progress, commands, pitfalls) + safe stop script in the repo
- `adf86ad` scene 4 album insert pushes in on the torn photo; framing sensor skips inserts (off-screen voice)
- `b901a0e` script: album + torn mountain photo continuity (K01, tear seed 7)
- `45a1d4d` mountain photo: little Kraggor's tail sweeps past the tear (tip = the hint on the album side, rest on the sc.13 piece)
- `8aeb26b` Merge remote-tracking branch 'origin/main'
- `fa5f536` mountain photo: little Kraggor stands closer to the tear so his tail tip shows on the album side
- `a9bf69c` continuity K01: the Ep.1 wall photo stays as aired (no tear/tail; linter guards it); Grandpa's album with old prints (town, with Little Sprinkles) and a NEW torn mountain photo whose tear comes from a seed - the scene 13 piece (photo_piece, little Kraggor from his real drawing, mirrored so his tail crosses the tear) fits exactly; scene 4 uses the album
- `63ece83` Merge remote-tracking branch 'origin/main'
- `b665545` C11 counts character dialogue only (narrator excluded) and leaves inserts out of the time base
- `b944a92` Merge remote-tracking branch 'origin/main'
- `1b0988e` scene 4: tail sized to the photo and tucked at the tear, lamp shot framed higher; inserts are their own shot type (sensor = linter)
- `2d00e6e` scene 4 self-review: inserts clear of Sprinkles, slim spiked green tail on the torn photo, lamp shot framed above her roof sign, memory swell bridges into the flashback, silent reaction removed (cut rate)
- `2379921` smoke preflight: story25d SMOKE draws ~3 frames/s + every shot in memory without encoding; produce_story3d runs it on the VM after prepare (a crash in new drawing code now stops in seconds, not in the cloud); sketch text stroke fixed
- `d977efb` Merge remote-tracking branch 'origin/main'
- `13ea84c` story3d Modal mounts all of branding/voice (the narrator's announcer_ref.wav was missing: scene 4 overlay crashed on the first narrator line)
- `931c1dd` Merge remote-tracking branch 'origin/main'
- `772cee3` produce_story3d: unbuffered live Modal log + watchdog (no overlay progress in 6 min = kill and retry once; the Modal client hung three times after 'Created objects')
- `e2dd61f` story3d garage interior (plank walls, shelves, workbench, night window, warm interior light), hanging lamp with sway + light cone + dust motes, falling crate with dust puff, torn photo with a green tail (sc.13 payoff), pencil sketch of little Kraggor signed K., box_drop SFX, room tone without hiss, props with from_shot, warm indoor tint; S01E02 scene 4
- `3f9e214` Merge remote-tracking branch 'origin/main'
- `4ca0540` C09-C11 (research: close-ups sparingly, staging in depth): max 2 marked close-ups per dialogue scene, no wide->close jumps (push in instead), QA wide-share; G04 nothing floats: platform_h (stage + ramps) lifts cars automatically, linter forbids fixed h, QA flags cars in the air; Godot stage ramps; scenes 2-3 re-cut without cut-in close-ups
- `e9829af` Merge remote-tracking branch 'origin/main'
- `d74513c` linter: exact vehicle body table (same on every machine) and eased move timing (x1.5) - the QA real-position check found a 1.0 m gap the linter had estimated at 1.9 m; scene 3 Sprinkles arrives in time
- `15fc511` Merge remote-tracking branch 'origin/main'
- `3c51afb` C08: a car's move must end inside its shot (linter; exits hidden next are fine) + QA bumper check on the real per-frame positions; scene 3: Sprinkles arrives in time, her theme covers the hush, brighter spotlight
- `97a3973` Merge remote-tracking branch 'origin/main'
- `86232c3` story3d arena location (stepped grandstand, roof, catch fence, banner, floodlights lit at sunset without shadows, far skyline), stage + spotlight props (world dims for a lonely spotlight moment); honk_cheer with only two horn types (A08); S01E02 scene 3 'The Town Meeting'; linter times = engine themes
- `11a5c8a` scene 1: tension drone enters after 'Huh? What was that?' (QA masking warning from the previous pass)
- `6009c28` honk_cheer registered lazily (defined after the SFX table)
- `f32a9e3` Merge remote-tracking branch 'origin/main'
- `b6dd9ce` A07: no noise-based crowd effects in story3d (cheer/laugh banned by the linter; QA warns on any noise-like effect); town cheers with 'honk_cheer' (cars honking, clean tones); near-stomp debris band-limited
- `870d2af` Merge remote-tracking branch 'origin/main'
- `40ca4fb` tracker #25-28 linked to STYLE_CONTRACT rules
- `486d7af` Merge remote-tracking branch 'origin/main'
- `198e8d0` held joins: explicit qsin fade-out of the old scene's sound into the black and fade-in of the new one (the crossfade into the black clip cut the sound: -20 -> -57 dB in 0.1 s, measured)
- `408690f` Merge remote-tracking branch 'origin/main'
- `bb1d095` self-review fixes: drone/lamp/far-thud carry phone-band energy, black hold has soft room tone (no digital silence), join drop measured at the audible floor; scene 2 hook cue under Zippy
- `b4085a4` Merge remote-tracking branch 'origin/main'
- `f6ba38e` STYLE_CONTRACT: one numbered rule book from every owner review (linter, QA, assembler and engine read it; golden scenes re-linted every run). J-cuts 0.45 s in dialogue (C04), jump-cut rule (C06), cut-rate/ASL sensor (C05), empty-silence sensor (A01) + drone/thud_far tension SFX, time-jump joins = fade out / hold on black / fade in (J01); scene 1 tension bed before the footprints; scene 2 music bed without holes
- `23b550f` Merge remote-tracking branch 'origin/main'
- `516f1e5` linter: a car inside the barricade is rejected; scene 2 staging tightened (gaps kept), barricade/Siren moved clear of Zippy
- `fbe3dc7` Merge remote-tracking branch 'origin/main'
- `40ab8dd` linter: cars bumper-to-bumper in a talking shot are rejected (reads as a traffic jam); scene 2 re-staged with gaps and depth
- `752efd2` film coverage instead of talking heads (owner 2026-10-06): cam 'group' frames the exchange and leans slowly toward the speaker, several lines per shot, listeners' eyes follow the speaker; linter rules (no close-up ping-pong, <=50% lines in single close-ups, group/two shot with >=2 lines); scene 2 re-blocked (three-shot exchange, walk-and-talk entrance, comic ECU + silent reaction); AGENTS/SOP updated
- `625c8b4` SOP_STORY3D §7: episode assembly, join rule, join sensors, lesson (quiet scene openings)
- `b58ce8b` joins: FAIL on abrupt sound cuts / holes / same-place steps, WARN on big steps across a time jump; scene 2 opens on a soft morning cue (wonder) that hands over to the panic cue
- `31d25c1` Merge remote-tracking branch 'origin/main'
- `7c8a16b` assemble: plain floats in the join report (no numpy in the local modal env)
- `dbf5693` story3d: smooth episode assembly on Modal (assemble entrypoint): join rule from scene JSON (time/location change = fade through black 1.0 s, same place = dissolve 0.6 s, edit.json overrides), audio cross-fade, join sensors (loudness step, silence hole), chapters; compose keeps the latest final of every scene in the volume
- `ea7947d` Merge remote-tracking branch 'origin/main'
- `c3c0d6f` story3d barricade spans ACROSS the road (kerb to kerb, slightly diagonal, two striped rails, 3 posts, blinking lamps) with the DANGER sign on the far end facing the camera (owner review scene 2)
- `423d86f` Merge remote-tracking branch 'origin/main'
- `05b3df1` model-agnostic standard: AGENTS.md (one manual for Claude/Gemini/OpenAI/DeepSeek/Kimi; GEMINI.md + CLAUDE.md point to it), validate_scene linter (invented keys/values, unknown cams/moves/sfx/cues/emotions, voiceless speakers, occluded speaker, variety, monotonous score, crickets in town, long lines) wired into produce_story3d preflight, TASK_CARD paste-in prompt; tracker #15-24; barricade sign text fits
- `28d41de` Merge remote-tracking branch 'origin/main'
- `db53646` car lettering readable on left-facing cars (story3d only, flag TEXT_UNMIRROR; Shorts unchanged)
- `f8e985b` story3d QA round 2: auto cut rule (big reframe = clean cut, small = slow glide; the 1 s 20 m swoops), no anisotropic low-cam stretch in 3D (283 px), sfx timed after the line ('end+0.1'), day breeze without hiss, hiss sensor = noise-like high band (flatness) not birdsong, jumps measured on the world layer; scene 2: Zippy/Siren/barricade spaced so nobody is parked in front of the speaker, panic cue under the voices
- `cfe92eb` Merge remote-tracking branch 'origin/main'
- `ae88d26` produce_story3d: live Modal log file + 90 min timeout
- `bc6336a` story3d calibration on the approved scene 1: camera sensor measures on-screen motion of the actor plane (shake/punch exempt), contrast threshold 1.15, two-pass loudnorm (was -18.3 LUFS), benign headless Vulkan lines filtered; heartbeat gets a phone-audible knock, near stomp less sub
- `e8fc276` story3d: lip-sync in the cloud - rhubarb 1.13.0 x86 (official release, same version as the VM build) in the Modal render image, cache in the Modal volume; prepare on the VM = voices only (the VM no longer needs x86)
- `f337a0b` Merge remote-tracking branch 'origin/main'
- `9a1d5f4` story3d: day look (sky, sun behind camera with soft short shadows, pastel town, shop row with signs, lamps/headlights off by day), timed props (from_shot/to_shot), barricade prop with blinking lamps; S01E02 scene 2 'Town Panic' shot list; SOP_STORY3D (standard command, scene rules, sensors, fix playbook)
- `8f23418` fix(upload): add en-US defaultLanguage to force US audience
- `25d515e` story3d: production package for option C (promoted from lab/godot_story): export_overlay (characters, shot table, all-actor records, cloud gates: voices/lip-sync/font must be prepared), modal_story3d (overlay CPU + Godot T4 + compose, all scenes/parts parallel, volume), audit_story3d (camera smoothness, Godot/cairo reprojection, grounding, focus occlusion, variety, light/contrast/shadow, hiss/dead air/masking/phone band/music monotony, LUFS, reveal), produce_story3d (standard command + exit codes); story25d: prepare-only mode, audio stems for QA, honk SFX
- `523b81f` Merge remote-tracking branch 'origin/main'
- `1f4c1de` S01E02 script v1 (draft for user review): 15 scenes, setups/payoffs, ad-break points, Godot location list, Modal render plan
- `8699c31` Merge remote-tracking branch 'origin/main'
- `ef0c7f6` stomp_near: pad layers to the same length; stronger boom body
- `aea9945` Ep.2 pilot v7: Godot roll sign fixed (car floated in the dutch shot: road and car tilted opposite ways); subtitles page long lines (only the last 2 lines showed - the song's first words never appeared; '|' + page times for songs); city-night bed without hiss, softer lamp-off, Kraggor steps audible on phone speakers (boom body + crunch, not only < 200 Hz)
- `ec41b0a` Merge remote-tracking branch 'origin/main'
- `87d045f` Ep.2 research: v6 results + lessons (after_sky in exporters, fog-free distant silhouettes, 2.5D sink)
- `76b2e27` Merge remote-tracking branch 'origin/main'
- `77c6da5` far Kraggor: 2.5D sinks his legs below the low skyline (upper body + head over the town); exporter calls after_sky so Godot gets the far-Kraggor sprite
- `e17e7ab` Merge remote-tracking branch 'origin/main'
- `89dfc22` Ep.2 research §9: floating-car root cause, whistling-in-the-dark song research, score spotting, singing VC, far Kraggor
- `c95e60d` Merge remote-tracking branch 'origin/main'
**🧪 Lab (eksperimen)**
- `2d0f00a` Godot: giant fog-free mountains (visible over the town), storm hides moon/stars, smaller Grandpa sign text; contact_sheet tool
- `21ef9aa` Godot far Kraggor: visible only in the frames of his shot (was standing behind the town from shot 3 on, spoiling the reveal)
- `a4bbb3d` Godot far Kraggor: fog-free materials (78 m of volumetric fog hid him completely)
- `ac6a492` lab singvc: return plain floats (local modal env has no numpy)
- `67e055e` lab singvc: pin protobuf >= 4.25 last (Modal runtime crash-loop with the funasr/modelscope protobuf)
**📤 Upload / antrean / Drive**
- `a2e5328` publish: daily run 2026-10-06 [cron daily_publish.sh]
**🎬 Story / episode panjang**
- `ec128d0` story25d: sung line lead-in (6th field: seconds heard over the previous shot); Ep.2 cold open uses Tilly's song in her own voice (Seed-VC take alt1: doo-doo intro under the establishing shot, cut after 'Not me!')
<details><summary>otomatis VM (40)</summary>

- `bd9b0df` records: modal usage
- `6542c6e` records: modal usage
- `336b82c` records: modal usage (auto)
- `19e1bf5` records: modal usage
- `294915e` records: modal usage (auto)
- `446574f` records: modal usage
- `2f9104a` records: modal usage
- `c194112` records: modal usage
- `d648975` records: modal usage
- `f41a439` records: modal usage
- `9962c52` records: modal usage
- `e5f51f9` records: modal usage
- `5ced06d` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `b237160` records: modal usage (smoke)
- `00f8fed` records: modal usage S01E02 scenes 5-8 (reconstructed)
- `7a88507` records
- `af80a3a` records
- `790bdf4` records
- `8339306` records
- `93c1249` records
- `4de8ba5` records
- `a6508d9` records
- `f568d78` analytics: daily report 2026-10-06
- `9eae5e5` records before analytics
- `f9df5fd` records
- `09843e5` records
- `59802bb` records
- `737f894` records
- `c678c59` records
- `5ef4bdb` records
- `be9125d` records
- `fbf354e` records
- `e2d0cc0` records
- `ceecec6` records
- `a001132` records
- `e98adab` records
- `db472ff` records
- `f2cf38d` records
- `2c67116` records
- `5f5d925` records

</details>

## 2026-10-05
**🔧 Lain-lain**
- `d823526` Merge remote-tracking branch 'origin/main'
- `8fda0c5` Ep.2 pilot v6: footprints flat along the road (5.5x3 m, staggered) + car contact shadow (the car looked like floating over the Godot road); far Kraggor silhouette in world space behind the town (kraggor_far: cairo after the sky, Godot sprite of the real drawing between building rows + glowing eyes + haze); score only from the footprint reveal; new Tilly song spec + lab Seed-VC singing conversion to her real voice
- `1740527` pilot A v5: Tilly sings (ACE-Step, ukulele) and the song cuts on the first dying lamp; city-night ambience; far footsteps in the dark before the eyes, near stomp at the end; real Kraggor head silhouette; pilot C: Kraggor drawn by story25d, Godot adds the glow
- `93a3611` pilot C test 2: skyline pushed back (55-130 m), sparser dimmer windows, thicker volumetric fog, stronger lamp/headlight fog energy, trees away from lamps, eyes in front of the skyline
- `09c7ebc` upload_sample.py: --folder= for Drive lab subfolders
- `91c3f91` pilot A v4: Tilly stops so her headlight pool lands on the first footprint; reveal frames car + prints
- `ddd45df` pilot A v2: footprints readable at night (cracked moonlit rim, bigger, stronger steam), Kraggor eyes bigger with a head silhouette, lighter fog, reveal shot frames the prints
- `49323e9` S01E02 research & production plan: music cue library + spotting, camera moves, expressive voice (Chatterbox-Turbo / Dia), 3D cost path, legendary hook recipe
- `9c71599` swap: Ep. 34/43/46 <- RACE v4 S045/S044/S046 (user 2026-10-05 approved)
**🎬 Story / episode panjang**
- `20aa03a` story25d: city-night ambience (no crickets in town, quieter crickets in the country), Kraggor footsteps (far steps closing in + near stomp), Kraggor's real head as the dark fog silhouette, sung lines from a wav (cut on a beat); Tilly song spec; Godot: no moon shadows at night
- `7336281` story25d: night headlight beams (air cone + road pool), flicker per shot as Kraggor's danger sign; pilot A uses them (beam reveals the footprints, flicker when the eyes open)
- `92219be` story25d: cue-library score with spotting (silence allowed, stings), lamp_off sfx, scared/angry voice styles; S01E02 scene 1 cold open (pilot A)
- `fa9dd2c` story25d: in-shot camera moves (push, pull reveal, pan, crane, dutch, handheld), street lamps that die one by one, steaming footprints, night fog; S01E02 cue library spec (ACE-Step instrumental)
**🧪 Lab (eksperimen)**
- `a0c9fc7` lab pilot C: story scene world in Godot 3D (Forward+, volumetric fog, real lamp/headlight lights, footprint decals, Kraggor eyes) behind the original story25d characters; exporter reads the cairo camera matrix per frame; modal_godot picks Forward+ from project.godot
**📤 Upload / antrean / Drive**
- `3cac47d` publish: daily run 2026-10-05 [cron daily_publish.sh]
<details><summary>otomatis VM (19)</summary>

- `978e558` records
- `5081031` records
- `19a2127` records
- `7f59d31` records: Tilly song v2 + VC takes
- `037b7ca` records: Tilly song v2 + VC takes
- `0d07965` records: modal usage
- `1dd1446` records: modal usage
- `2b7df45` records
- `5cb1603` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `555c0b9` records
- `72fb163` records
- `2f17484` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `8036414` records
- `6fac18c` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `eb4e5bf` records
- `bd5891e` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `5bdeb91` records: S01E02 cues
- `f29e60a` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `5918524` analytics: daily report 2026-10-05

</details>

## 2026-10-04
**🕳️ CHALLENGE (sim_engine)**
- `576b4eb` produce: SIM_RACE25D_V4_S046 (pending review) [Claude Code Opus]
- `a101cb6` produce: SIM_RACE25D_V4_S045 (pending review) [Claude Code Opus]
- `b6e995d` produce: SIM_RACE25D_V4_S044 (pending review) [Claude Code Opus]
- `35d0c97` produce: SIM_RACE25D_V4_S043 (pending review) [Claude Code Opus]
- `ae4e638` produce: SIM_RACE25D_V4_S042 (pending review) [Claude Code Opus]
- `dffdaee` produce: SIM_RACE25D_V4_S040 (pending review) [Claude Code Opus]
- `0943553` produce: SIM_RACE25D_V4_S039 (pending review) [Claude Code Opus]
- `3073109` produce: SIM_RACE25D_V4_S038 (pending review) [Claude Code Opus]
- `fc9f82f` produce: SIM_RACE25D_V4_S037 (pending review) [Claude Code Opus]
- `697bef3` produce: SIM_RACE25D_V4_S036 (pending review) [Claude Code Opus]
- `61512be` produce: SIM_RACE25D_V4_S035 (pending review) [Claude Code Opus]
- `b266b5e` produce: SIM_RACE25D_V4_S034 (pending review) [Claude Code Opus]
- `8cded33` produce: SIM_RACE25D_V4_S033 (pending review) [Claude Code Opus]
- `0a0ea4b` produce: SIM_RACE25D_V4_S032 (pending review) [Claude Code Opus]
- `7ca3a3b` produce: SIM_RACE25D_V4_S030 (pending review) [Claude Code Opus]
- `e161375` produce: SIM_RACE25D_V4_S029 (pending review) [Claude Code Opus]
- `aeb57ba` produce: SIM_RACE25D_V4_S028 (pending review) [Claude Code Opus]
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
**🏁 RACE (race25d)**
- `cd7b0e5` race25d pixel sensor v4 (validated): star hazard clearly visible; car on screen + hazard invisible = fail; fully off-screen hits = warning
- `b0cda9b` race25d: container stays on the road after landing (it flew 22 m up off-screen since v3); pixel sensor check: every hazard that hits must be visible on screen; QA_DEFECT_TRACKER.md
- `717042c` race25d: no speed bonus after a ramp (a monster truck beat an unhit taxi, S041); produce.py tries the next seed after an engine-check failure
- `3c7af6b` race25d: cold open starts 0.45 s before the star (camera already on it, no pan inside); 4 title forms, never a title another video has
- `d073a40` race25d: redraw the hazard set when layout + hazards equal one of the last 10 RACE videos
- `5485fe5` race25d camera: whip pan (up to 9 m/frame) between far-apart cars; check allows <= 10 empty frames inside a whip, none while the camera rests
- `fe8859e` race25d camera: without a highlight follow the biggest group (zoom for that group), not the midpoint of the whole field
- `52d6b51` race25d: log the first empty frames (mode, focus, camera, car positions) for diagnosis
- `b6d1bd3` race25d camera: soft keep-in-frame (fast pan up to 4 m/frame) when the capped glide lags behind the key car
- `53a7710` race25d: zoom in on the star moment (the asked-about car was often tiny in a back lane)
- `3a65754` race25d camera: when hazard moments overlap, focus the title's star (S022 test: cold open framed the ice dragon while asking about the hammer)
- `2437c64` race25d crusher: the press stops on the victim's roof and follows the squash (tall trucks were pierced by the press/rod)
- `de29f8a` RACE cold open: question in the top band over a dark gradient (not over the action); title, cold open and replay share one star moment
- `d73348d` race25d: cars swerve around (or brake behind) a fresh wreck in their lane; camera glides with a speed cap instead of jumping
- `9ecbffa` race25d: title/hook question asks about the racer who really meets the most striking hazard (honest payoff)
- `9ea2ec7` race25d v4: class speeds F1 > sports > police > taxi > monster > icecream/firetruck > bus/bigrig, pickup per class, realistic-order check
**🔧 Lain-lain**
- `21cf459` reject: SIM_RACE25D_V4_S038, S039, S042 (container invisible, user 2026-10-04)
- `420c2f1` swap: Ep. 31/37/40/49 <- RACE v4 S036/S040/S037/S043 (user 2026-10-04 approved)
- `588e535` reject: SIM_RACE25D_V4_S028-S035 (user 2026-10-04: remake with unique titles + cold open on the star)
- `14d14c0` reject: SIM_RACE25D_V4_S019-S025 (user 2026-10-04: remake with camera/cold-open fixes)
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
**📤 Upload / antrean / Drive**
- `90a5fa8` publish: daily run 2026-10-04 [cron daily_publish.sh]
- `c657eee` episodes.py unreject: a REJECTED render back to pending (MP4 restored from Drive) when the user changes their mind
**🧪 Lab (eksperimen)**
- `2bfc0a1` lab hybrid: upload_sample.py (Drive lab/hybrid)
- `9a6e738` lab hybrid: darker sea with sun path, purple headlands, brighter clouds
- `ac6a7b8` lab hybrid: cairo screen-space sky + sun, visible sea, low dunes, fuller palms
- `4f5ad71` lab hybrid: Godot background project (beach sunset: theme sky, sun glow, waves + glitter, foam, dunes, palms, clouds, gulls)
- `a2d61b8` lab hybrid: exporter (aired 2.5D frames with transparent background + background camera)
- `2fe3bf8` lab: revert3d.py (review videos back to the 2.5D engine, user 2026-10-04) + ERROR_LOG for the 3D review batch
<details><summary>otomatis VM (35)</summary>

- `a0a3d49` records
- `e236b91` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `5f1914e` records
- `d3cffc4` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `5f6edfd` records: S041 audit failed
- `fc57c6a` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `05358b1` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `055847d` records: S031 structure repeat
- `a71825d` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `54ed3a5` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `2bf2ab5` records: S027 audit failed
- `f96f524` Merge branch 'main' of github-megawheel:kokoali-bima/megawheel-video-engine
- `7692a2a` records: S026 audit failed
- `f617ef4` analytics: daily report 2026-10-04
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
