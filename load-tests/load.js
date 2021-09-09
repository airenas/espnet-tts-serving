// test acoustic model with several voice parameters
import http from "k6/http";
import { check, sleep } from "k6";
import { SharedArray } from "k6/data";

const prj = "test"
const testURL = 'http://host.docker.internal:8000';

const data = new SharedArray("am data", function() { return JSON.parse(open('/data/data.json')).data; });
const t_len = data.texts.len()
const v_len = Math.min(data.voices.len(), __ENV.VOICES)

function getRandomInt(max) {
  return Math.floor(Math.random() * max);
}

export default function (data) {
    ti = getRandomInt(t_len)
    vi = getRandomInt(v_len)
    var url = testURL;
    var payload = JSON.stringify({
        text: data.texts[ti],
        voice: data.voices[vi],
    });
    var params = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    let res = http.post(url, payload, params);
    check(res, {
        "status was 200": (r) => r.status == 200,
        "transaction time OK": (r) => r.timings.duration < 20000
    });
    sleep(0.1);
}
