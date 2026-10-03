"""LAB probe: which NVIDIA graphics libraries does a Modal GPU container expose (GL / EGL / Vulkan), so Godot can
render on the GPU instead of llvmpipe? (user 2026-10-03: try Modal GPU, faster and cheaper)
  venv-modal/bin/modal run lab/godot3d_challenge/modal_gpu_probe.py"""
import modal

app = modal.App("megawheel-gpu-probe")
image = modal.Image.debian_slim().apt_install("mesa-utils", "vulkan-tools", "libegl1", "libgl1", "xvfb", "xauth")


@app.function(image=image, gpu="T4", timeout=300)
def probe() -> str:
    import glob
    import os
    import subprocess
    out = []
    for pat in ["/usr/lib/x86_64-linux-gnu/*nvidia*", "/usr/lib64/*nvidia*", "/usr/local/nvidia/lib64/*",
                "/usr/share/vulkan/icd.d/*", "/etc/vulkan/icd.d/*", "/usr/share/glvnd/egl_vendor.d/*"]:
        out += sorted(glob.glob(pat))[:40]
    out.append("ENV NVIDIA_DRIVER_CAPABILITIES=" + os.environ.get("NVIDIA_DRIVER_CAPABILITIES", "?"))
    for cmd in (["nvidia-smi", "-L"], ["vulkaninfo", "--summary"], ["xvfb-run", "-a", "glxinfo", "-B"]):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            out.append("$ " + " ".join(cmd) + "\n" + (r.stdout + r.stderr)[-1500:])
        except Exception as ex:
            out.append(f"$ {cmd}: {ex}")
    return "\n".join(out)


@app.local_entrypoint()
def main():
    print(probe.remote())
