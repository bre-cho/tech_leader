from __future__ import annotations
import json

from _repo_bootstrap import ensure_repo_root_on_path

ensure_repo_root_on_path()

from ai_trading_brain.economic_os.models import EconomicInput
from ai_trading_brain.economic_os import EconomicOSRuntime

if __name__ == "__main__":
    data = EconomicInput(revenue=10000, traffic=20000, leads=1200, customers=80, ad_spend=2500, product_cost=1500)
    report = EconomicOSRuntime().run(data)
    print(json.dumps(report.__dict__, ensure_ascii=False, indent=2))
