"""e02: compliance checklist for a BLE coin-cell children's toy (line E)."""
from common import task_dir
import checklist_match as cm

META = {"id": "e02", "line": "E", "title": "BLE 纽扣电池玩具合规清单 必含/不得含", "kind": "capability"}
HERE = task_dir(__file__)

# Answer key (independent, by instrument number)
MUST = {
    "Reese": r"1263|Reese", "CPSIA/F963": r"CPSIA|F963|Consumer Product Safety Improvement Act",
    "EU-Toy": r"2009/48/EC|2025/2509", "EU-Battery": r"2023/1542", "RED": r"2014/53/EU",
    "RED-DA-cyber": r"2022/30", "FCC-15C": r"Part 15 Subpart C|15\.247|有意辐射体",
    "AU-coin": r"Button/Coin Batter|纽扣/硬币电池",
}
MUST_NOT = {
    "CommonCharger": r"2022/2380", "LVD": r"2014/35/EU", "DOE-EPS": r"430\.32",
    "EU-EMC": r"2014/30/EU", "CyberTrust": r"Cyber Trust",
}


def produce(ctx):
    return cm.produce(ctx, HERE / "product.yaml")


def score(ans):
    return cm.score(ans, MUST, MUST_NOT)
