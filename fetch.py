"""Download raw files from data.go.kr into data/raw/ and write MANIFEST.json (url, retrieved_at, sha256)."""
import hashlib, json, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

RAW = Path(__file__).parent / "data" / "raw"
PORTAL = "https://www.data.go.kr"
# (local file, dataset pk, detail uddi, dataset page title)
SOURCES = [
    ("items_2022.csv", "15126188", "uddi:72119382-754e-4ec2-ba3d-da13b5855a32", "농업정책보험금융원_농작물재해보험 품목별 가입 및 지급현황_20221231"),
    ("items_2023.csv", "15126188", "uddi:ecd72bd1-e510-44ec-92d2-9535c01de312", "농업정책보험금융원_농작물재해보험 품목별 가입 및 지급현황_20231231"),
    ("items_2024.csv", "15126188", "uddi:dacc5f91-eff5-4cdf-a1e0-b0d6e5192454", "농업정책보험금융원_농작물재해보험 품목별 가입 및 지급현황_20241231"),
    ("yearly_payout.csv", "15068602", "uddi:eec63e06-4776-4965-a6f4-c76d95b3722b", "농업정책보험금융원_농작물재해보험 연도별 지급현황_20241231"),
]
# fixed URL, used only for definitions (subsidy rate, loss-ratio denominator), not for the CSV
REFERENCE = ("yearbook_2016.pdf", "https://www.mafra.go.kr/bbs/mafra/131/189964/download.do", "2016 농업재해보험연감 (농림축산식품부)")


def post(path, fields):
    body = urllib.parse.urlencode(fields).encode()
    with urllib.request.urlopen(urllib.request.Request(PORTAL + path, data=body), timeout=60) as r:
        return json.load(r)


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    manifest = []
    for name, pk, uddi, title in SOURCES:
        meta = post("/tcs/dss/selectFileDataDownload.do", {
            "publicDataPk": pk, "publicDataDetailPk": uddi, "atchFileId": "",
            "fileDetailSn": "1", "publicDataTyCode": "PR0051"})
        file_id = meta["atchFileId"]
        url = f"{PORTAL}/cmm/cmm/fileDownload.do?atchFileId={file_id}&fileDetailSn=1&dataNm=x"
        retrieved_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with urllib.request.urlopen(url, timeout=120) as r:
            data = r.read()
        (RAW / name).write_bytes(data)
        manifest.append({
            "file": name, "url": url, "dataset_page": f"{PORTAL}/data/{pk}/fileData.do",
            "dataset_title": title, "retrieved_at": retrieved_at,
            "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    name, url, title = REFERENCE
    retrieved_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with urllib.request.urlopen(url, timeout=120) as r:
        data = r.read()
    (RAW / name).write_bytes(data)
    manifest.append({"file": name, "url": url, "dataset_page": url, "dataset_title": title,
                     "retrieved_at": retrieved_at, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    (RAW / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
