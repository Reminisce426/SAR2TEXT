import json
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


def load_config(path):
    path = Path(path).expanduser().resolve()
    with path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    missing = sorted(REQUIRED_TOP_LEVEL - set(config))
    if missing:
        raise ValueError("Missing config keys: {}".format(", ".join(missing)))
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
    ks = config["evaluation"]["recall_ks"]
    if not ks or any(not isinstance(k, int) or k <= 0 for k in ks):
        raise ValueError("evaluation.recall_ks must contain positive integers")
    config["_config_path"] = str(path)
    return config
