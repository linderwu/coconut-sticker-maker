# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=10"]
# ///
"""Prompt, non-destructive registration and read-only validation of sticker packs."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image

STYLE = """Generate ONE finished coconut-character chat sticker, not a sheet. Use the provided original sketch only for the specified drawing's action/meaning, and the finished reference images only for character style. Lime-green oval/teardrop coconut (golden brown only when explicitly specified), small branch-like limbs, rounded thick black outlines, gentle watercolor texture, cute expressive eyes and blush, generous crisp white die-cut outline around character AND lettering. Match the supplied existing sticker series. OPAQUE PURE BLACK background (#000000), not transparency/checkerboard, no mockup or paper background. Large readable traditional Chinese, rounded bold black strokes with thick white outline, no simplified Chinese. Keep the full body, limbs, props and letters inside the canvas with 6-8% clear black margin on every side. Long edge at least 1024 px. No watermark, page numbers, circled item numbers, dates, notes, unrelated neighboring sketches or labels from the reference sticker. Only one composition in the final image."""


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    ids = [item["id"] for item in data["items"]]
    if ids != list(range(1, len(ids) + 1)):
        raise ValueError("Item ids must be unique and sequential starting at 1")
    return data


def prompt_for(data, item):
    return (f'{STYLE}\nSource drawing: {item["source_id"]}, {item["source_position"]}. '
            f'Scene: {item["scene"]}\nEXACT main display text (verbatim): '
            f'{json.dumps(item["caption"], ensure_ascii=False)}. '
            f'Production constraints, do not print these notes: {item.get("notes", "")}')


def inspect(path):
    with Image.open(path) as image:
        image.load()
        rgb = image.convert("RGB")
        alpha = image.convert("RGBA").getchannel("A")
        borders = [rgb.crop(box).getextrema() for box in (
            (0, 0, image.width, 1), (0, image.height-1, image.width, image.height),
            (0, 0, 1, image.height), (image.width-1, 0, image.width, image.height))]
        return {
            "format": image.format, "width": image.width, "height": image.height,
            "mode": image.mode, "opaque": alpha.getextrema() == (255, 255),
            "black_border": all(high <= 24 for border in borders for low, high in border),
            "nonblank": max(high-low for low, high in rgb.getextrema()) > 100,
            "sha256": digest(path),
        }


def register(path, data, item_id, generated):
    item = next(item for item in data["items"] if item["id"] == item_id)
    target = path.parent / f"{item_id:02}.png"
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite {target}")
    info = inspect(generated)
    if info["format"] != "PNG":
        raise ValueError("Expected actual PNG, not a renamed JPEG/WebP")
    shutil.copy2(generated, target)
    item.update({key: info[key] for key in ("width", "height", "mode", "sha256")})
    item.update(file=target.name, generated_path=str(generated.resolve()),
                prompt=prompt_for(data, item), status="generated", visual_checked=False)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"saved": str(target), **info}, ensure_ascii=False))


def verify(path, data):
    errors, results, hashes = [], [], set()
    source = Path(data["source"])
    if not source.is_file() or digest(source) != data["source_sha256"]:
        errors.append("Source missing or changed")
    expected = {f'{item["id"]:02}.png' for item in data["items"]}
    actual = {p.name for p in path.parent.glob("*.png") if p.stem.isdecimal()}
    if actual != expected:
        errors.append(f"File count/names mismatch: missing={sorted(expected-actual)}, extra={sorted(actual-expected)}")
    for item in data["items"]:
        target = path.parent / f'{item["id"]:02}.png'
        if not target.is_file():
            continue
        try:
            info = inspect(target)
            checks = {
                "PNG": info["format"] == "PNG",
                "size": max(info["width"], info["height"]) >= 1024,
                "nonblank": info["nonblank"],
                "hash": info["sha256"] == item.get("sha256"),
                "unique": info["sha256"] not in hashes,
                "visual_checked": item.get("visual_checked") is True,
                "recorded_name": item.get("file") == target.name,
            }
            if data.get("background") == "black":
                checks.update(opaque=info["opaque"], black_border=info["black_border"])
            hashes.add(info["sha256"])
            errors.extend(f'{target.name}: {key}' for key, passed in checks.items() if not passed)
            results.append({"file": target.name, **info, "checks": checks})
        except (OSError, ValueError) as error:
            errors.append(f"{target.name}: {error}")
    report = {"edition": data["edition"], "expected": len(expected), "present": len(actual),
              "passed": not errors, "errors": errors, "files": results}
    (path.parent / "verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "files"}, ensure_ascii=False))
    return 0 if not errors else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("prompt", "record", "verify"):
        command = sub.add_parser(name)
        command.add_argument("manifest", type=Path)
        if name != "verify":
            command.add_argument("id", type=int)
        if name == "record":
            command.add_argument("generated", type=Path)
    args = parser.parse_args()
    data = load(args.manifest)
    if args.command == "verify":
        return verify(args.manifest, data)
    if args.command == "record":
        register(args.manifest, data, args.id, args.generated)
    else:
        item = next(item for item in data["items"] if item["id"] == args.id)
        print(prompt_for(data, item))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
