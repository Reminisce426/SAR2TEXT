import argparse
import copy
from pathlib import Path

from .config import load_config
from .encoder import OpenCLIPEncoder
from .evaluation import evaluate_bidirectional, write_cases
from .manifest import load_manifest
from .reproducibility import environment_snapshot, set_seed, sha256_file, write_json


def main():
    parser = argparse.ArgumentParser(description="Run reproducible bidirectional retrieval")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    output_dir = Path(config["output_dir"]).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    set_seed(config["seed"], config["deterministic"])
    data_config = config["data"]
    manifest = load_manifest(
        data_config["manifest"], data_config["image_root"], data_config["split"]
    )

    weight_path = Path(config["model"]["pretrained_path"]).expanduser().resolve()
    actual_weight_hash = sha256_file(weight_path)
    expected_weight_hash = config["model"].get("expected_sha256", "").strip().lower()
    if expected_weight_hash and actual_weight_hash != expected_weight_hash:
        raise ValueError(
            "Weight SHA256 mismatch: expected {}, got {}".format(
                expected_weight_hash, actual_weight_hash
            )
        )
    fingerprints = {
        "manifest_sha256": sha256_file(data_config["manifest"]),
        "weight_sha256": actual_weight_hash,
        "image_count": len(manifest.image_ids),
        "caption_count": len(manifest.caption_ids),
        "candidate_order": "first appearance in manifest after split filtering",
    }
    persisted_config = copy.deepcopy(config)
    persisted_config.pop("_config_path", None)
    write_json(output_dir / "resolved_config.json", persisted_config)
    write_json(output_dir / "environment.json", environment_snapshot())
    write_json(output_dir / "fingerprints.json", fingerprints)

    encoder = OpenCLIPEncoder(config["model"])
    evaluation_config = config["evaluation"]
    image_features = encoder.encode_images(
        manifest.image_paths,
        evaluation_config["batch_size"],
        evaluation_config["num_workers"],
    )
    text_features = encoder.encode_texts(
        manifest.captions, evaluation_config["batch_size"]
    )
    evaluation = evaluate_bidirectional(
        text_features,
        image_features,
        manifest.caption_image_indices,
        evaluation_config["recall_ks"],
        evaluation_config["query_batch_size"],
        evaluation_config["case_top_k"],
    )
    write_json(output_dir / "metrics.json", evaluation["metrics"])
    write_cases(
        output_dir / "cases.jsonl",
        evaluation,
        manifest,
        evaluation_config["case_count_each"],
    )
    print("Completed: {}".format(output_dir))


if __name__ == "__main__":
    main()
