"""Print the numbers quoted in NOTES.md from data/loss-ratio.csv."""
import csv, statistics
from collections import defaultdict

rows = list(csv.DictReader(open("data/loss-ratio.csv", encoding="utf-8")))
f = lambda x: float(x) if x else None


def agg(label, sel, den=None):
    pay = sum(float(r["payout_krw"]) for r in sel)
    d = sum(float(r["risk_premium_krw"] or r["premium_krw"]) for r in sel)
    rat = [float(r["loss_ratio_official"]) for r in sel]
    print(f"{label}: n={len(sel)} pooled={pay/d*100:.1f}% mean={statistics.mean(rat):.1f} median={statistics.median(rat):.1f} min={min(rat)} max={max(rat)} over100={sum(x>100 for x in rat)}")


A = [r for r in rows if r["crop"] == "전체"]
agg("ALL 2001-2024 (mixed denominator)", A, "premium_krw")
agg("ALL 2012-2024 (위험보험료)", [r for r in A if int(r["year"]) >= 2012], "risk_premium_krw")
agg("ALL 2001-2011 (환급후)", [r for r in A if int(r["year"]) <= 2011], "premium_krw")
print("over100 years", [r["year"] for r in A if float(r["loss_ratio_official"]) > 100])
print("worst/best years", sorted((float(r["loss_ratio_official"]), r["year"]) for r in A)[:3], sorted((float(r["loss_ratio_official"]), r["year"]) for r in A)[-4:])
for y in (2022, 2023, 2024):
    r = [x for x in A if int(x["year"]) == y][0]
    print(y, "premium", r["premium_krw"], "risk", r["risk_premium_krw"], "payout", r["payout_krw"], "lr", r["loss_ratio"], "official", r["loss_ratio_official"])
C = [r for r in rows if r["row_kind"] == "crop_year"]
print("crop-years", len(C), "crops", len({r["crop"] for r in C}))
pay = sum(float(r["payout_krw"]) for r in C); pr = sum(float(r["premium_krw"]) for r in C); rk = sum(float(r["risk_premium_krw"]) for r in C)
print(f"pooled crop-years 2022-24: lr(net after refund)={pay/pr*100:.1f}% official(risk)={pay/rk*100:.1f}%")
lr = [float(r["loss_ratio"]) for r in C]
print("crop-year lr: median", statistics.median(lr), "min", min(lr), "max", max(lr), ">100:", sum(x > 100 for x in lr), "<100:", sum(x < 100 for x in lr), "of", len(lr))
print("premium-weighted share of premium in crop-years with lr>100:", sum(float(r["premium_krw"]) for r in C if float(r["loss_ratio"]) > 100) / pr)
by = defaultdict(list)
for r in C: by[r["crop"]].append(r)
out = []
for c, rs in by.items():
    p = sum(float(r["payout_krw"]) for r in rs); d = sum(float(r["premium_krw"]) for r in rs)
    out.append((d, c, len(rs), p / d * 100, min(float(r["loss_ratio"]) for r in rs), max(float(r["loss_ratio"]) for r in rs), sorted(int(r["year"]) for r in rs)))
out.sort(reverse=True)
print("n=3 crops:", sum(o[2] == 3 for o in out), "n<3:", [(o[1], o[6]) for o in out if o[2] < 3])
print("top 12 by premium:")
for d, c, n, l, lo, hi, ys in out[:12]: print(f"  {c} prem={d/1e8:.0f}억 n={n} pooled={l:.1f}% range {lo}-{hi}")
print("crops with pooled lr>100:", [(o[1], round(o[3])) for o in out if o[3] > 100])
print("share of crops (n=3) pooled lr>100:", sum(o[3] > 100 for o in out if o[2] == 3), "/", sum(o[2] == 3 for o in out))
print("year by year pooled crop-level: ", {y: round(sum(float(r['payout_krw']) for r in C if r['year']==str(y))/sum(float(r['premium_krw']) for r in C if r['year']==str(y))*100,1) for y in (2022,2023,2024)})
