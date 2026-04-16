"""
tests/unit/test_fatigue_service.py
疲勞分析服務單元測試（最優先撰寫，因為是純邏輯運算，不需要外部 API）
"""
import pytest
# from services.fatigue_service import analyze_fatigue, WEIGHTS


class TestFatigueService:

    def test_base_score_red_eye(self):
        """紅眼航班應增加 20 分疲勞"""
        # TODO: 實作 fatigue_service 後取消註解
        # result = analyze_fatigue("Asia/Taipei", "Asia/Taipei", 3.0, is_red_eye=True)
        # assert result["breakdown"]["redEyeScore"] == 20
        pass

    def test_layover_adds_score(self):
        """每次轉機應增加 15 分"""
        # result = analyze_fatigue("Asia/Taipei", "Europe/London", 14.0, layover_count=2)
        # assert result["breakdown"]["layoverScore"] == 30
        pass

    def test_senior_multiplier(self):
        """高齡 + 低運動量旅行者的疲勞係數應為 1.5"""
        # result = analyze_fatigue(
        #     "Asia/Taipei", "America/New_York", 16.0,
        #     travelers=[{"age": 70, "fitnessLevel": "low"}]
        # )
        # assert result["travelers"][0]["multiplier"] == 1.5
        pass

    def test_score_max_100(self):
        """疲勞分數不應超過 100"""
        # result = analyze_fatigue("Asia/Taipei", "America/Los_Angeles", 20.0,
        #                          layover_count=3, is_red_eye=True)
        # assert result["baseScore"] <= 100
        pass
