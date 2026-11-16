#!/usr/bin/env python3
"""Build YouTube Data API v3 `localizations` dict for MegaWheel Arena videos.

Keeps ONLY English (en-US) + the 5 target audience languages:
  id (Indonesian), es-419 (Latin American Spanish), pt-BR (Brazilian Portuguese),
  ar (Arabic), de (German).

Preserves character names (Sprinkles, Rocky, Siren, Zippy, Buster, Hydro,
Grizzly, Nitro, Tilly, Titan), brand name (MegaWheel Arena), and #Shorts.
"""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from typing import Dict

TARGET_LANGS = ("id", "es-419", "pt-BR", "ar", "de")

_GT_CODE = {
    "id": "id",
    "es-419": "es",
    "pt-BR": "pt",
    "ar": "ar",
    "de": "de",
}

_PROTECTED = (
    "MegaWheel Arena",
    "Sprinkles",
    "Rocky",
    "Siren",
    "Zippy",
    "Buster",
    "Hydro",
    "Grizzly",
    "Nitro",
    "Tilly",
    "Titan",
    "#Shorts",
)

# Common description lines translated natively for natural tone
_DESC_LINES: Dict[str, Dict[str, str]] = {
    "💬 Comment A if you love the NEW 3D graphics, or B if you prefer the classic look!": {
        "id": "💬 Komen A kalau kamu suka grafik 3D BARU, atau B kalau lebih suka tampilan klasik!",
        "es-419": "💬 ¡Comenta A si te encantan los NUEVOS gráficos 3D, o B si prefieres el estilo clásico!",
        "pt-BR": "💬 Comente A se você curtiu os NOVOS gráficos 3D, ou B se prefere o visual clássico!",
        "ar": "💬 اكتب A في التعليقات إذا أعجبتك الرسومات ثلاثية الأبعاد الجديدة، أو B إذا كنت تفضل الشكل الكلاسيكي!",
        "de": "💬 Kommentiere mit A, wenn dir die NEUE 3D-Grafik gefällt, oder mit B, wenn du den klassischen Look bevorzugst!",
    },
    "Watch till the end for the slow-motion replay! 🎬": {
        "id": "Tonton sampai habis untuk melihat tayangan ulang gerak lambat (slow-motion)! 🎬",
        "es-419": "¡Mira hasta el final para ver la repetición en cámara lenta! 🎬",
        "pt-BR": "Assista até o final para ver o replay em câmera lenta! 🎬",
        "ar": "شاهد حتى النهاية لرؤية الإعادة بالعرض البطيء! 🎬",
        "de": "Schau bis zum Ende für die Zeitlupen-Wiederholung! 🎬",
    },
    "🏆 Comment your champion below!": {
        "id": "🏆 Tulis jagoanmu di kolom komentar!",
        "es-419": "🏆 ¡Comenta quién es tu campeón aquí abajo!",
        "pt-BR": "🏆 Comente o seu campeão aqui embaixo!",
        "ar": "🏆 اكتب اسم بطلك المفضل في التعليقات!",
        "de": "🏆 Schreib deinen Favoriten unten in die Kommentare!",
    },
    "🔔 Subscribe to MegaWheel Arena for new car challenges every week.": {
        "id": "🔔 Subscribe ke MegaWheel Arena untuk tantangan mobil seru setiap minggu.",
        "es-419": "🔔 Suscríbete a MegaWheel Arena para nuevos desafíos de autos cada semana.",
        "pt-BR": "🔔 Inscreva-se no MegaWheel Arena para novos desafios de carros toda semana.",
        "ar": "🔔 اشترك في قناة MegaWheel Arena لتحديات سيارات جديدة كل أسبوع.",
        "de": "🔔 Abonniere MegaWheel Arena für jede Woche neue Auto-Challenges.",
    },
    "🎬 Produced by Infrasoft Media & Tech": {
        "id": "🎬 Produced by Infrasoft Media & Tech",
        "es-419": "🎬 Produced by Infrasoft Media & Tech",
        "pt-BR": "🎬 Produced by Infrasoft Media & Tech",
        "ar": "🎬 Produced by Infrasoft Media & Tech",
        "de": "🎬 Produced by Infrasoft Media & Tech",
    },
}

_NEW_3D_SUFFIX = {
    "id": "Grafik 3D Baru",
    "es-419": "Nuevos Gráficos 3D",
    "pt-BR": "Novos Gráficos 3D",
    "ar": "رسومات ثلاثية الأبعاد جديدة",
    "de": "NEUE 3D-Grafik",
}


def _gt_translate(text: str, lang: str) -> str:
    """Best-effort Google Translate call with protected tokens; never raises."""
    if not text.strip():
        return text
    placeholders = {}
    masked = text
    for i, tok in enumerate(_PROTECTED):
        if tok in masked:
            key = f"ZXQ{i}K"
            placeholders[key] = tok
            masked = masked.replace(tok, key)
    try:
        url = (
            "https://translate.googleapis.com/translate_a/single"
            f"?client=gtx&sl=en&tl={_GT_CODE[lang]}&dt=t&q="
            + urllib.parse.quote(masked)
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        out = "".join(seg[0] for seg in data[0] if seg and seg[0])
        for key, tok in placeholders.items():
            out = out.replace(key, tok)
        return out
    except Exception:
        return text


def translate_title(title: str, lang: str) -> str:
    """Translate a MegaWheel title cleanly and enforce YouTube's 100-char cap."""
    # Split off "| Ep. 123 #Shorts" if present
    ep_suffix = ""
    core = title
    m = re.search(r"\s*\|\s*Ep\.\s*(\d+)(\s*#Shorts)?\s*$", title)
    if m:
        ep_num = m.group(1)
        shorts = " #Shorts" if m.group(2) else ""
        ep_label = f"ح {ep_num}" if lang == "ar" else f"Ep. {ep_num}"
        ep_suffix = f" | {ep_label}{shorts}"
        core = title[: m.start()].strip()

    # Replace "NEW 3D Graphics" cleanly before translating
    core_for_gt = core.replace("NEW 3D Graphics", "ZXNEW3D")
    translated = _gt_translate(core_for_gt, lang)
    translated = translated.replace("ZXNEW3D", " " + _NEW_3D_SUFFIX[lang])
    if lang == "id":
        translated = translated.replace("Mobil Terakhir Berdiri", "Mobil Terakhir Bertahan")
    # Fix common spacing around punctuation
    translated = re.sub(r"\s{2,}", " ", translated).strip()

    full = f"{translated}{ep_suffix}".strip()
    if len(full) <= 100:
        return full
    # Trim core if over 100 chars
    budget = 100 - len(ep_suffix) - 1
    if budget > 10:
        return f"{translated[:budget].rstrip()}…{ep_suffix}"
    return full[:100]


def translate_description(description: str, lang: str) -> str:
    """Translate description line-by-line, keeping hashtags and credits intact."""
    out_lines = []
    for line in description.splitlines():
        s = line.strip()
        if not s:
            out_lines.append("")
        elif s in _DESC_LINES:
            out_lines.append(_DESC_LINES[s][lang])
        elif s.startswith("#"):
            # Keep hashtag line as-is so #Shorts / #MegaWheelArena stay intact
            out_lines.append(s)
        else:
            out_lines.append(_gt_translate(s, lang))
    return "\n".join(out_lines)[:5000]


def build(title: str, description: str) -> Dict[str, Dict[str, str]]:
    """Return YouTube `localizations` dict for en-US + the 5 target languages."""
    locs: Dict[str, Dict[str, str]] = {
        "en-US": {
            "title": title[:100],
            "description": description[:5000],
        }
    }
    for lang in TARGET_LANGS:
        locs[lang] = {
            "title": translate_title(title, lang),
            "description": translate_description(description, lang),
        }
    return locs
