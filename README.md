# espnet-tts-serving

![Python](https://github.com/airenas/espnet-tts-serving/workflows/Python/badge.svg) [![Coverage Status](https://coveralls.io/repos/github/airenas/espnet-tts-serving/badge.svg?branch=main)](https://coveralls.io/github/airenas/espnet-tts-serving?branch=main) ![CodeQL](https://github.com/airenas/espnet-tts-serving/workflows/CodeQL/badge.svg)

Serves [EspNET](https://github.com/espnet/espnet) (*version 1*) TTS model file. It is just a pytorch model inference. No special frontend here. Input is a list of phonemes: `{"text":"a <space> b"}`, output is a based64 encoded spectogram prediction: `{"data":"T5CE ...<truncated>... AAA=="}`.

See [deploy/docker-compose](deploy/docker-compose) for deployment sample.

---

## License

Copyright © 2020, [Airenas Vaičiūnas](https://github.com/airenas).

Released under the [The 3-Clause BSD License](LICENSE).

---


