"""Random but valid netlists for layout stress tests."""
import random

from wirediag.model import Wire


def random_netlist(seed: int, n_parts: int = 6, n_wires: int = 18) -> list[Wire]:
    rnd = random.Random(seed)
    parts = ["MCU"] + [f"P{i}" for i in range(1, n_parts)]
    wires, used = [], set()
    pin_net = {}
    nets = ["+3V3", "GND", "+5V"] + [f"SIG{i}" for i in range(n_wires)]
    kinds = {"+3V3": "power", "+5V": "power", "GND": "ground"}
    row = 0
    tries = 0
    while len(wires) < n_wires and tries < 2000:
        tries += 1
        a = "MCU" if rnd.random() < 0.7 else rnd.choice(parts[1:])
        b = rnd.choice([p for p in parts if p != a])
        net = rnd.choice(nets[:3]) if rnd.random() < 0.4 else rnd.choice(nets[3:])
        pa = net if net in kinds else f"IO{rnd.randint(0, 12)}"
        pb = net if net in kinds else f"X{rnd.randint(0, 3)}"
        if pin_net.get((a, pa), net) != net or pin_net.get((b, pb), net) != net:
            continue
        key = (a, pa, b, pb)
        if key in used or (b, pb, a, pa) in used:
            continue
        used.add(key)
        pin_net[(a, pa)] = net
        pin_net[(b, pb)] = net
        row += 1
        wires.append(Wire(row, a, pa, b, pb, net, kinds.get(net, "signal"), ""))
    return wires
