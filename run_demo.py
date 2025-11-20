#!/usr/bin/env python3
"""
Omniverse Market API Demo Script
Author: Abhi
Email: dankalu.work@gmail.com

A simple demonstration script that loads sample market data and performs
basic prediction analysis. This is for demo purposes only and should not
be used for actual trading decisions.
"""

import json
import statistics
from datetime import datetime
from typing import Dict, List, Tuple


def load_sample_data() -> Dict:
    """Load sample market data from JSON file."""
    try:
        with open("data/sample_timeseries.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: sample_timeseries.json not found. Run 'make gen-sample' first.")
        return {}


def calculate_price_trend(timeseries: List[Dict]) -> Tuple[float, str]:
    """
    Calculate simple price trend from timeseries data.

    Returns:
        Tuple of (trend_strength, trend_direction)
    """
    if len(timeseries) < 2:
        return 0.0, "insufficient_data"

    prices = [point["price"] for point in timeseries]

    # Calculate simple linear trend
    n = len(prices)
    x_values = list(range(n))

    # Simple linear regression slope
    x_mean = statistics.mean(x_values)
    y_mean = statistics.mean(prices)

    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, prices))
    denominator = sum((x - x_mean) ** 2 for x in x_values)

    if denominator == 0:
        return 0.0, "flat"

    slope = numerator / denominator

    # Determine trend direction and strength
    if abs(slope) < 0.001:
        return abs(slope), "flat"
    elif slope > 0:
        return slope, "upward"
    else:
        return abs(slope), "downward"


def calculate_volatility(timeseries: List[Dict]) -> float:
    """Calculate price volatility (standard deviation of returns)."""
    if len(timeseries) < 2:
        return 0.0

    prices = [point["price"] for point in timeseries]
    returns = []

    for i in range(1, len(prices)):
        if prices[i - 1] != 0:
            return_rate = (prices[i] - prices[i - 1]) / prices[i - 1]
            returns.append(return_rate)

    if not returns:
        return 0.0

    return statistics.stdev(returns) if len(returns) > 1 else 0.0


def simple_prediction(market: Dict, timeseries: List[Dict]) -> Dict:
    """
    Generate a simple prediction based on trend and volatility.

    WARNING: This is a toy implementation for demo purposes only!
    Do not use for actual trading decisions.
    """
    current_price = market["outcomes"][0]["price"]  # Assume first outcome is "Yes"

    trend_strength, trend_direction = calculate_price_trend(timeseries)
    volatility = calculate_volatility(timeseries)

    # Simple prediction logic (demo only!)
    confidence = 0.5  # Base confidence

    if trend_direction == "upward":
        predicted_direction = "increase"
        confidence += min(trend_strength * 100, 0.3)
    elif trend_direction == "downward":
        predicted_direction = "decrease"
        confidence += min(trend_strength * 100, 0.3)
    else:
        predicted_direction = "stable"

    # Adjust confidence based on volatility (higher volatility = lower confidence)
    confidence = max(0.1, confidence - (volatility * 2))
    confidence = min(0.9, confidence)

    return {
        "market_id": market["id"],
        "current_price": current_price,
        "predicted_direction": predicted_direction,
        "confidence": round(confidence, 3),
        "trend_strength": round(trend_strength, 6),
        "volatility": round(volatility, 4),
        "recommendation": "DEMO ONLY - NOT FOR TRADING",
    }


def main():
    """Run the demo prediction analysis."""
    print("=" * 60)
    print("Omniverse Market API - Demo Prediction Script")
    print("Author: Abhi (dankalu.work@gmail.com)")
    print("=" * 60)
    print()

    # Load sample data
    print("Loading sample market data...")
    data = load_sample_data()

    if not data:
        return

    markets = data.get("markets", [])
    timeseries_data = data.get("timeseries", {})

    print(f"Loaded {len(markets)} markets with timeseries data")
    print()

    # Analyze each market
    for market in markets:
        market_id = market["id"]
        timeseries = timeseries_data.get(market_id, [])

        print(f"Market: {market['title']}")
        print(f"ID: {market_id}")
        print(f"Provider: {market['provider']}")
        print(f"Category: {market['category']}")
        print()

        if timeseries:
            prediction = simple_prediction(market, timeseries)

            print("Prediction Analysis (DEMO ONLY):")
            print(f"  Current Price: {prediction['current_price']}")
            print(f"  Predicted Direction: {prediction['predicted_direction']}")
            print(f"  Confidence: {prediction['confidence']}")
            print(f"  Trend Strength: {prediction['trend_strength']}")
            print(f"  Volatility: {prediction['volatility']}")
            print(f"  Recommendation: {prediction['recommendation']}")
        else:
            print("No timeseries data available for prediction")

        print("-" * 50)
        print()

    print("Demo completed!")
    print()
    print("IMPORTANT DISCLAIMER:")
    print("This is a demonstration script with toy prediction logic.")
    print("Do NOT use these predictions for actual trading or investment decisions.")
    print("Always conduct proper research and risk assessment before trading.")


if __name__ == "__main__":
    main()
