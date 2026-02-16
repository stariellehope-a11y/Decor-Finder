"""CLIP embedding service for images and text."""

import io
from typing import Optional

import numpy as np
import open_clip
import torch
from PIL import Image

from app.core.config import get_settings

settings = get_settings()


class EmbeddingService:
    """Generate CLIP embeddings for images and text queries."""

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            settings.clip_model_name, pretrained=settings.clip_pretrained
        )
        self.tokenizer = open_clip.get_tokenizer(settings.clip_model_name)
        self.model.to(self.device)
        self.model.eval()

    def embed_image(self, image_bytes: bytes) -> np.ndarray:
        """Generate embedding from raw image bytes."""
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            embedding = self.model.encode_image(image_tensor)
            embedding = embedding / embedding.norm(dim=-1, keepdim=True)

        return embedding.cpu().numpy().flatten()

    def embed_image_url(self, image_url: str) -> Optional[np.ndarray]:
        """Download image from URL and generate embedding."""
        import httpx

        try:
            response = httpx.get(image_url, timeout=15, follow_redirects=True)
            response.raise_for_status()
            return self.embed_image(response.content)
        except Exception as e:
            print(f"Failed to embed image from {image_url}: {e}")
            return None

    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding from text query."""
        tokens = self.tokenizer([text]).to(self.device)

        with torch.no_grad():
            embedding = self.model.encode_text(tokens)
            embedding = embedding / embedding.norm(dim=-1, keepdim=True)

        return embedding.cpu().numpy().flatten()


# Singleton — model loads once
_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    global _service
    if _service is None:
        _service = EmbeddingService()
    return _service
