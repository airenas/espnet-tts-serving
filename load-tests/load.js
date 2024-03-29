// test acoustic model with several voice parameters
import http from "k6/http";
import { check, sleep } from "k6";
import { SharedArray } from "k6/data";
import { Counter } from 'k6/metrics';

var counter500 = new Counter('status 5xx');
var counter400 = new Counter('status 4xx');

const testURL = __ENV.URL;

const voices = new SharedArray("am voices", function() { return JSON.parse(open(__ENV.DATA_DIR + '/data.json')).data.voices; });
const texts = new SharedArray("am texts", function() { return JSON.parse(open(__ENV.DATA_DIR + '/data.json')).data.texts; });
const t_len = texts.length;
const v_len = Math.min(voices.length, __ENV.VOICES_NUM);

function getRandomInt(max) {
  return Math.floor(Math.random() * max);
}

export default function (data) {
    var ti = getRandomInt(t_len);
    var vi = getRandomInt(v_len);
    var url = testURL;
    var payload = JSON.stringify({
        text: texts[ti],
        voice: voices[vi],
        priority: getRandomInt(100),
    });
    var params = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    let res = http.post(url, payload, params);
    counter500.add(res.status >= 500);
    counter400.add(res.status >= 400 && res.status < 500);
    check(res, {
        "status was 200": (r) => r.status === 200,
        "json ok": (r) => r.json("data") && r.json("data").length > 10000,
        "transaction time OK": (r) => r.timings.duration < 15000
    });
    sleep(0.1);
}
