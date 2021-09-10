// test acoustic model live endpoint
import http from "k6/http";
import { check, sleep } from "k6";

const testURL = __ENV.URL;

export default function (data) {
    let res = http.get(testURL);
    check(res, {
        "status was 200": (r) => r.status === 200,
        "transaction time OK": (r) => r.timings.duration < 500
    });
    sleep(0.1);
}
