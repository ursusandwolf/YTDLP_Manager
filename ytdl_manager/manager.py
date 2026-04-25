import sys
from pathlib import Path

from .filename_generator import FilenameGenerator
from .subtitle_cleaner import SubtitleCleaner
from .youtube_downloader import YouTubeDownloader


class YTDLManager:
    def __init__(
        self,
        downloader: YouTubeDownloader,
        cleaner: SubtitleCleaner,
        filename_generator: FilenameGenerator,
    ):
        self._downloader = downloader
        self._cleaner = cleaner
        self._filename_generator = filename_generator

    def process_video(self, video_url: str, lang: str, output_dir: Path):
        """
        Orchestrate the download, cleaning, and saving of subtitles.
        """
        print(f"📥 Загружаем субтитры на языке: {lang}")
        vtt_path = None
        try:
            title = self._downloader.get_video_title(video_url)
            output_basename = self._filename_generator.build_filename(title)
            
            vtt_path = self._downloader.download_subtitles(
                video_url, lang, output_basename
            )

            print(f"🧼 Обрабатываем файл: {vtt_path.name}")
            cleaned_text = self._cleaner.clean_vtt_to_text(vtt_path)

            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / vtt_path.with_suffix(".txt").name
            self._save_to_file(cleaned_text, output_file)

            print(f"✅ Готово! Текст сохранён в: {output_file}")

        except (RuntimeError, FileNotFoundError) as e:
            print(f"❌ Ошибка: {e}", file=sys.stderr)
            sys.exit(1)
        finally:
            if vtt_path and vtt_path.exists():
                vtt_path.unlink()
                print(f"🗑️ Временный файл «{vtt_path.name}» удалён.")

    def _save_to_file(self, text: str, output_path: Path):
        """Save text to a file."""
        output_path.write_text(text, encoding="utf-8")
