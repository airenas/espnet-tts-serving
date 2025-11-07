import math
from typing import List

import torch
from espnet2.tts.espnet_model import ESPnetTTSModel
from torch import Tensor

from service.api.api import PitchChange, PitchChangeType


class PitchChanger:
    def __init__(self, mu: Tensor, sigma: Tensor):
        self.mu = mu
        self.sigma = sigma

    @classmethod
    def from_tts(cls, model: ESPnetTTSModel):
        pn = model.pitch_normalize
        return cls(mu=pn.mean, sigma=pn.std)

    def apply_pitch_changes(self, x: Tensor, changes: List[List[PitchChange]]) -> Tensor:
        original_shape = x.shape
        x_flat = x.view(-1)
        for i, ch in enumerate(changes):
            xi = self.apply_change(x_flat[i], ch)
            x_flat[i] = xi
        return x_flat.view(original_shape)

    def denormalize_tensor(self, x: torch.Tensor) -> torch.Tensor:
        return x * self.sigma + self.mu

    def denormalize_tensor_to_hz(self, x: torch.Tensor) -> torch.Tensor:
        return torch.exp(x * self.sigma + self.mu)

    def normalize_tensor(self, x: torch.Tensor) -> torch.Tensor:
        return (x - self.mu) / self.sigma

    def normalize_tensor_from_hz(self, x: torch.Tensor) -> torch.Tensor:
        return (torch.log(x) - self.mu) / self.sigma

    def apply_change(self, x: Tensor, ch_list: List[PitchChange]) -> Tensor:
        for ch in ch_list:
            x = self._apply_single_change(x, ch)
        return x

    def _apply_single_change(self, x: Tensor, ch: PitchChange) -> Tensor:
        v = ch.value
        if ch.type == PitchChangeType.MULTIPLIER:
            # x = v * x + (v - 1) * self.mu / self.sigma
            x = x + math.log(v) / self.sigma
        if ch.type == PitchChangeType.SEMITONE:
            x = x + v * math.log(2) / (12 * self.sigma)
        if ch.type == PitchChangeType.HERTZ:
            x = self.normalize_tensor_from_hz(self.denormalize_tensor_to_hz(x) + v)
        return x
