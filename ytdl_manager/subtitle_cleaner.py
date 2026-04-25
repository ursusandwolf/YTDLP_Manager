import html
import re
from datetime import timedelta
from pathlib import Path


class SubtitleCleaner:
    def clean_vtt_to_text(self, vtt_path: Path, min_timestamp_gap: int = 300) -> str:
        """
        Clean a VTT subtitle file into plain text with optional timestamps.
        """
        raw_text = vtt_path.read_text(encoding="utf-8")

        cleaned_lines = []
        last_timestamp = None

        for timestamp_str, text_block in self._parse_vtt_blocks(raw_text):
            lines = self._clean_text_block(text_block)
            if not lines:
                continue

            # Add a timestamp if the gap is large enough
            timestamp = self._parse_timestamp(timestamp_str)
            if (
                last_timestamp is None
                or (timestamp - last_timestamp).total_seconds() >= min_timestamp_gap
            ):
                cleaned_lines.append(f"\n[{self._format_timestamp(timestamp)}]")
                last_timestamp = timestamp

            # Remove duplicates
            for line in lines:
                if not cleaned_lines or line != cleaned_lines[-1]:
                    cleaned_lines.append(line)

        # Post-process lines for better readability
        punctuated_text = self._post_process_text(cleaned_lines)
        return punctuated_text

    def _parse_vtt_blocks(self, raw_text: str):
        """Parse VTT text and yield (timestamp, text_block) tuples."""
        # Regex to capture timestamp and text, ignoring the rest of the time line
        # and ensuring we capture multi-line blocks correctly.
        return re.findall(
            r"(\d{2}:\d{2}:\d{2}\.\d{3}) --> .*?\n(.*?)(?=\n\n|\Z)",
            raw_text,
            re.DOTALL,
        )

    def _clean_text_block(self, text_block: str) -> list[str]:
        """Clean a single block of subtitle text and return a list of lines."""
        lines = text_block.strip().split("\n")
        cleaned_block = []
        for line in lines:
            # Remove HTML tags, formatting cues, and speaker tags
            line = re.sub(r"<c[.\w\d]+>", "", line)  # color tags
            line = re.sub(r"</c>", "", line)
            line = re.sub(r"<[^>]+>", "", line)
            line = re.sub(r"\[.*?\]", "", line)  # [Music], [Applause]
            line = html.unescape(line.strip())
            if line:
                cleaned_block.append(line)
        return cleaned_block

    def _post_process_text(self, lines: list[str]) -> str:
        """Improve punctuation and capitalization of the final text."""
        processed_lines = []
        for i, line in enumerate(lines):
            if line.startswith("\n[") and line.endswith("]"):
                processed_lines.append(line)
                continue

            # Capitalize the first letter of a sentence
            if i > 0 and processed_lines[-1] and processed_lines[-1].endswith((".", "!", "?", "…")):
                line = line[0].upper() + line[1:]

            # Add punctuation at the end of lines that don't have it.
            if not line.endswith((".", "!", "?", "…")):
                line += "."

            processed_lines.append(line)

        text = "\n".join(processed_lines)
        # Capitalize the very first letter of the text
        if text:
            text = text.strip()
            # Find the first letter to capitalize
            match = re.search(r"[a-zA-Zа-яА-Я]", text)
            if match:
                start = match.start()
                text = text[:start] + text[start].upper() + text[start + 1 :]

        return text

    def _parse_timestamp(self, ts_str: str) -> timedelta:
        """Parse a timestamp string (HH:MM:SS.ms) into a timedelta object."""
        h, m, s_ms = ts_str.split(":")
        s, ms = s_ms.split(".")
        return timedelta(
            hours=int(h), minutes=int(m), seconds=int(s), milliseconds=int(ms)
        )

    def _format_timestamp(self, td: timedelta) -> str:
        """Format a timedelta object into a [HH:MM:SS] string."""
        total_seconds = int(td.total_seconds())
        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60
        return f"{h:02}:{m:02}:{s:02}"
