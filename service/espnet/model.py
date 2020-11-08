import base64
import io
import os
import sys
import time
from argparse import Namespace

import torch
from espnet.asr.asr_utils import get_model_conf
from espnet.asr.asr_utils import torch_load
from espnet.utils.dynamic_import import dynamic_import
from fastapi.logger import logger


class EspNETModel:
    def __init__(self, model_dir, name):
        logger.info("Model path: %s" % model_dir)
        logger.info("Model name: %s" % name)

        dict_path = os.path.join(model_dir, "vocab")
        model_path = os.path.join(model_dir, name)

        with open(dict_path) as f:
            lines = f.readlines()

        lines = [line.replace("\n", "").split(" ") for line in lines]
        self.char_to_id = {c: int(i) for c, i in lines}

        self.device = torch.device("cpu")
        self.idim, odim, train_args = get_model_conf(model_path)
        model_class = dynamic_import(train_args.model_module)
        model = model_class(self.idim, odim, train_args)
        torch_load(model_path, model)
        self.model = model.eval().to(self.device)
        self.inference_args = Namespace(**{"threshold": 0.5, "minlenratio": 0.0, "maxlenratio": 10.0})
        logger.info("Model loaded - now ready to synthesize!")

    def frontend(self, text):
        charseq = text.split(" ")
        idseq = []
        for c in charseq:
            if c.isspace():
                idseq += [self.char_to_id["<space>"]]
            elif c not in self.char_to_id.keys():
                idseq += [self.char_to_id["<unk>"]]
            else:
                idseq += [self.char_to_id[c]]
        idseq += [self.idim - 1]  # <eos>
        return torch.LongTensor(idseq).view(-1).to(self.device)

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
