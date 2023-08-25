import base64
import io
import logging
import time

import torch
from espnet2.bin.tts_inference import Text2Speech
from espnet_model_zoo.downloader import ModelDownloader

from service.utils import check_alpha, len_fix_np

logger = logging.getLogger(__name__)


def extract_model(model_zip_path):
    logger.info("Model zip path: %s" % model_zip_path)
    d = ModelDownloader("~/.cache/espnet")
    m_extracted = d.unpack_local_file(model_zip_path)
    logger.info("Model extraction info: %s" % m_extracted)
    return m_extracted


class ESPNetModel:
    def __init__(self, model_data, device, speed_shift: float = 1):
        logger.info("Device: %s" % device)
        logger.info("Model data: %s" % model_data)
        logger.info("Model speed shift: %s" % ("None" if speed_shift is None else format(speed_shift, '.2f')))
        self.tts = Text2Speech(**model_data,
                               device=device,
                               # Only for Tacotron 2\n",
                               threshold=0.5,
                               minlenratio=0.0,
                               maxlenratio=10.0,
                               use_att_constraint=True,
                               backward_window=1,
                               forward_window=3,
                               # Only for FastSpeech & FastSpeech2\n",
                               speed_control_alpha=1.0,
                               )

        self.tts.spc2wav = None  # Disable griffin-lim\n",
        self.tts.vocoder = None
        self.device = torch.device(device)
        self.speed_shift = speed_shift
        logger.info("Model loaded - now ready to synthesize!")

    def calculate(self, data: str, speed_control_alpha: float = None):
        with torch.no_grad():
            start = time.time()
            res = self.tts(text=data,
                           decode_conf={"alpha": check_alpha(speed_control_alpha, self.speed_shift)})
            end = time.time()
            elapsed = (end - start)
            logger.info(f"acoustic model done: {elapsed:5f} s")
        buffer = io.BytesIO()
        torch.save(res["feat_gen"], buffer)
        buffer.seek(0)
        encoded_data = base64.b64encode(buffer.read())
        return {"features": encoded_data.decode('ascii'),
                "durations": len_fix_np(res["duration"].numpy(), speed_control_alpha).tolist()}
