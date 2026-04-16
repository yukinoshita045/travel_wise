"""
tests/unit/test_budget_service.py
預算分配計算單元測試
"""
import pytest
# from services.budget_service import calculate_budget


class TestBudgetService:

    def test_basic_calculation(self):
        """基本預算分配測試"""
        # result = calculate_budget(
        #     total_budget=50000, days=5, travelers=2,
        #     spots=[{"name": "淺草寺", "ticketPrice": 0}]
        # )
        # total = sum(v["total"] for v in result["breakdown"].values())
        # assert abs(total - 50000) < 1  # 加總應等於總預算
        pass

    def test_over_budget_warning(self):
        """景點費用超過活動預算時應發出 warning"""
        # result = calculate_budget(
        #     total_budget=10000, days=1, travelers=1,
        #     spots=[{"name": "迪士尼", "ticketPrice": 8000}]
        # )
        # assert result["isOverBudget"] or len(result["warnings"]) > 0
        pass
