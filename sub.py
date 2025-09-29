import subprocess
import os
import re
from io import StringIO

def download_subtitles(video_url, output_basename="temp_subs"):
    subtitle_filename = f"{output_basename}.en.vtt"

    result = subprocess.run([
        "yt-dlp",
        "--write-auto-sub",
        "--sub-lang", "en",
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

def clean_vtt_to_text(vtt_path):
    with open(vtt_path, "r", encoding="utf-8") as f:
        raw = f.read()

    # Clean sub WEBVTT and timecodes
    cleaned = re.sub(r"WEBVTT.*?\n", "", raw)
    cleaned = re.sub(r"\d{2}:\d{2}:\d{2}\.\d{3} --> .*?\n", "", cleaned)
    cleaned = re.sub(r"align:start position:\d+%.*?\n", "", cleaned)

    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    text = " ".join(lines)

    return text

def save_to_file(text, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

def main():
    video_url = input("🔗 Введите ссылку на YouTube-видео: ").strip()
    print("📥 Загружаем автосубтитры...")
    vtt_file = download_subtitles(video_url)

    print(f"🧼 Обрабатываем файл: {vtt_file}")
    cleaned_text = clean_vtt_to_text(vtt_file)

    output_file = vtt_file.replace(".vtt", ".txt")
    save_to_file(cleaned_text, output_file)
    print(f"✅ Готово! Чистый текст сохранён в: {output_file}")

if __name__ == "__main__":
    main()
