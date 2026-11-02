# Crop and parametric risk: data and prior-art map (SNR-31)

Researched 2026-11-03. Read-only web research. Tags: PRIMARY = official site, repo, or the file itself; SECONDARY = news, summaries, search-engine text, or a fetch tool's paraphrase. Anything marked VERIFIED LIVE I downloaded or called myself in this session. Anything marked UNREAD I could not open.

Method note: WebFetch returns a small model's paraphrase of the page, so I treat it as SECONDARY unless I confirmed it by downloading the file or calling the API with curl or gh.

## Bottom line

- Single best source for premiums and payouts by year: data.go.kr file 15068602 (payouts, 2001-2024) joined with file 15068600 (premiums, 2001-2024), both from 농업정책보험금융원 (APFS). PRIMARY, VERIFIED LIVE (downloaded, 24 rows each). Joining them reproduces the published 손해율 exactly (table below).
- GAP: the by-crop file (15126188) and by-province file (15126185) are one-year snapshots (2024), not panels. No crop x year x region panel exists on data.go.kr that I could find. Getting one probably means APFS statistical yearbooks (UNREAD, see section A1) or a data request. This limits the premium-gap note to national-by-year plus a 2024 crop cross-section.
- Honest-backtest has real prior art to borrow for PBO and DSR. mlfinlab is NOT usable (proprietary licence). No TLA+ spec of backtest correctness found; one 2026 paper formalises look-ahead-freedom with a type system instead.
- No open-source parametric or index-insurance pricer of substance found on GitHub. Hits are toys (0-3 stars). CLIMADA is the only serious open framework, and it is GPL-3.0.

---

## A. Public data

### A1. 농작물재해보험 statistics

All four APFS files: provider 농업정책보험금융원 (APFS); format CSV; encoding CP949 (not UTF-8; use `encoding="cp949"`); licence field "이용허락범위 제한 없음" (no restriction); no API key and no login (download only); updated yearly each December with prior-year-end figures; registered 2025-12-18 or 2025-12-22. Metadata PRIMARY (data.go.kr page and its JSON), file contents VERIFIED LIVE.

| ID | Title | URL | Granularity | Years | Rows |
|---|---|---|---|---|---|
| 15068602 | 연도별 지급현황 | https://www.data.go.kr/data/15068602/fileData.do | national x year | 2001-2024 | 24 |
| 15068600 | 연도별 가입 현황 | https://www.data.go.kr/data/15068600/fileData.do | national x year | 2001-2024 | 24 |
| 15126188 | 품목별 가입 및 지급현황 | https://www.data.go.kr/data/15126188/fileData.do | crop item, ONE year (file name suffix _20241231) | 2024 only | 87 (76 items in 2025 per description, plus 시설 sub-items) |
| 15126185 | 시도별 가입 및 지급현황 | https://www.data.go.kr/data/15126185/fileData.do | province, ONE year (_20241231) | 2024 only | 18 (national + 17 provinces) |

Columns (verified from the downloaded files):
- 15068602: 연도, 지급건수, 지급보험금 (million KRW), 손해율 (%).
- 15068600: 연도, 가입농가수, 가입건수, 가입금액, 가입면적(ha), 면적가입률, 순보험료, 국고, 시도, 시군구, 농가부담, 위험보험료 (all money in million KRW).
- 15126188 and 15126185: 대상면적, 가입농가수, 가입건수, 가입농지수, 가입금액, 가입면적, 가입률, 순보험료, 순환급금, 환급금 차감 후 순보험료, 위험보험료, 보험료율, 지급건수, 보험금, 손해율. The description says area in ha, money amounts in won, premiums and refunds in million won. Check units before dividing (my read of the 2024 rows: 보험금 looks like million KRW; the gross 2024 row shows 1,020,784, which matches the yearly file).

Key finding, VERIFIED by computing it: 손해율 = 지급보험금 / 위험보험료 (risk premium), NOT payout / 순보험료. Every year 2001-2024 matches to 0.1 point. Any "premium gap" metric must say which premium it uses.

Joined yearly table (million KRW). Payout from 15068602, risk premium from 15068600. LR = reported 손해율.

| Year | Payout | Risk premium | LR % |
|---|---|---|---|
| 2001 | 1,379 | 3,016 | 45.7 |
| 2002 | 34,709 | 8,008 | 433.5 |
| 2003 | 50,018 | 17,202 | 290.8 |
| 2004 | 13,599 | 32,143 | 42.3 |
| 2005 | 23,871 | 54,847 | 43.5 |
| 2006 | 21,112 | 57,627 | 36.6 |
| 2007 | 61,464 | 55,670 | 110.4 |
| 2008 | 24,932 | 55,423 | 45.0 |
| 2009 | 66,176 | 62,524 | 105.8 |
| 2010 | 90,330 | 86,357 | 104.6 |
| 2011 | 132,628 | 111,004 | 119.5 |
| 2012 | 490,978 | 137,477 | 357.1 |
| 2013 | 45,088 | 205,712 | 21.9 |
| 2014 | 144,978 | 216,632 | 66.9 |
| 2015 | 52,444 | 288,028 | 18.2 |
| 2016 | 106,904 | 323,221 | 33.1 |
| 2017 | 279,673 | 314,152 | 89.0 |
| 2018 | 534,450 | 518,038 | 103.2 |
| 2019 | 898,048 | 482,227 | 186.2 |
| 2020 | 1,015,827 | 674,740 | 150.6 |
| 2021 | 573,989 | 773,471 | 74.2 |
| 2022 | 555,777 | 855,316 | 65.0 |
| 2023 | 1,004,249 | 936,018 | 107.3 |
| 2024 | 1,020,784 | 1,042,753 | 97.9 |

Read this as a national aggregate only. It mixes products (fruit, field crops, greenhouse, rice) whose mix changed a lot over 24 years, so a loss-ratio trend across it is confounded by scope expansion.

Other sources checked:
- 농림축산식품부 년도별 농작물 보험금지급 통계정보 (파일), https://www.data.go.kr/data/15129624/fileData.do. PRIMARY page, WebFetch paraphrase only (not downloaded). Annual national payouts and loss ratio, system since 2001, licence KOGL Type 1 (attribution), registered 2024-07-08, modified 2025-09-05. Likely duplicates APFS 15068602; not compared.
- 농림축산식품부 농업재해정보 (disaster events by year and serial number, start and end dates), data.go.kr, SECONDARY (seen only in search-result text, not opened). Useful as an event list for basis-risk work. I did not capture the dataset ID or confirm it exists in that form.
- APFS site apfs.kr: UNREAD. The fetch tool only reached search snippets, and I could not confirm a statistics room or yearbook there. Do not assume a per-crop-per-year panel is published; check by hand.
- 국회예산정책처 (NABO) 재난안전 관리 현황과 주요 대책 분석 V: 재난보험 운영실태와 재정운용 분석, 2017.10, https://www.nabo.go.kr/board/file/down.do?fid=33314430. PRIMARY, PDF downloaded and text extracted (about 3,800 lines). It models the national reinsurance fiscal loss by fitting exponential and mixed-gamma distributions to historical loss ratios and simulating. Its note puts the annual expected fiscal loss for crop insurance at 251 to 549 억원 depending on method (269 억원 in the headline estimate). Direct prior art for the premium-gap note and for a "measured risk" framing. I read only the summary pages, not the appendix.
- KREI repository (repository.krei.re.kr) hosts crop-insurance evaluation reports, including 제1차 농업재해보험 기본계획 (2023-2027) policy research. SECONDARY (seen in search results only; not opened).
- News claims (e.g. 2012 loss ratio 357%): matches the official file above. Other news figures (e.g. 9,439억 premium cited in a 2021 article) not reconciled; SECONDARY, do not use.

### A2. 기상청 ASOS daily station data

Two routes:

1. data.go.kr OpenAPI 기상청_지상(종관, ASOS) 일자료 조회서비스, ID 15059093, https://www.data.go.kr/data/15059093/openapi.do.
   - Endpoint: https://apis.data.go.kr/1360000/AsosDalyInfoService/getWthrDataList. VERIFIED LIVE that the endpoint exists and rejects a keyless call with SERVICE_KEY_IS_NULL, so a key is required (free serviceKey from data.go.kr).
   - Format JSON or XML. Granularity: daily by station. Fields include temperature (min, max, mean), precipitation, wind, humidity, pressure, sunshine, solar radiation, soil temperature, snow. Coverage "from 1904, varies by station" (PRIMARY page, WebFetch paraphrase; check per-station start dates yourself).
   - Licence: 출처표시 (attribution required) per the page paraphrase. Daily call limit: page did not state one. Check at key issuance.
2. 기상청 API허브 https://apihub.kma.go.kr. Page is reachable. Requires registration with SMS phone verification (PRIMARY, paraphrase). I could not read the endpoint list, the authKey process, terms of use, or limits. UNREAD. Also the 기상자료개방포털 data.kma.go.kr: not opened.

PIT caveat for honest-backtest: ASOS values can be revised or quality-flagged after first release. The API serves the current version, not first-published vintages. Do not treat it as point-in-time without logging fetch dates.

### A3. NASA POWER

- Daily API: https://power.larc.nasa.gov/api/temporal/daily/point (docs: https://power.larc.nasa.gov/docs/services/api/temporal/daily/).
- VERIFIED LIVE: a keyless call for lon 127.0, lat 36.5, 2024-07-01 to 07-03 returned PRECTOTCORR and T2M_MAX with HTTP 200 and no key. API version v2.10.1; sources MERRA2 and POWER; fill value -999; default time standard LST.
- Coverage from 1981-01-01 to near real time, 0.5 x 0.5 degree grid (docs, PRIMARY, paraphrase). At that resolution one cell spans roughly 50 km, so it will smooth out the localised convective rainfall that drives Korean crop loss. Expect large basis risk versus ASOS for rainfall and wind. That makes it a useful second-source comparison, not a replacement.
- Formats: JSON, CSV, NetCDF, ASCII, ICASA (point only). Point requests up to 20 parameters. HTTP 429 exists for rate limiting; thresholds not read.
- Licence and citation terms: NOT READ. Check the POWER data-use page before publishing derived data.

### A4. Korean yield statistics (통계청 농작물생산조사)

- Existence and access route: SECONDARY. Search results say the time series is on KOSIS (https://kosis.kr), free, no membership needed to view, with .xlsx download, and city/county-level area, production and yield. The statistic is run by the national statistics agency (now named 국가데이터처 in some sources; unverified).
- Not found: the exact KOSIS table ID, which crops are included at city/county level, the first year, and the KOSIS OpenAPI terms. The KOSIS listing page fetch showed no 농작물생산조사 entry. UNREAD. A KOSIS OpenAPI key is needed for programmatic access (general knowledge, unconfirmed here).
- Design note: the survey is sample-based for major crops and administrative for others (SECONDARY). Sample error at county level could be larger than the signal in a basis-risk test. Check the published standard errors first.
- Other data.go.kr crop-production files exist (example: 15131371, barley variety production 2010-2025, 농촌진흥청) but they are variety-level supply, not yield-by-region. Not useful for loss.

---

## B. Prior art

Repo facts below are PRIMARY, VERIFIED LIVE via `gh api` on 2026-11-03. "Last commit" is the default-branch commit date. `pushed_at` is the latest push to any branch and can be later.

### B1. Catastrophe and index-insurance modelling

| Project | URL | Stars | Licence | Last commit (default branch) / pushed_at |
|---|---|---|---|---|
| CLIMADA core | https://github.com/CLIMADA-project/climada_python | 486 | GPL-3.0 | 2026-06-08 / 2026-11-02 |
| CLIMADA petals | https://github.com/CLIMADA-project/climada_petals | 39 | GPL-3.0 | n/a / 2026-10-29 |
| Oasis LMF | https://github.com/OasisLMF/OasisLMF | 171 | BSD-3-Clause | 2026-11-02 / 2026-11-02 |

- CLIMADA (ETH). Borrow: the hazard x exposure x impact-function pattern with probabilistic event sets and a cost-benefit module; the repo layout includes `hazard`, `entity`, `engine`. Its `climada_petals` has a `hazard` and `entity` tree; I did not confirm it has a crop module. Avoid: GPL-3.0 means anything that imports and ships it must be GPL. Fine for a personal portfolio repo, a problem for any code later licensed to an employer. Global 4 km hazard data will not suit Korean county-level basis risk. I did not verify a parametric-payout feature (the README fetch said none is mentioned).
- Oasis LMF. Borrow: the pipeline vocabulary (event, footprint, vulnerability, financial-terms module for deductibles and limits); permissive BSD. Avoid: heavy model-vendor infrastructure; it needs you to bring hazard and vulnerability data, and Python 3.10 or newer plus native tools. Overkill for a payout-vs-loss comparison.
- World Bank and GIIF design material (no code found): "Risk Modeling for Appraising Named Peril Index Insurance Products: A Guide for Practitioners", World Bank, April 2017, authors Mapfumo, Groenendaal, Dugger. Record on openknowledge.worldbank.org (https://openknowledge.worldbank.org/entities/publication/8541baeb-8303-5e77-a6bd-ae8869f465a1) and the GIIF site. SECONDARY (search results only, PDF not read). Borrow: the method outline (index design, payout function calibration, basis-risk measures). I found no GIIF or World Bank open-source design tool; do not claim one exists.
- Open-source parametric pricers: GitHub search turned up only toys or student repos. Examples: edv-sc/WeatherIndexInsurance (1 star, MIT, last push 2018), AIDELabAZ/risk_crop_insurance (3 stars, MIT, 2022). Not read in depth. Treat as "nothing to borrow" until opened.

### B2. Crop models

| Project | URL | Stars | Licence | Last commit / pushed_at |
|---|---|---|---|---|
| DSSAT CSM | https://github.com/DSSAT/dssat-csm-os | 239 | BSD-3-Clause | 2026-10-03 / 2026-10-03 |
| PCSE | https://github.com/ajwdewit/pcse | 294 | EUPL v1.1 (header of LICENSE file; GitHub shows NOASSERTION) | 2026-06-15 / 2026-10-19 |

- DSSAT: Fortran, 45+ crops (README). Borrow: nothing as code; it is the reference for how weather inputs map to simulated yield, and BSD is permissive. Avoid: needs per-site soil and management files and calibrated cultivar parameters that I cannot get for Korean fields; building that is out of scope for a minimal project.
- PCSE/WOFOST: pure Python, modular (README). Borrow: it takes daily weather and crop parameters and gives yield, which makes it a plausible "model-based loss proxy" when actual loss data is thin. Avoid: WOFOST parameters for Korean orchard and field crops, and the cost of calibrating, are unknowns. EUPL 1.1 is copyleft; read it before copying code.
- Neither is needed for the premium-gap note. Consider them only if kr-crop-index-backtest wants a simulated-loss baseline.

### B3. Backtest honesty

Original papers (PRIMARY, abstract pages):
- Bailey, Borwein, López de Prado, Zhu, "The Probability of Backtest Overfitting" (J. Computational Finance 2015): https://papers.ssrn.com/abstract=2326253. Method name: combinatorially symmetric cross-validation (CSCV).
- Bailey and López de Prado, "The Deflated Sharpe Ratio" (J. Portfolio Management 40(5), 2014): https://papers.ssrn.com/abstract=2460551.

Implementations (PRIMARY, gh api):

| Repo | URL | Stars | Licence | pushed_at |
|---|---|---|---|---|
| hudson-and-thames/mlfinlab | https://github.com/hudson-and-thames/mlfinlab | 4,965 | proprietary, "Copyright Protection Notice and Licensing Agreement" (GitHub: NOASSERTION) | 2023-10-02 |
| esvhd/pypbo | https://github.com/esvhd/pypbo | 145 | AGPL-3.0 | 2026-07-06 |
| mnemox-ai/deflated-sharpe | https://github.com/mnemox-ai/deflated-sharpe | 9 | Apache-2.0 | 2026-03-21 |
| eslazarev/purged-cross-validation | https://github.com/eslazarev/purged-cross-validation | 61 | MIT | 2026-10-25 |
| mrbcuda/pbo (R, CRAN `pbo`) | https://github.com/mrbcuda/pbo | 51 | "Other" | 2022-05-26 |
| skfolio/skfolio | https://github.com/skfolio/skfolio | 2,579 | BSD-3-Clause | 2026-10-29 |
| sam31415/timeseriescv | https://github.com/sam31415/timeseriescv | 289 | MIT | 2022-02-15 |

- mlfinlab: the public repo says it "exists for the sole purpose" of issue tracking, and the LICENSE is a proprietary agreement (I read the opening lines). The code is not open. Avoid. The 4,965 stars are from the older open version.
- pypbo: covers PBO, PSR, MinTRL, MinBTL and DSR (README). Good for cross-checking my own implementation. AGPL-3.0 means do not copy into a repo you want to keep non-AGPL; calling it as a test oracle is lighter but still read the licence.
- mnemox-ai/deflated-sharpe: pure Python, zero required dependencies, Apache-2.0, 27 tests claimed (README). Only 9 stars and young: audit the formula against the paper before trusting it.
- Purged and combinatorial CV: skfolio (BSD) is the most maintained general library; eslazarev (MIT) is a focused one. I did not confirm that either implements combinatorial purged CV exactly as in López de Prado's book. Check the docs.
- Recommendation: write DSR and PBO yourself from the two papers (about 100 lines), and use pypbo and mnemox as independent oracles. Two implementations that agree is the "honest" bit.

Point-in-time / no-lookahead frameworks:
- zipline-reloaded (stefan-jansen): https://github.com/stefan-jansen/zipline-reloaded, 1,996 stars, Apache-2.0, pushed 2026-11-02. Event-driven design, which makes lookahead hard by construction; original quantopian/zipline (20,190 stars, Apache-2.0, last push 2024-02-13) is stale. Heavy setup; built around equities bundles, not insurance data.
- vectorbt (9,645 stars, NOASSERTION licence: read it, it has a commercial Pro tier) and backtesting.py (9,180 stars, AGPL-3.0): vectorised, which makes lookahead easy to introduce unless you shift signals. Backtrader (23,643 stars, GPL-3.0, last push 2024-08-19) is largely unmaintained.
- Not found: a maintained library that stores bitemporal data (valid-time vs. knowledge-time) for backtests. For honest-backtest, this means building the as-of data layer yourself. That is the project's most distinctive piece.

### B4. TLA+ or formal spec of backtest or event-time correctness

- No TLA+ spec of backtesting correctness found. A GitHub search for "TLA+ backtest" returned nothing relevant, and a web search turned up only general TLA+ papers.
- Closest: Fonseca, "Look-Ahead-Freedom as Temporal Non-Interference: A Verifiable Correctness Property for Backtesting and Agentic Trading Pipelines", arXiv 2607.04958, submitted 2026-07-06, https://arxiv.org/abs/2607.04958. PRIMARY (arXiv abstract page, fetched). Models look-ahead as non-interference over a time-indexed information lattice, with a linear-time type-and-effect checker for value-independent cases and undecidability for value-dependent ones. No TLA+, Lean or Coq mentioned; no code link on the abstract page. Authors say it was submitted to ACM TOSEM (not yet peer reviewed, as far as I can tell). Borrow: the vocabulary separating a datum's availability time from its reference time. Avoid: treating it as validated.
- Implication: a small TLA+ or property-based model of "a decision at time t reads only facts with availability time <= t" would be new work, not a port. Treat as optional.

---

## C. Recommended minimal stack

### C1. Premium-gap note (농작물재해보험 premiums vs payouts)
- Data: the two yearly APFS files (15068600, 15068602) plus the 2024 crop snapshot (15126188) and province snapshot (15126185). All downloadable without a key.
- Method: pandas only. Show payout / risk premium (the official 손해율) and payout / farmer-paid premium (the farmer's view) side by side, because the official metric hides the subsidy. Fit a heavy-tailed loss-ratio distribution as the NABO 2017 report did (exponential and mixed-gamma) and report tail probabilities, not just means.
- Borrow from B: NABO 2017 simulation approach (A1). Nothing from CLIMADA or Oasis.
- State limits in the note: national aggregate only for the time series; 2012, 2002 and 2019 dominate the tail; product scope changed over time; by-crop panel unavailable.

### C2. kr-crop-index-backtest (weather-index payout vs actual loss, basis risk)
- Data: ASOS daily (15059093, key needed) for the index; NASA POWER as a keyless second weather source; actual loss from the closest available series. Honest problem: the public loss data is national or provincial for one year only. County-level loss must come from 농작물생산조사 yield (A4, table ID not yet found) or a data request to APFS. Decide this before writing code.
- Method: a payout function (trigger, exit, limit) calibrated on a training period; basis risk reported as the correlation between index payout and loss, and as a shortfall measure; compare ASOS vs POWER indexes.
- Borrow from B: concept only from the World Bank 2017 guide (read it first). CLIMADA's impact-function idea if you want a structure, but do not take a GPL dependency. PCSE only if you add a simulated-yield baseline.
- Hard dependency: the A4 gap. Without county-level loss, this project is a method demo on synthetic or proxy loss and must say so.

### C3. honest-backtest (point-in-time, no lookahead, overfitting checks)
- Core: an as-of data layer (every record carries knowledge time and reference time), a runner that refuses to read facts with knowledge time later than the decision time, and a trial log that counts every variant tried.
- Overfitting: DSR and PBO written from the two SSRN papers; cross-check against pypbo (AGPL, test oracle only) and mnemox-ai/deflated-sharpe (Apache-2.0). Purged CV from skfolio or eslazarev.
- Reference design for event-time: zipline-reloaded's event loop as a model, plus the Fonseca vocabulary. Do not depend on mlfinlab.
- Optional: a TLA+ or property-test model of the as-of rule. It would be new; scope it as a stretch.
- Reuse the insurance data as the demo case, with the ASOS revision caveat from A2 stated up front.

---

## Open items (could not read or confirm)
1. apfs.kr statistics pages and yearbooks: UNREAD. Needed to find any crop x year panel.
2. KOSIS 농작물생산조사 table IDs, county coverage, first year, OpenAPI terms: UNREAD.
3. 기상청 API허브 endpoints, terms, rate limits; data.go.kr ASOS daily call limit: UNREAD.
4. NASA POWER licence and citation terms; rate limits: UNREAD.
5. World Bank 2017 guide PDF contents: UNREAD (metadata only).
6. NABO 2017 report: only the summary and loss-simulation notes read; appendix and the crop-insurance chapters not read.
7. Whether 15129624 (농림축산식품부) differs from 15068602: not compared.
8. CLIMADA crop-related modules (petals), and mnemox DSR and eslazarev CV correctness: not tested.
