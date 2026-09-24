import hashlib
import json
import os
import platform
import random
import subprocess
import sys
from pathlib import Path


def sha256_file(path, chunk_size=1024 * 1024):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def set_seed(seed, deterministic):
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import numpy as np

        np.random.seed(seed)
    except ImportError:
        pass
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        if deterministic:
            torch.use_deterministic_algorithms(True, warn_only=True)
            if hasattr(torch.backends, "cudnn"):
                torch.backends.cudnn.benchmark = False
                torch.backends.cudnn.deterministic = True
    except ImportError:
        pass


def _git_snapshot(repository_dir):
    command_prefix = ["git"]
    if repository_dir is not None:
        command_prefix.extend(["-C", str(Path(repository_dir).resolve())])
    try:
        commit = subprocess.run(
            command_prefix + ["rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout.strip()
        status = subprocess.run(
            command_prefix + ["status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout
        return commit, bool(status.strip())
    except (OSError, subprocess.SubprocessError):
        return None, None


def environment_snapshot(repository_dir=None):
    snapshot = {
        "python": sys.version,
        "platform": platform.platform(),
    }
    try:
        import torch

        snapshot.update(
            {
                "torch": torch.__version__,
                "cuda_runtime": torch.version.cuda,
                "cuda_available": torch.cuda.is_available(),
                "cudnn": torch.backends.cudnn.version() if torch.backends.cudnn.is_available() else None,
                "gpus": [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())],
            }
        )
    except ImportError:
        snapshot["torch"] = None
    try:
        import open_clip

        snapshot["open_clip"] = getattr(open_clip, "__version__", "unknown")
    except ImportError:
        snapshot["open_clip"] = None
    git_commit, git_dirty = _git_snapshot(repository_dir)
    snapshot["git_commit"] = git_commit
    snapshot["git_dirty"] = git_dirty
    return snapshot


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
