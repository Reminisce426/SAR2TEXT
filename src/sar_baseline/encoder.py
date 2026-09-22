from pathlib import Path


class OpenCLIPEncoder:
    def __init__(self, model_config):
        try:
            import open_clip
            import torch
        except ImportError as error:
            raise RuntimeError(
                "OpenCLIP runtime is unavailable. Install the pinned dependencies in the DBCloud environment."
            ) from error

        weight_path = Path(model_config["pretrained_path"]).expanduser().resolve()
        if not weight_path.is_file():
            raise FileNotFoundError("Offline weight not found: {}".format(weight_path))
        self.torch = torch
        self.device = torch.device(model_config["device"])
        if self.device.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested but is unavailable")
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            model_config["name"],
            pretrained=str(weight_path),
            device=self.device,
            precision=model_config["precision"],
        )
        self.tokenizer = open_clip.get_tokenizer(model_config["name"])
        self.model.eval()

    def encode_images(self, image_paths, batch_size, num_workers):
        from PIL import Image
        from torch.utils.data import DataLoader, Dataset

        preprocess = self.preprocess

        class ImageDataset(Dataset):
            def __len__(self):
                return len(image_paths)

            def __getitem__(self, index):
                with Image.open(image_paths[index]) as image:
                    return preprocess(image.convert("RGB"))

        loader = DataLoader(
            ImageDataset(),
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=self.device.type == "cuda",
        )
        features = []
        with self.torch.inference_mode():
            for images in loader:
                batch = self.model.encode_image(images.to(self.device, non_blocking=True))
                features.append(self.torch.nn.functional.normalize(batch.float(), dim=-1).cpu())
        return self.torch.cat(features, dim=0)

    def encode_texts(self, texts, batch_size):
        features = []
        with self.torch.inference_mode():
            for start in range(0, len(texts), batch_size):
                tokens = self.tokenizer(list(texts[start : start + batch_size])).to(self.device)
                batch = self.model.encode_text(tokens)
                features.append(self.torch.nn.functional.normalize(batch.float(), dim=-1).cpu())
        return self.torch.cat(features, dim=0)
