import base64
import io
import os
import pathlib
import time
from argparse import Namespace

import torch
from espnet.asr.asr_utils import get_model_conf
from espnet.asr.asr_utils import torch_load
from espnet.utils.dynamic_import import dynamic_import
from fastapi.logger import logger


class Vocab:
    def __init__(self, file):
        if isinstance(file, str) or isinstance(file, pathlib.Path):
            with open(file) as f:
                lines = f.readlines()
        else:
            lines = file.readlines()

        lines = [line.replace("\n", "").split(" ") for line in lines]
        self.char_to_id = {c: int(i) for c, i in lines}
        self.i_dim = len(self.char_to_id) + 2  # start from 0 and + eos

    def map(self, text):
        char_seq = text.split(" ")
        id_seq = []
        for c in char_seq:
            if c.isspace():
                id_seq += [self.char_to_id["<space>"]]
            elif c not in self.char_to_id.keys():
                id_seq += [self.char_to_id["<unk>"]]
            else:
                id_seq += [self.char_to_id[c]]
        id_seq += [self.i_dim - 1]  # <eos>
        return id_seq


class EspNETModel:
    def __init__(self, model_dir, name):
        logger.info("Model path: %s" % model_dir)
        logger.info("Model name: %s" % name)

        dict_path = os.path.join(model_dir, "vocab")
        model_path = os.path.join(model_dir, name)

        self.vocab = Vocab(dict_path)

        self.device = torch.device("cpu")
        i_dim, o_dim, train_args = get_model_conf(model_path)
        if i_dim != self.vocab.i_dim:
            raise Exception("Vocab size %d is not as expected %d" % (self.vocab.i_dim, i_dim))
        model_class = dynamic_import(train_args.model_module)
        model = model_class(i_dim, o_dim, train_args)
        torch_load(model_path, model)
        self.model = model.eval().to(self.device)
        self.inference_args = Namespace(**{"threshold": 0.5, "minlenratio": 0.0, "maxlenratio": 10.0})
        logger.info("Model loaded - now ready to synthesize!")

    def frontend(self, text):
        ids = self.vocab.map(text)
        return torch.LongTensor(ids).view(-1).to(self.device)

    def calculate(self, data):
        with torch.no_grad():
            start = time.time()
            x = self.frontend(data)
            logger.debug(f"x = {x}")
            c, _, _ = self.model.inference(x, self.inference_args)
            am_start = time.time()
            elapsed = (am_start - start)
            logger.info(f"acoustic model done: {elapsed:5f} s")
        buffer = io.BytesIO()
        torch.save(c, buffer)
        buffer.seek(0)
        encoded_data = base64.b64encode(buffer.read())
        return encoded_data.decode('ascii')
