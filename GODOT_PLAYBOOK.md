# GODOT_PLAYBOOK — menguasai Godot untuk video MegaWheel Arena (Shorts 2D + episode cerita)

> Permintaan user 2026-10-03: "kuasai Godot sampai level expert, kumpulkan referensi sebanyak-banyaknya" — untuk
> Shorts (CHALLENGE/RACE/SMASH) dan Episode 2. Dokumen hidup: setiap pelajaran prototipe ditulis di sini.

## 0. Status prototipe (2026-10-03)
| Sampel | Hasil | Pelajaran |
|---|---|---|
| SMASH v2 | ✅ meteor + ledakan bercahaya + mobil pecah + suara | fitur inti Godot terbukti; kamera auto-fit bekerja |
| RACE v2 | ⚠️ palu/kontainer terjadi di luar layar | **kamera harus disutradarai per momen** (bukan "ikuti mobil terdepan") |
| CHALLENGE v2 | ⚠️ hanya Zippy terlihat, mobil lain di luar layar | sama + lintasan harus lebih panjang dari jarak finish |
| v1 | terasa "slow motion", gambar kecil | slow-mo dipicu tiap ledakan & zoom 0.6 → **slow-mo 1×/video, zoom ≥ 1.0** |

Render: Godot 4.4.1 ARM64 di VM 99.3, `xvfb-run` + renderer **gl_compatibility** (software GL), ±1,5–2 menit per
Short 25 dtk, **gratis** (tanpa Modal). Video selalu diputar kecepatan normal (Movie Maker = non-real-time).

## 1. Arsitektur target (hybrid, yang sudah terbukti)
```
cairo cast (sim_engine)  --export_sprites.py-->  PNG sprite tokoh (identik di semua mesin)
                                                     |
Godot project (main.gd per mode)  --Movie Maker-->  AVI MJPEG  --ffmpeg-->  MP4
        | events.json (t, type, power, x)                                     |
        +--> godot_mix.py (SFX bank + musik + jingle) -----------------------> MP4 + audio
                                                     |
             manifest + registry + audit + Drive + approval + upload (pipeline lama, tidak berubah)
```

## 2. Teknik inti + referensi
| Teknik | Cara di Godot | Referensi |
|---|---|---|
| Render video otomatis | `--write-movie out.avi --fixed-fps 30 --quit-after N`, resolusi = viewport (`--resolution`), MJPEG quality di project setting | Docs "Creating movies"; artikel "Movie Maker mode arrives in Godot 4" |
| Server tanpa layar | `xvfb-run -a -s "-screen 0 1080x1920x24"`, `--rendering-driver opengl3`; `--headless` hanya untuk cek parse (tidak merender) | godot-ci docker (barichello/godot-ci) |
| Renderer | Compatibility (OpenGL, jalan di CPU) sekarang; **Forward+ (Vulkan)** untuk glow/HDR 2D → uji di GPU Modal nanti | Docs "Overview of renderers" |
| Cahaya & bayangan 2D | CanvasModulate (gelapkan dunia) + PointLight2D / DirectionalLight2D + LightOccluder2D; filter PCF untuk bayangan lembut | Docs "2D lights and shadows"; Catlike Coding "Light and Shadow" |
| Normal map sprite (cahaya terasa 3D) | generate dari sprite dengan **Laigter** (GPL, CLI/plugin) → `CanvasTexture` normal | Laigter docs; Godot Normal Map Generator plugin |
| Partikel (api, asap, percikan, debu) | GPUParticles2D direkomendasikan (Forward+); CPUParticles2D di Compatibility; color ramp + scale curve | Docs "2D particle systems" |
| Shader layar (shockwave, heat haze, chromatic) | `canvas_item` shader di ColorRect/CanvasLayer teratas, `hint_screen_texture` | godotshaders.com (Distortion/Shockwave, Heat Haze); Docs "Screen-reading shaders" |
| Hancur berkeping | potong poligon sprite (Delaunay/Voronoi, `Geometry2D`) → RigidBody2D per keping, UV tekstur | Godot Polygon2D Fracture (DaveGreen, MIT); Breakable 2D Sprites (opaque_to_polygons) |
| Kamera sinematik | trauma-based shake, smooth follow (lerp), zoom Tween, "phantom camera" (pisahkan *look at* & *follow*) | uhiyama-lab "Camera2D techniques"; ProCam2D; dev.to "screen shake & hit stop" |
| Tokoh ber-rig (badan, mata, mulut) | Skeleton2D + Bone2D + Polygon2D ber-weight (cutout animation), IK | Docs "Cutout animation" / "2D skeletons" |
| Cutscene / episode cerita | **AnimationPlayer** (track posisi, kamera, method call, audio) + signal; dialog via Dialogic 2 (opsional) | wayline.io "Cinematic cutscenes"; Dialogic 2; Cinematic Camera 2D asset |
| Lip-sync | output Rhubarb (TSV/JSON) → track AnimationPlayer frame mulut | Rhubarb Lip Sync (MIT) |
| Audio di dalam render | AudioStreamPlayer2D (panning stereo otomatis sesuai posisi layar) — Movie Maker merekam audio juga | Docs "Creating movies" |

## 3. Aturan produksi Godot (dari kesalahan prototipe)
1. **Sutradara kamera**: setiap momen (hit, jump, crash, win) didaftarkan sebagai *beat*; kamera menuju beat aktif
   0,8 dtk sebelum terjadi. Pemimpin balapan hanya dipakai saat tidak ada beat.
2. Slow-mo maksimal 1× per video (0,5–0,7 dtk, 45%), hit-stop 2–3 frame boleh untuk tiap tabrakan besar.
3. Zoom ≥ 1.0 (Shorts vertikal: mobil ≥ 1/3 lebar layar saat momen penting).
4. Penggerak mobil = pengendali kecepatan (m/s) + torsi roda kecil untuk visual (bukan torsi saja).
5. CCD (`CCD_MODE_CAST_SHAPE`) untuk roda & keping; spawn 0,25 m di atas tanah; jangan spawn dua mobil di titik sama.
6. Perubahan fisika di callback tabrakan → `call_deferred` (hindari error "flushing queries").
7. Typed GDScript: hindari `:=` dari nilai Variant (Dictionary/Array) — parse error.
8. Cek parse cepat sebelum render: `godot --headless --path P --quit-after 20`.
9. Lintasan selalu lebih panjang dari finish + 40 m (mobil tidak jatuh di ujung dunia).

## 4. Roadmap menuju "level expert"
| Tahap | Isi | Target |
|---|---|---|
| A (minggu ini) | sutradara kamera + beats; sampel RACE/CHALLENGE ulang; SFX bank (lihat SFX_PLAN.md) | 3 sampel layak banding |
| B | normal map (Laigter) + cahaya per waktu; partikel GPU & glow di GPU Modal (Forward+) | kualitas visual "bumi-langit" |
| C | tokoh ber-rig (mata/mulut/badan) + AnimationPlayer cutscene + Rhubarb | siap Episode cerita |
| D | port generator stok (seed, variasi, audit, manifest) ke Godot | produksi harian |

## Sumber
Docs Godot: Creating movies; Overview of renderers; 2D lights and shadows; 2D particle systems; Screen-reading shaders;
Cutout animation. Artikel: godotengine.org "Movie Maker mode arrives in Godot 4"; forum "physics_process twice as
fast in Movie Maker". Tutorial/asset: Catlike Coding; uhiyama-lab Camera2D; ProCam2D; dev.to screen shake; wayline.io
cutscenes; Dialogic 2; godotshaders.com; Godot Polygon2D Fracture; Breakable 2D Sprites; Laigter; godot-ci.
