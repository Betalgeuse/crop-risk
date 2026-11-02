import unittest
from build import ALL, build


class PublishedTotals(unittest.TestCase):
    def test_crop_payouts_sum_to_published_annual_total(self):
        # 농업정책보험금융원 "농작물재해보험 연도별 지급현황_20241231" (data.go.kr/data/15068602), 지급보험금 in 백만원
        published = {2022: 555_777, 2023: 1_004_249, 2024: 1_020_784}
        rows = build()
        for year, million in published.items():
            total = sum(r["payout_krw"] for r in rows if r["row_kind"] == "crop_year" and r["year"] == year)
            self.assertAlmostEqual(total / 1_000_000, million, delta=1, msg=str(year))


if __name__ == "__main__":
    unittest.main()
