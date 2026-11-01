"""e01: compliance checklist for a Wi-Fi connected desk gadget (no battery, no adapter, adults) (line E)."""
from common import task_dir
import checklist_match as cm

META = {"id": "e01", "line": "E", "title": "Wi-Fi 桌面摆件合规清单 必含/不得含", "kind": "capability"}
HERE = task_dir(__file__)

# Answer key (independent, by instrument number)
MUST = {
    "RED": r"2014/53/EU", "RED-DA-cyber": r"2022/30", "RoHS": r"2011/65/EU", "WEEE": r"2012/19/EU",
    "GPSR": r"2023/988", "FCC-15C": r"Part 15 Subpart C|15\.247|有意辐射体",
    "UK-RER": r"Radio Equipment Regulations 2017", "UK-PSTI": r"PSTI|Product Security and Telecommunications",
}
MUST_NOT = {
    "EU-EMC": r"2014/30/EU", "UK-EMC": r"Electromagnetic Compatibility Regulations 2016", "LVD": r"2014/35/EU",
    "EU-Battery": r"2023/1542", "Toy": r"2009/48/EC|2025/2509|Toys \(Safety\)", "Reese": r"1263|Reese",
}


def produce(ctx):
    return cm.produce(ctx, HERE / "product.yaml")


def score(ans):
    return cm.score(ans, MUST, MUST_NOT)
