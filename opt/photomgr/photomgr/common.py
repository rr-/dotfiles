import re

RAW_SUFFIXES = {".cr2", ".nef", ".raf"}
JPEG_SUFFIXES = {".jpg", ".jpeg"}

FILENAME_DATE_REGEX = re.compile(
    r"(?P<year>20\d{2})"
    r"(?P<month>\d{2})"
    r"(?P<day>\d{2})"
    r"_"
    r"(?P<hour>\d{2})"
    r"(?P<minute>\d{2})"
    r"(?P<second>\d{2})"
    r"_(?P<device>[^_]+)"
    r"(?:_(?P<discriminator>\d{7}))?"
    r"(?:-(?P<editing_suffix>[^_-]+))?"
    r"(?P<extension>\.\w+)$"
)
