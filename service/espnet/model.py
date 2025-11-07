import base64
import io
import logging
import time
from typing import List

import torch
from espnet2.bin.tts_inference import Text2Speech
from espnet_model_zoo.downloader import ModelDownloader

from service.api.api import PitchChange
from service.espnet.pitch_changer import PitchChanger
from service.utils import check_alpha, len_fix_np, fix_duration

logger = logging.getLogger(__name__)


def extract_model(model_zip_path):
    logger.info("Model zip path: %s" % model_zip_path)
    d = ModelDownloader("~/.cache/espnet")
    m_extracted = d.unpack_local_file(model_zip_path)
    logger.info("Model extraction info: %s" % m_extracted)
    return m_extracted


class CalcResult:
    def __init__(self, features: bytes, durations: list, silent_duration: int = 0):
        self.features = features
        self.durations = durations
        self.silence_duration = silent_duration


class ESPNetModel:
    def __init__(self, config):
        logger.info("Device: %s" % config.device)
        logger.info("Model data: %s" % config.data)
        logger.info(
            "Model speed shift: %s" % ("None" if config.speed_shift is None else format(config.speed_shift, '.2f')))
        logger.info("Model duration fix: %s" % ("None" if config.duration_fix is None else config.duration_fix))
        self.tts = Text2Speech(**config.data,
                               device=config.device,
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
        self.device = torch.device(config.device)
        self.speed_shift = config.speed_shift
        self.duration_fix = config.duration_fix
        self.pitch_changer = PitchChanger.from_tts(self.tts.model)
        logger.info("Model loaded - now ready to synthesize!")

    def calculate(self, data: str, speed_control_alpha: float = None,
                  durations_change: List[float] | None = None,
                  pitch_change: List[List[PitchChange]] | None = None) -> CalcResult:
        alpha = check_alpha(speed_control_alpha, self.speed_shift)
        with torch.no_grad():
            start = time.time()

            def pitch_postprocess_callback(x):
                # logger.info(f"pitch: {x}")
                if pitch_change is not None:
                    # hz = self.pitch_changer.denormalize_tensor_to_hz(x).tolist()
                    # logger.info(f"hz: {hz}")
                    # hz = self.pitch_changer.denormalize_tensor(x).tolist()
                    # logger.info(f"log: {hz}")
                    # logger.info(f"change: {pitch_change}")

                    x = self.pitch_changer.apply_pitch_changes(x, pitch_change)

                    # hz = self.pitch_changer.denormalize_tensor_to_hz(x).tolist()
                    # logger.info(f"after: {hz}")
                    # hz = self.pitch_changer.denormalize_tensor(x).tolist()
                    # logger.info(f"log: {hz}")
                return x

            def duration_postprocess_callback(x):
                if alpha == 1.0 and durations_change is None:
                    return x
                res = x
                # logger.info(f"durations in: {x}")
                # logger.info(f"durations in: {len(durations_change)}")
                if durations_change is not None:
                    dur_tensor = torch.tensor(durations_change + [1], device=x.device)
                    res = x * dur_tensor

                if alpha != 1.0:
                    res = res * alpha
                res = res.round().long()
                # logger.info(f"durations in: {x}")
                # logger.info(f"durations out: {res}")
                return res

            res = self.tts(text=data,
                           decode_conf={"alpha": 1.0,
                                        "pitch_postprocess_callback": pitch_postprocess_callback,
                                        "duration_postprocess_callback": duration_postprocess_callback,
                                        })
            end = time.time()
            elapsed = (end - start)
            logger.info(f"acoustic model done: {elapsed:5f} s")
        buffer = io.BytesIO()
        torch.save(res["feat_gen"], buffer)
        buffer.seek(0)
        calc_res = CalcResult(features=buffer.read(),
                              durations=fix_duration(res["duration"].cpu().numpy(), self.duration_fix).tolist())
        return calc_res
        # encoded_data = base64.b64encode(buffer.read())
        # return {"features": encoded_data.decode('ascii'),
        #         "durations": len_fix_np(res["duration"].cpu().numpy(), alpha, self.duration_fix).tolist()}
