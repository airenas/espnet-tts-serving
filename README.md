# espnet-tts-serving

![Python](https://github.com/airenas/espnet-tts-serving/workflows/Python/badge.svg) [![Coverage Status](https://coveralls.io/repos/github/airenas/espnet-tts-serving/badge.svg?branch=main)](https://coveralls.io/github/airenas/espnet-tts-serving?branch=main) ![CodeQL](https://github.com/airenas/espnet-tts-serving/workflows/CodeQL/badge.svg)

Serves [ESPnet](https://github.com/espnet/espnet) (*version 2*) TTS model file. It packs the python code into a docker container for running pytorch on CPU. It is just a pytorch model inference. No special frontend is defined here. Input is a list of phonemes: `{"text":"a <space> b"}`, output is a based64 encoded spectrogram prediction: `{"data":"T5CE ...<truncated>... AAA=="}`.

See [deploy/docker-compose](deploy/docker-compose) for deployment and testing samples.

For ESPnet (*version 1*) look at [ESPnet1 branch](https://github.com/airenas/espnet-tts-serving/tree/espnet1)

---

## License

Copyright © 2020, [Airenas Vaičiūnas](https://github.com/airenas).

Released under the [The 3-Clause BSD License](LICENSE).

---


