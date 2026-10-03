"""LAB — undo a 3D conversion: the 2.5D original (<id>_25d.mp4) becomes the review file again (user 2026-10-04:
"pakai yang 2.5D engine lama; 3D harus dibuat dari awal, bukan convert"). The 3D file is deleted, the 2.5D preview
sheet comes back, manifest/registry lose render3d, the Drive review copy is replaced by the 2.5D one.
  venv/bin/python lab/godot3d_challenge/revert3d.py <VIDEO_ID> [...]"""
import json
import os
import shutil
import sys

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for sub in ("generators/physics_2d", "generators/publishing"):
    sys.path.insert(0, os.path.join(BASE, sub))
import registry  # noqa: E402


def revert(vid):
    e = registry.get(vid)
    if not e or e.get("status") != "RENDERED_PENDING_APPROVAL":
        print(f"[revert3d] STOP {vid}: bukan RENDERED_PENDING_APPROVAL")
        return False
    folder = f"{BASE}/{e['folder']}"
    orig = f"{folder}/{vid}_25d.mp4"
    if not os.path.exists(orig):
        print(f"[revert3d] {vid}: tidak ada _25d.mp4 (sudah 2.5D?)")
        return False
    os.replace(orig, f"{folder}/{vid}.mp4")
    for x in (f"{folder}/{vid}_3dold.mp4", f"{folder}/{vid}_audit3d.md"):
        if os.path.exists(x):
            os.remove(x)
    if os.path.isdir(f"{folder}/preview_25d"):
        shutil.rmtree(f"{folder}/preview", ignore_errors=True)
        shutil.move(f"{folder}/preview_25d", f"{folder}/preview")
    man_path = f"{folder}/{vid}.json"
    man = json.load(open(man_path))
    man.pop("render3d", None)
    for k, tag in (("engine", " + godot3d"), ("assets", "; picture re-drawn in 3D")):
        if tag in man.get(k, ""):
            man[k] = man[k].split(tag)[0]
    json.dump(man, open(man_path, "w"), indent=2, ensure_ascii=False)
    registry.update(vid, render3d=False)
    try:
        import drive_sync
        e = registry.get(vid)
        for key in ("drive_id", "drive_sheet_id"):
            if e.get(key):
                try:
                    drive_sync.service().files().delete(fileId=e[key]).execute()
                except Exception as ex:
                    print(f"[drive] hapus 3D gagal: {ex}")
        registry.update(vid, drive_id=None, drive_sheet_id=None)
        drive_sync.sync_one(vid)
    except Exception as ex:
        print(f"[drive] dilewati: {ex}")
    print(f"[revert3d] {vid} -> 2.5D")
    return True


if __name__ == "__main__":
    ok = [revert(v) for v in sys.argv[1:]]
    print(f"[revert3d] {sum(ok)}/{len(ok)} dikembalikan ke 2.5D")
