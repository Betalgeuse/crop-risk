"""Build data/loss-ratio.csv from data/raw/. Deterministic: no clock, no network.

Units in the sources are 백만원 (million KRW); the CSV is in KRW.
premium_krw        = 환급금 차감 후 순보험료 (net premium after refunds; government + farmer share together)
risk_premium_krw   = 위험보험료
loss_ratio         = payout / premium_krw
loss_ratio_official= 손해율 as the source publishes it (payout / 위험보험료 from 2012, payout / 환급금 차감 후 보험료 up to 2011)
farmer_paid_krw, subsidy_krw stay empty: the sources do not split them.
"""
import csv, hashlib, io, json
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path

ROOT = Path(__file__).parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "loss-ratio.csv"
COLUMNS = ["crop", "year", "region", "policies", "premium_krw", "risk_premium_krw", "farmer_paid_krw",
           "subsidy_krw", "payout_krw", "loss_ratio", "loss_ratio_official", "official_denominator",
           "row_kind", "source_url", "source_table", "retrieved_at"]
ALL = "전체"
MILLION = Decimal(1_000_000)


def krw(million):
    return int((Decimal(million) * MILLION).quantize(Decimal(1), rounding=ROUND_HALF_EVEN))


def pct(num, den):
    return str((Decimal(num) / Decimal(den) * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN))


def read_csv(name, manifest):
    entry = manifest[name]
    data = (RAW / name).read_bytes()
    if hashlib.sha256(data).hexdigest() != entry["sha256"]:
        raise SystemExit(f"{name}: sha256 differs from MANIFEST.json")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = data.decode("cp949")
    rows = [{k.strip(): v.strip() for k, v in r.items()} for r in csv.DictReader(io.StringIO(text))]
    return rows, entry


def crop_year_rows(manifest):
    rows = []
    for year in (2022, 2023, 2024):
        src, entry = read_csv(f"items_{year}.csv", manifest)
        for r in src:
            premium, risk, payout = krw(r["환급금 차감 후 순보험료"]), krw(r["위험보험료"]), krw(r["보험금"])
            official = pct(payout, risk)
            if abs(Decimal(official) - Decimal(r["손해율"])) > max(Decimal("0.06"), Decimal(r["손해율"]) / 500):
                raise SystemExit(f"{year} {r['품목']}: computed {official} vs published {r['손해율']}")
            rows.append(dict(
                crop=r["품목"], year=year, region="", policies=int(Decimal(r["가입건수"])),
                premium_krw=premium, risk_premium_krw=risk, farmer_paid_krw="", subsidy_krw="",
                payout_krw=payout, loss_ratio=pct(payout, premium), loss_ratio_official=official,
                official_denominator="위험보험료", row_kind="crop_year",
                source_url=entry["url"], source_table=f"{entry['dataset_title']} / 품목 행 '{r['품목']}'",
                retrieved_at=entry["retrieved_at"]))
    return rows


def aggregate_rows(manifest, crop_rows):
    rows = []
    for year in (2022, 2023, 2024):
        part = [r for r in crop_rows if r["year"] == year]
        premium, risk = sum(r["premium_krw"] for r in part), sum(r["risk_premium_krw"] for r in part)
        payout = sum(r["payout_krw"] for r in part)
        rows.append(dict(
            crop=ALL, year=year, region="", policies=sum(r["policies"] for r in part),
            premium_krw=premium, risk_premium_krw=risk, farmer_paid_krw="", subsidy_krw="",
            payout_krw=payout, loss_ratio=pct(payout, premium), loss_ratio_official=pct(payout, risk),
            official_denominator="위험보험료", row_kind="aggregate_sum",
            source_url=part[0]["source_url"], source_table=f"{part[0]['source_table'].split(' / ')[0]} / 품목 행 합계",
            retrieved_at=part[0]["retrieved_at"]))
    src, entry = read_csv("yearly_payout.csv", manifest)
    for r in src:
        year = int(r["연도"][:4])
        if year >= 2022:
            continue
        payout, ratio = krw(r["지급보험금"]), Decimal(r["손해율"])
        denominator = int((Decimal(payout) / ratio * 100).quantize(Decimal(1), rounding=ROUND_HALF_EVEN))
        before_2012 = year <= 2011
        rows.append(dict(
            crop=ALL, year=year, region="", policies="", premium_krw=denominator if before_2012 else "",
            risk_premium_krw="" if before_2012 else denominator, farmer_paid_krw="", subsidy_krw="",
            payout_krw=payout, loss_ratio=r["손해율"], loss_ratio_official=r["손해율"],
            official_denominator="환급금 차감 후 보험료" if before_2012 else "위험보험료",
            row_kind="aggregate_derived", source_url=entry["url"], source_table=entry["dataset_title"],
            retrieved_at=entry["retrieved_at"]))
    return rows


def build():
    manifest = {m["file"]: m for m in json.loads((RAW / "MANIFEST.json").read_text(encoding="utf-8"))}
    crops = crop_year_rows(manifest)
    rows = aggregate_rows(manifest, crops) + crops
    rows.sort(key=lambda r: (r["crop"] != ALL, r["crop"], r["year"]))
    return rows


def main():
    rows = build()
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
