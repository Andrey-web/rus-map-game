#!/usr/bin/env python3
"""
Собирает один самодостаточный HTML: подставляет data URL вместо ./files/...
Запуск из корня проекта:
  python3 bundle_standalone.py
Результат: index-standalone.html (можно отдавать «как есть», без папки files).
"""
from __future__ import annotations

import base64
import re
import sys
from pathlib import Path

MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".avif": "image/avif",
    ".mp3": "audio/mpeg",
}

# Пробел/кавычки/закр. скобка — границы пути (\s именно whitespace, не буква s)
PLACEHOLDER_RE = re.compile(r"\./files/(?:img|music)/[^\s\"')]+")


def main() -> None:
    root = Path(__file__).resolve().parent
    src = root / "index.html"
    out = root / "play.html"
    if not src.is_file():
        print("Нет index.html рядом со скриптом.", file=sys.stderr)
        sys.exit(1)

    html = src.read_text(encoding="utf-8")
    paths = sorted(set(PLACEHOLDER_RE.findall(html)), key=len, reverse=True)

    for rel in paths:
        fpath = root / rel.lstrip("./")
        if not fpath.is_file():
            print(f"Пропущен (нет файла): {rel}", file=sys.stderr)
            continue
        ext = fpath.suffix.lower()
        mime = MIME.get(ext)
        if not mime:
            print(f"Неизвестное расширение {ext} для {rel}", file=sys.stderr)
            sys.exit(1)
        b64 = base64.standard_b64encode(fpath.read_bytes()).decode("ascii")
        data_url = f"data:{mime};base64,{b64}"
        html = html.replace(rel, data_url)

    out.write_text(html, encoding="utf-8")
    print(f"Готово: {out} ({out.stat().st_size // (1024 * 1024)} МиБ прибл.)")


if __name__ == "__main__":
    main()
