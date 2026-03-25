import subprocess
import sys
import os
from pathlib import Path

from filename import build_filename

def download_subtitles(video_url, lang="en", output_basename="temp_subs"):
    title = get_video_title(video_url)
    output_basename = build_filename(title)
    subtitle_filename = f"{output_basename}.{lang}.vtt"

    result = subprocess.run([
        "yt-dlp",
        "--write-auto-sub",
        "--sub-lang", lang,
        "--skip-download",
        "--output", output_basename,
        video_url
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("yt-dlp failed to download subtitles.")

    if not os.path.exists(subtitle_filename):
        raise FileNotFoundError(f"Subtitle file not found: {subtitle_filename}")

    return subtitle_filename

def get_video_title(video_url: str) -> str:
    result = subprocess.run(
        ["yt-dlp", "--print", "title", video_url],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError("Failed to fetch video title")

    return result.stdout.strip()


def clean_vtt_to_text(vtt_path, min_timestamp_gap=300):
    import html
    import re

    with open(vtt_path, "r", encoding="utf-8") as f:
        raw = f.read()

    # Извлекаем блоки с таймкодами и текстом
    blocks = re.findall(r"(\d{2}:\d{2}:\d{2}\.\d{3}) --> .*?\n(.*?)\n", raw, re.DOTALL)

    cleaned_lines = []
    last_timestamp = None
    last_line = None
    for timestamp_str, text in blocks:
        # Удаляем HTML-теги и служебные описания
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"\[.*?\]", "", text)
        text = html.unescape(text.strip())

        if not text:
            continue

        # Удаляем подряд идущие повторы
        if text == last_line:
            continue
        last_line = text

        # Добавляем таймкод, если прошло достаточно времени
        timestamp = parse_timestamp(timestamp_str)
        if last_timestamp is None or (timestamp - last_timestamp).total_seconds() >= min_timestamp_gap:
            cleaned_lines.append(f"[{format_timestamp(timestamp)}]")
            last_timestamp = timestamp

        cleaned_lines.append(text)

    # Исправляем пунктуацию и объединяем с переносами строк
    punctuated_lines = fix_punctuation_lines(cleaned_lines)
    final_text = "\n".join(punctuated_lines)

    return final_text

def parse_timestamp(ts_str):
    from datetime import timedelta
    h, m, s = ts_str.split(":")
    sec, ms = s.split(".")
    return timedelta(hours=int(h), minutes=int(m), seconds=int(sec), milliseconds=int(ms))

def format_timestamp(td):
    total_seconds = int(td.total_seconds())
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h:02}:{m:02}:{s:02}"

def fix_punctuation_lines(lines):
    import re
    punctuated = []
    for line in lines:
        if line.startswith("[") and line.endswith("]"):
            punctuated.append(line)
            continue

        # Добавляем точку, если строка не заканчивается знаком
        if not re.search(r"[.!?…]$", line):
            line += "."

        # Заглавная буква в начале
        if line:
            line = line[0].upper() + line[1:]

        punctuated.append(line)

    return punctuated

def save_to_file(text, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

def main():
    # Обработка аргументов
    args = sys.argv[1:]
    video_url = None
    lang = "en"  # язык по умолчанию

    for arg in args:
        if arg.startswith("http"):
            video_url = arg
        elif arg.startswith("-"):
            lang = arg[1:].lower()

    # Если аргументы не переданы — спрашиваем у пользователя
    if not video_url:
        video_url = input("🔗 Введите ссылку на YouTube-видео: ").strip()
        lang = input("🌍 Укажите язык субтитров (например: en, ru, de, uk): ").strip().lower() or "en"

    print(f"📥 Загружаем автосубтитры на языке: {lang}")
    vtt_file = download_subtitles(video_url, lang=lang)

    print(f"🧼 Обрабатываем файл: {vtt_file}")
    cleaned_text = clean_vtt_to_text(vtt_file)

    # 📁 отдельная папка
    output_dir = Path("txt")
#    output_file = output_dir / (Path(vtt_file).stem + ".txt")

    output_file = output_dir / vtt_file.replace(".vtt", ".txt")
    save_to_file(cleaned_text, output_file)

    # 🗑 удаляем vtt только если всё успешно
    if os.path.exists(vtt_file):
        os.remove(vtt_file)
        print(f".vtt файл удален")

#    output_file = vtt_file.replace(".vtt", ".txt")
#    save_to_file(cleaned_text, output_file)
    print(f"✅ Готово! Чистый текст сохранён в: {output_file}")

if __name__ == "__main__":
    main()
