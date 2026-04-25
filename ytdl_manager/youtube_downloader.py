import subprocess
from pathlib import Path


class YouTubeDownloader:
    def download_subtitles(
        self, video_url: str, lang: str, output_basename: str
    ) -> Path:
        """Download subtitles using yt-dlp and return the path to the VTT file."""
        subtitle_path = Path(f"{output_basename}.{lang}.vtt")

        command = [
            "yt-dlp",
            "--write-auto-sub",
            "--sub-lang",
            lang,
            "--skip-download",
            "--output",
            output_basename,
            video_url,
        ]

        result = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8"
        )

        if result.returncode != 0:
            raise RuntimeError(f"yt-dlp failed: {result.stderr}")

        if not subtitle_path.exists():
            raise FileNotFoundError(f"Subtitle file not found: {subtitle_path}")

        return subtitle_path

    def get_video_title(self, video_url: str) -> str:
        """Fetch video title using yt-dlp."""
        command = ["yt-dlp", "--print", "title", video_url]
        result = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8"
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to fetch video title: {result.stderr}")
        return result.stdout.strip()
