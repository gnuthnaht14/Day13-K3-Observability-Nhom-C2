from app.metrics import percentile, record_error, record_request, snapshot


def test_percentile_basic() -> None:
    assert percentile([100, 200, 300, 400], 50) >= 100


def test_snapshot_error_rate_pct() -> None:
    record_request(100, 0.001, 10, 20, 0.9)
    record_error("ValueError")
    snap = snapshot()
    assert "error_rate_pct" in snap
    assert snap["error_rate_pct"] > 0.0


