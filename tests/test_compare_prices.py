from mcp_servers.procurement.tools.compare_prices import (
    compare_bid_price,
)


def test_alpha_bid_price_is_in_normal_range():
    result = compare_bid_price("BID-ALPHA-001")

    assert result["bid_price"] == 42000000
    assert result["currency"] == "TZS"
    assert result["historical_statistics"]["sample_size"] == 4
    assert result["historical_statistics"]["median"] == 40000000
    assert result["deviation_percentage"] == 5.0
    assert result["risk_level"] == "NORMAL_RANGE"
    assert result["evidence"]


def test_beta_bid_price_is_elevated():
    result = compare_bid_price("BID-BETA-001")

    assert result["bid_price"] == 47000000
    assert result["historical_statistics"]["median"] == 40000000
    assert result["deviation_percentage"] == 17.5
    assert result["risk_level"] == "ELEVATED"
    assert result["sources"]["bid"]
    assert result["sources"]["historical_awards"]