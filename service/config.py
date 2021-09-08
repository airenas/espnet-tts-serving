from typing import List

import yaml

from service.api.api import ModelInfo
from service.espnet.model import extract_model


def load_yaml(stream):
    return yaml.safe_load(stream)


class VoiceConfig:
    def __init__(self, name, device, file):
        self.name = name
        self.device = device
        self.file = file


def parse(data_loaded, def_device) -> dict:
    res = dict()
    for c in data_loaded["voices"]:
        vc = VoiceConfig(c["name"], c["device"], c["file"])
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
