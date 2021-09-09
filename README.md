# espnet-tts-serving

![Python](https://github.com/airenas/espnet-tts-serving/workflows/Python/badge.svg) [![Coverage Status](https://coveralls.io/repos/github/airenas/espnet-tts-serving/badge.svg?branch=main)](https://coveralls.io/github/airenas/espnet-tts-serving?branch=main) ![CodeQL](https://github.com/airenas/espnet-tts-serving/workflows/CodeQL/badge.svg)

Serves [ESPnet](https://github.com/espnet/espnet) (*version 2*) TTS model file. It packs the python code into a docker container for running pytorch on CPU/GPU. It is just a pytorch model inference. No special frontend is defined here. Input is a list of phonemes: `{"text":"a <space> b", "voice": "sample.v"}`, output is a based64 encoded spectrogram prediction: `{"data":"T5CE ...<truncated>... AAA=="}`.

## Configuration

The service can load several models. It takes a configuration file as an input. See [deploy/cpu/voices.yaml](deploy/cpu/voices.yaml) as a sample. Service will load a model for a configured voice name, and it will keep it until a request with another voice name will arrive. There is a possibility to load several models into a memory using environment `WORKERS` parameter. 

There is also some load balancer implemented. It tries to keep a model in memory if there are many requests waiting for the same voice.

## Sample usage

See [deploy/cpu](deploy/cpu) or [deploy/gpu](deploy/gpu) for deployment and testing samples.

## ESPnet version 1

For ESPnet (*version 1*) look at [ESPnet1 branch](https://github.com/airenas/espnet-tts-serving/tree/espnet1)

---

## License

Copyright © 2021, [Airenas Vaičiūnas](https://github.com/airenas).

Released under the [The 3-Clause BSD License](LICENSE).

---


