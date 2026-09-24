import argparse
import json
import os
from pathlib import Path

from .config import load_config
from .manifest import load_manifest
from .reproducibility import sha256_file


def _check_output_location(output_dir):
    output_dir = Path(output_dir)
    if output_dir.exists() and not output_dir.is_dir():
        raise NotADirectoryError("output_dir is not a directory: {}".format(output_dir))

    existing_parent = output_dir
    while not existing_parent.exists() and existing_parent != existing_parent.parent:
        existing_parent = existing_parent.parent
    if not existing_parent.is_dir() or not os.access(existing_parent, os.W_OK):
        raise PermissionError(
            "No writable parent directory for output_dir: {}".format(output_dir)
        )
    return existing_parent


def check_offline_inputs(config):
    """Validate local inputs without importing or initializing the model runtime."""
    data = config["data"]
    manifest = load_manifest(data["manifest"], data["image_root"], data["split"])

    weight_path = Path(config["model"]["pretrained_path"])
    if not weight_path.is_file():
        raise FileNotFoundError("Offline weight not found: {}".format(weight_path))
    actual_weight_hash = sha256_file(weight_path)
    expected_weight_hash = config["model"].get("expected_sha256", "")
    if expected_weight_hash and actual_weight_hash != expected_weight_hash:
        raise ValueError(
            "Weight SHA256 mismatch: expected {}, got {}".format(
                expected_weight_hash, actual_weight_hash
            )
        )

    output_parent = _check_output_location(config["output_dir"])
    report = {
        "config_path": config["_config_path"],
        "config_sha256": sha256_file(config["_config_path"]),
        "manifest_path": data["manifest"],
        "manifest_sha256": sha256_file(data["manifest"]),
        "image_root": data["image_root"],
        "split": data["split"],
        "image_count": len(manifest.image_ids),
        "caption_count": len(manifest.caption_ids),
        "weight_path": str(weight_path),
        "weight_sha256": actual_weight_hash,
        "weight_hash_expected": bool(expected_weight_hash),
        "output_dir": config["output_dir"],
        "output_existing_parent": str(output_parent),
        "model_runtime_initialized": False,
    }
    return manifest, report


def main():
    parser = argparse.ArgumentParser(
        description="Validate offline baseline inputs before model initialization"
    )
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    _, report = check_offline_inputs(config)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
