import base64
import io
import logging
import time

import torch
from espnet2.bin.tts_inference import Text2Speech
from espnet_model_zoo.downloader import ModelDownloader

logger = logging.getLogger(__name__)


class ESPNetModel:
    def __init__(self, model_zip_path, device):
        logger.info("Model zip path: %s" % model_zip_path)
        logger.info("Device: %s" % device)

        d = ModelDownloader("~/.cache/espnet")
        m_extracted = d.unpack_local_file(model_zip_path)
        logger.info("Model extraction info: %s" % m_extracted)
        self.tts = Text2Speech(**m_extracted,
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
        self.device = torch.device(device)
        logger.info("Model loaded - now ready to synthesize!")

    def calculate(self, data):
        with torch.no_grad():
            start = time.time()
            _, y, *_ = self.tts(data)
            end = time.time()
            elapsed = (end - start)
            logger.info(f"acoustic model done: {elapsed:5f} s")
        buffer = io.BytesIO()
        torch.save(y, buffer)
        buffer.seek(0)
        encoded_data = base64.b64encode(buffer.read())
        return encoded_data.decode('ascii')
