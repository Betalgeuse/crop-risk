# crop-risk

Korean crop disaster insurance (농작물재해보험), measured from public data only.

**Result.** From 2012 to 2024, payouts were 99.3% of the risk premium (n = 13 years, official loss-ratio basis). The average hides the tail: the single worst year, 2012, reached 357%. By crop (2022–2024, 77 crops with all three years), 24 crops paid out more than they took in (rice 115%, pepper 117%, garlic 123%), while multi-span greenhouses paid out 14.5%. The premium includes the government subsidy.

Read this as: crop risk is **mispriced across crops and concentrated in tail years**. It is not systematically overpriced.

## Reproduce

```sh
python3 fetch.py   # optional: downloads raw files listed in data/raw/MANIFEST.json (no API key)
python3 build.py   # data/raw/* -> data/loss-ratio.csv
python3 stats.py   # every number in NOTES.md
python3 -m pytest -q test_build.py
```

Rebuilding from the raw files gives a byte-identical `data/loss-ratio.csv`. The test checks that per-crop payouts sum to the published yearly totals for 2022, 2023 and 2024.

## Sources

농업정책보험금융원 files on data.go.kr: 품목별 가입 및 지급현황 (15126188; 2022, 2023 and 2024 versions) and 연도별 지급현황 (15068602; 2001–2024). The 2016 농업재해보험연감 is used for definitions only. URLs, retrieval times and sha256 hashes are in `data/raw/MANIFEST.json`.

## Limits

- Per-crop data exists only for 2022–2024, so crops added later have n of 1 or 2.
- The source does not split the farmer-paid premium from the subsidy, so those columns are empty and no split is estimated.
- 2001–2021 national premiums are derived as payout ÷ published ratio and are flagged `aggregate_derived`.
- Realized payouts over a short window are not expected loss, and the ratio is not an insurer margin: it excludes operating cost (fully state-paid), reinsurance and the state's catastrophe backstop.

Full analysis, in Korean: [NOTES.md](NOTES.md). Prior art and data map: [docs/refs.md](docs/refs.md).

## 한국어 요약

공공데이터만으로 농작물재해보험 손해율을 재현했습니다. 2012~2024년 보험금은 위험보험료의 99.3%였고(13개 연도), 2012년 한 해는 357%였습니다. 2022~2024년 품목별로 보면 77개 품목 중 24개는 보험금이 보험료보다 많았고(벼 115%, 고추 117%, 마늘 123%), 연동하우스는 14.5%였습니다. 평균으로는 맞지만 품목 사이와 큰 재해 연도에서 가격이 어긋나 있습니다.

Code: MIT. Data: subject to each source's terms on data.go.kr.
