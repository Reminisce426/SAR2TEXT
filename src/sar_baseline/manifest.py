import csv
from dataclasses import dataclass
from pathlib import Path


REQUIRED_COLUMNS = ("image_id", "image_path", "caption_id", "caption", "split")


@dataclass(frozen=True)
class CaptionRecord:
    image_id: str
    image_path: str
    caption_id: str
    caption: str
    split: str


@dataclass(frozen=True)
class RetrievalManifest:
    records: tuple
    image_ids: tuple
    image_paths: tuple
    caption_ids: tuple
    captions: tuple
    caption_image_indices: tuple


def load_manifest(csv_path, image_root, split, check_files=True):
    csv_path = Path(csv_path).expanduser().resolve()
    image_root = Path(image_root).expanduser().resolve()
    if not csv_path.is_file():
        raise FileNotFoundError("Manifest not found: {}".format(csv_path))

    selected = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            raise ValueError("Manifest missing columns: {}".format(", ".join(missing)))
        for line_number, row in enumerate(reader, start=2):
            values = {key: (row.get(key) or "").strip() for key in REQUIRED_COLUMNS}
            if values["split"] != split:
                continue
            empty = [key for key, value in values.items() if not value]
            if empty:
                raise ValueError(
                    "Empty value(s) at line {}: {}".format(line_number, ", ".join(empty))
                )
            selected.append(CaptionRecord(**values))

    if not selected:
        raise ValueError("No manifest rows found for split={!r}".format(split))

    image_to_path = {}
    image_ids = []
    image_paths = []
    caption_ids = []
    captions = []
    caption_image_indices = []
    seen_caption_ids = set()

    for record in selected:
        full_path = Path(record.image_path)
        if not full_path.is_absolute():
            full_path = image_root / full_path
        full_path = full_path.resolve()
        normalized_path = str(full_path)

        if record.caption_id in seen_caption_ids:
            raise ValueError("Duplicate caption_id: {}".format(record.caption_id))
        seen_caption_ids.add(record.caption_id)

        if record.image_id in image_to_path:
            index, previous_path = image_to_path[record.image_id]
            if normalized_path != previous_path:
                raise ValueError(
                    "image_id {} maps to multiple paths".format(record.image_id)
                )
        else:
            index = len(image_ids)
            image_to_path[record.image_id] = (index, normalized_path)
            image_ids.append(record.image_id)
            image_paths.append(normalized_path)

        if check_files and not full_path.is_file():
            raise FileNotFoundError("Image not found: {}".format(full_path))
        caption_ids.append(record.caption_id)
        captions.append(record.caption)
        caption_image_indices.append(index)

    return RetrievalManifest(
        records=tuple(selected),
        image_ids=tuple(image_ids),
        image_paths=tuple(image_paths),
        caption_ids=tuple(caption_ids),
        captions=tuple(captions),
        caption_image_indices=tuple(caption_image_indices),
    )
