from cetodex.phase0_gate import run_gate as phase0
from cetodex.laptop_gate import run_all


def test_phase0_gate_passes():
    report = phase0()
    assert report["passed"]


def test_laptop_aggregate_offline():
    report = run_all(offline_recon=True)
    assert report["passed"]
    assert report["subgates"]["phase0"]
