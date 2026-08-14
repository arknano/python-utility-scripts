# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pillow",
#   "piexif",
# ]
# ///

"""Convert image files in the current folder to a requested format."""

import os
import sys
from pathlib import Path

import piexif
from PIL import Image


FORMAT_ALIASES = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "tif": "TIFF",
    "tiff": "TIFF",
}


def save_formats() -> dict[str, list[str]]:
    Image.init()
    formats: dict[str, list[str]] = {}
    for extension, image_format in Image.registered_extensions().items():
        if image_format not in Image.SAVE:
            continue
        formats.setdefault(image_format, []).append(extension.lstrip("."))
    return dict(sorted(formats.items()))


def print_formats() -> None:
    print("Usage: uv run convert_images.py <format>")
    print()
    print("Valid formats:")
    for image_format, extensions in save_formats().items():
        print(f"  {image_format.lower():<8} {', '.join(sorted(extensions))}")


def resolve_format(format_name: str) -> tuple[str, str]:
    normalized = format_name.strip().lower().lstrip(".")
    image_format = FORMAT_ALIASES.get(normalized, normalized.upper())
    formats = save_formats()

    if image_format in formats:
        return image_format, sorted(formats[image_format])[0]

    for candidate_format, extensions in formats.items():
        if normalized in extensions:
            return candidate_format, normalized

    raise ValueError(f"'{format_name}' is not a valid output format")


def image_for_format(image: Image.Image, image_format: str) -> Image.Image:
    if image_format == "JPEG" and image.mode in {"RGBA", "LA", "P"}:
        return image.convert("RGB")
    return image


def save_options(image_format: str) -> dict[str, object]:
    if image_format == "WEBP":
        return {"lossless": False, "quality": 100}
    if image_format == "JPEG":
        return {"quality": 100}
    return {}


def convert_images(image_format: str, extension: str) -> int:
    converted = 0
    current_dir = Path.cwd()

    for path in current_dir.iterdir():
        if not path.is_file() or path.name == Path(__file__).name:
            continue

        output_path = path.with_suffix(f".{extension}")
        if output_path.resolve() == path.resolve():
            continue

        try:
            with Image.open(path) as image:
                if "exif" in image.info:
                    piexif.remove(str(path))
                output_image = image_for_format(image, image_format)
                output_image.save(output_path, format=image_format, **save_options(image_format))
                converted += 1
        except Exception as e:
            print(f"Failed to process '{path.name}': {e}")

    return converted


def main() -> int:
    if len(sys.argv) != 2:
        print_formats()
        return 0

    try:
        image_format, extension = resolve_format(sys.argv[1])
    except ValueError as e:
        print(e)
        print()
        print_formats()
        return 2

    converted = convert_images(image_format, extension)
    print(f"Converted {converted} file(s) to {extension}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
