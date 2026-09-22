import argparse

from .config import load_config
from .manifest import load_manifest


def main():
    parser = argparse.ArgumentParser(description="Validate a retrieval manifest")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    data = config["data"]
    manifest = load_manifest(data["manifest"], data["image_root"], data["split"])
    print("manifest_ok=true")
    print("images={}".format(len(manifest.image_ids)))
    print("captions={}".format(len(manifest.caption_ids)))


if __name__ == "__main__":
    main()
