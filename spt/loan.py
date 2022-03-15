from __future__ import annotations
from typing import Tuple, List
from .http import HTTPClient


class Loan:
    def __init__(self, http: HTTPClient, data: dict):
        self.http = http
        self.data = data

        self.due_at = data.get("due", None)
        self.id = data.get("id", None)
        self.repayment_amount = data.get("repaymentAmount", None)
        self.status = data.get("status", None)
        self.type = data.get("type", None)

    async def pay_off(self) -> Tuple[int, List[Loan]]:
        result = await self.http.loan_pay(self.id)

        return result.get("credits", None), [
            Loan(self.http, x) for x in result["loans"]
        ]
