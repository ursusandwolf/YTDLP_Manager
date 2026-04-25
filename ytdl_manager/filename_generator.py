from datetime import datetime
import re
from typing import Tuple, Optional


class FilenameGenerator:
    def build_filename(self, title: str, max_length: int = 80) -> str:
        """
        Build a clean, truncated filename from a title, extracting a date if present.
        """
        sanitized_title = self._sanitize_filename(title)
        raw_date, normalized_date = self._extract_date(sanitized_title)

        # Remove the original date from the title to avoid redundancy
        if raw_date:
            # Use regex to remove the date to handle surrounding whitespace better
            title_wo_date = re.sub(
                r"\s*" + re.escape(raw_date) + r"\s*", " ", sanitized_title
            ).strip()
        else:
            title_wo_date = sanitized_title

        # Determine the available length for the main part of the title
        if normalized_date:
            # Reserve space for " YYYY-MM-DD"
            reserved_length = len(normalized_date) + 1
        else:
            reserved_length = 0

        allowed_length = max_length - reserved_length

        # Truncate the main part of the title
        main_part = self._smart_truncate(title_wo_date, allowed_length)

        # Combine the parts
        if normalized_date:
            # Ensure there's a space between title and date
            return f"{main_part} {normalized_date}".strip()

        return main_part

    def _sanitize_filename(self, name: str) -> str:
        """
        Remove illegal characters from a string to make it a valid filename.
        """
        name = name.strip()
        # Remove characters that are illegal in filenames on Windows and/or Linux
        name = re.sub(r'[\/*?:"<>|]', "", name)
        # Replace multiple whitespace characters with a single space
        name = re.sub(r"\s+", " ", name)
        return name

    def _extract_date(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Find a date in a string and normalize it to ISO 8601 format (YYYY-MM-DD).

        Returns a tuple of (raw_date, normalized_date).
        """
        # More comprehensive list of patterns
        date_patterns = [
            (r"\b(\d{4}-\d{2}-\d{2})\b", "%Y-%m-%d"),  # 2026-03-15
            (r"\b(\d{2}\.\d{2}\.\d{4})\b", "%d.%m.%Y"),  # 15.03.2026
            (r"\b(\d{2}/\d{2}/\d{4})\b", "%m/%d/%Y"),  # 03/15/2026 (US)
            (r"\b(\d{4}/\d{2}/\d{2})\b", "%Y/%m/%d"),  # 2026/03/15
            (r"\b(\d{2}-\d{2}-\d{4})\b", "%m-%d-%Y"),  # 03-15-2026 (US)
            (
                r"\b(\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{4})\b",
                "%d %b %Y",
            ),  # 15 Jan 2026
        ]

        for pattern, fmt in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                raw_date = match.group(1)
                try:
                    # Normalize the found date to ISO format
                    dt = datetime.strptime(raw_date, fmt)
                    return raw_date, dt.strftime("%Y-%m-%d")
                except ValueError:
                    # This might happen for ambiguous formats like 01-02-2023
                    # We can try to be smarter, but for now, we'll just continue
                    continue

        return None, None

    def _smart_truncate(self, text: str, max_length: int) -> str:
        """
        Truncate a string to a maximum length without cutting words in half.
        """
        if len(text) <= max_length:
            return text

        # Truncate to the max_length
        truncated = text[:max_length]

        # Find the last space to avoid cutting a word
        last_space = truncated.rfind(" ")
        if last_space != -1:
            return truncated[:last_space].strip()

        # If no space was found, we have to cut the word
        return truncated.strip()
