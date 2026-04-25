import argparse
import sys
from pathlib import Path

from ytdl_manager.filename_generator import FilenameGenerator
from ytdl_manager.manager import YTDLManager
from ytdl_manager.subtitle_cleaner import SubtitleCleaner
from ytdl_manager.youtube_downloader import YouTubeDownloader


def main():
    """Parse arguments and run the subtitle processing."""
    parser = argparse.ArgumentParser(
        description="Загрузка и очистка субтитров с YouTube.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("video_url", nargs="?", help="Ссылка на YouTube-видео.")
    parser.add_argument(
        "-l", "--lang", default="en", help="Язык субтитров (по умолчанию: en)."
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        type=Path,
        default=Path("txt"),
        help="Папка для сохранения результата (по умолчанию: txt/).",
    )
    args = parser.parse_args()

    video_url = args.video_url
    lang = args.lang

    if not video_url:
        try:
            video_url = input("🔗 Введите ссылку на YouTube-видео: ").strip()
            if not video_url:
                print("❌ Ссылка не указана.", file=sys.stderr)
                sys.exit(1)

            lang_input = (
                input(f"🌍 Укажите язык субтитров (по умолчанию: {lang}): ")
                .strip()
                .lower()
            )
            if lang_input:
                lang = lang_input

        except (KeyboardInterrupt, EOFError):
            print("\n👋 Выход.", file=sys.stderr)
            sys.exit(0)

    # Instantiate the components
    downloader = YouTubeDownloader()
    cleaner = SubtitleCleaner()
    filename_generator = FilenameGenerator()

    # Instantiate the manager with the components
    manager = YTDLManager(downloader, cleaner, filename_generator)

    # Run the process
    manager.process_video(video_url, lang, args.output_dir)


if __name__ == "__main__":
    main()
