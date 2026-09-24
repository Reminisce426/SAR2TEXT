import json
import re
from pathlib import Path


REQUIRED_TOP_LEVEL = {
    "experiment_name",
    "seed",
    "deterministic",
    "model",
    "data",
    "evaluation",
    "output_dir",
}

_SHA256_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")


def _require_mapping(config, section):
    value = config.get(section)
    if not isinstance(value, dict):
        raise ValueError("{} must be an object".format(section))
    return value


def _require_non_empty_string(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("{} must be a non-empty string".format(name))


def _require_integer(value, name, minimum):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        comparator = "positive" if minimum == 1 else ">= {}".format(minimum)
        raise ValueError("{} must be a {} integer".format(name, comparator))


def _resolve_local_path(value, config_dir):
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = config_dir / path
    return str(path.resolve())


def load_config(path):
    path = Path(path).expanduser().resolve()
    with path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    if not isinstance(config, dict):
        raise ValueError("Config root must be an object")
    missing = sorted(REQUIRED_TOP_LEVEL - set(config))
    if missing:
        raise ValueError("Missing config keys: {}".format(", ".join(missing)))
    model = _require_mapping(config, "model")
    data = _require_mapping(config, "data")
    evaluation = _require_mapping(config, "evaluation")
    for section, keys in {
        "model": ("name", "pretrained_path", "device", "precision"),
        "data": ("manifest", "image_root", "split"),
        "evaluation": (
            "batch_size",
            "num_workers",
            "query_batch_size",
            "recall_ks",
            "case_top_k",
            "case_count_each",
        ),
    }.items():
        absent = [key for key in keys if key not in config[section]]
        if absent:
            raise ValueError("Missing {} keys: {}".format(section, ", ".join(absent)))

    _require_non_empty_string(config["experiment_name"], "experiment_name")
    _require_integer(config["seed"], "seed", 0)
    if not isinstance(config["deterministic"], bool):
        raise ValueError("deterministic must be a boolean")
    for key in ("name", "pretrained_path", "device", "precision"):
        _require_non_empty_string(model[key], "model.{}".format(key))
    for key in ("manifest", "image_root", "split"):
        _require_non_empty_string(data[key], "data.{}".format(key))
    _require_non_empty_string(config["output_dir"], "output_dir")

    for key in ("batch_size", "query_batch_size", "case_top_k"):
        _require_integer(evaluation[key], "evaluation.{}".format(key), 1)
    for key in ("num_workers", "case_count_each"):
        _require_integer(evaluation[key], "evaluation.{}".format(key), 0)

    ks = evaluation["recall_ks"]
    if not isinstance(ks, list) or not ks or any(
        isinstance(k, bool) or not isinstance(k, int) or k <= 0 for k in ks
    ):
        raise ValueError("evaluation.recall_ks must contain positive integers")
    if len(set(ks)) != len(ks):
        raise ValueError("evaluation.recall_ks must not contain duplicates")

    expected_sha256 = model.get("expected_sha256", "")
    if not isinstance(expected_sha256, str):
        raise ValueError("model.expected_sha256 must be a string")
    expected_sha256 = expected_sha256.strip().lower()
    if expected_sha256 and not _SHA256_PATTERN.fullmatch(expected_sha256):
        raise ValueError("model.expected_sha256 must be empty or 64 hexadecimal characters")
    model["expected_sha256"] = expected_sha256

    config_dir = path.parent
    model["pretrained_path"] = _resolve_local_path(model["pretrained_path"], config_dir)
    data["manifest"] = _resolve_local_path(data["manifest"], config_dir)
    data["image_root"] = _resolve_local_path(data["image_root"], config_dir)
    config["output_dir"] = _resolve_local_path(config["output_dir"], config_dir)
    config["_config_path"] = str(path)
    return config
