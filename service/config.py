from typing import List

import yaml

from service.api.api import ModelInfo
from service.espnet.model import extract_model
from service.utils import len_fix


def load_yaml(stream):
    return yaml.safe_load(stream)


class VoiceConfig:
    def __init__(self, name, device, file, speed_shift: float = 1, silence_duration=20):
        if speed_shift is None:
            speed_shift = 1.0
        if silence_duration is None:
            silence_duration = 20
        self.name = name
        self.device = device
        self.file = file
        self.speed_shift = speed_shift
        self.silence_duration = len_fix(silence_duration, speed_shift)


def parse(data_loaded, def_device="cpu") -> dict:
    res = dict()
    for c in data_loaded["voices"]:
        vc = VoiceConfig(c["name"], c.get("device"), c["file"], c.get("speedShift"), c.get("silDuration"))
        if not vc.device:
            vc.device = def_device
        vc.device = vc.device.replace("{{device}}", def_device)
        res[c["name"]] = vc
    return res


class Config:
    def __init__(self, yaml_data, device="cpu", extract_func=extract_model):
        data = load_yaml(yaml_data)
        self.voices = parse(data, device)
        for k in self.voices:
            vc = self.voices[k]
            vc.data = extract_func(vc.file)

    def get(self, name) -> VoiceConfig:
        return self.voices.get(name)

    def get_info(self) -> List[ModelInfo]:
        res = list()
        for k in self.voices:
            vc = self.voices[k]
            res.append(ModelInfo(name=vc.name, device=vc.device))
        return res
