import re
from datetime import datetime

def sanitize_filename(name: str) -> str:
    name = name.strip()
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = re.sub(r"\s+", " ", name)
    return name


def extract_date(text: str):
    # Поддержка разных форматов
    patterns = [
        r"\b\d{4}-\d{2}-\d{2}\b",      # 2026-03-15
        r"\b\d{2}\.\d{2}\.\d{4}\b",    # 15.03.2026
        r"\b\d{2}/\d{2}/\d{4}\b",      # 03/15/2026
        r"\b\d{2}-\d{2}-\d{4}\b",      # 03-15-2026
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            raw_date = match.group()

            # Попробуем нормализовать в ISO
            for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%m/%d/%Y", "%m-%d-%Y"):
                try:
                    dt = datetime.strptime(raw_date, fmt)
                    return raw_date, dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue

            return raw_date, raw_date  # fallback

    return None, None


def smart_truncate(text: str, max_length: int) -> str:
    if len(text) <= max_length:
        return text

    truncated = text[:max_length]

    # не режем слово
    if " " in truncated:
        truncated = truncated.rsplit(" ", 1)[0]

    return truncated


def build_filename(title: str, max_length: int = 50) -> str:
    title = sanitize_filename(title)

    raw_date, normalized_date = extract_date(title)

    # Удаляем дату из основного текста
    if raw_date:
        title_wo_date = title.replace(raw_date, "").strip()
    else:
        title_wo_date = title

    # Сколько осталось под основную часть
    if normalized_date:
        reserved = len(normalized_date) + 1  # пробел
    else:
        reserved = 0

    allowed_length = max_length - reserved

    main_part = smart_truncate(title_wo_date, allowed_length)

    if normalized_date:
        return f"{main_part} {normalized_date}".strip()

    return main_part
