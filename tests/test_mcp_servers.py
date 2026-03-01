#!/usr/bin/env python3
"""
Test MCP Servers
"""

import requests
import json
import time


def test_agmarknet_server():
    """Test Agmarknet MCP Server"""
    print("\n" + "=" * 60)
    print("TEST 1: Agmarknet Server")
    print("=" * 60)
    
    base_url = "http://localhost:8001"
    
    # Test health check
    print("\n1. Health Check...")
    response = requests.get(f"{base_url}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test get_mandi_prices
    print("\n2. Get Mandi Prices...")
    payload = {
        "crop": "Tomato",
        "district": "Nashik",
        "state": "Maharashtra"
    }
    response = requests.post(f"{base_url}/get_mandi_prices", json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Success: {result['success']}")
    print(f"Message: {result.get('message')}")
    if result['prices']:
        print(f"Prices found: {len(result['prices'])}")
        print(f"Sample: {json.dumps(result['prices'][0], indent=2)}")
    
    # Test get_nearby_mandis
    print("\n3. Get Nearby Mandis...")
    payload = {
        "district": "Nashik",
        "radius_km": 50
    }
    response = requests.post(f"{base_url}/get_nearby_mandis", json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Success: {result['success']}")
    print(f"Message: {result.get('message')}")
    if result['mandis']:
        print(f"Mandis found: {len(result['mandis'])}")
        print(f"Sample: {json.dumps(result['mandis'][0], indent=2)}")
    
    return response.status_code == 200


def test_weather_server():
    """Test Weather MCP Server"""
    print("\n" + "=" * 60)
    print("TEST 2: Weather Server")
    print("=" * 60)
    
    base_url = "http://localhost:8002"
    
    # Test health check
    print("\n1. Health Check...")
    response = requests.get(f"{base_url}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test get_current_weather
    print("\n2. Get Current Weather...")
    payload = {
        "location": "Nashik, Maharashtra",
        "units": "metric"
    }
    response = requests.post(f"{base_url}/get_current_weather", json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Success: {result['success']}")
    print(f"Location: {result['location']}")
    print(f"Temperature: {result['temperature']}°C")
    print(f"Humidity: {result['humidity']}%")
    print(f"Description: {result['description']}")
    
    # Test get_weather_forecast
    print("\n3. Get Weather Forecast...")
    payload = {
        "location": "Nashik, Maharashtra",
        "days": 3
    }
    response = requests.post(f"{base_url}/get_weather_forecast", json=payload)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Success: {result['success']}")
    print(f"Forecast days: {len(result['forecast'])}")
    if result['forecast']:
        print(f"Sample day: {json.dumps(result['forecast'][0], indent=2)}")
    
    return response.status_code == 200


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("MCP SERVERS TEST")
    print("=" * 60)
    print("\nMake sure MCP servers are running:")
    print("  py scripts/run_mcp_servers.py")
    print("\nWaiting for servers to be ready...")
    
    # Wait for servers to start
    max_retries = 10
    for i in range(max_retries):
        try:
            requests.get("http://localhost:8001/", timeout=1)
            requests.get("http://localhost:8002/", timeout=1)
            print("✓ Servers are ready!\n")
            break
        except:
            if i == max_retries - 1:
                print("✗ Servers not responding. Please start them first.")
                return 1
            time.sleep(1)
    
    # Run tests
    passed = 0
    failed = 0
    
    try:
        if test_agmarknet_server():
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"✗ Agmarknet test failed: {e}")
        failed += 1
    
    try:
        if test_weather_server():
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"✗ Weather test failed: {e}")
        failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total: 2")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n✓ ALL TESTS PASSED - MCP Servers Ready!")
        return 0
    else:
        print(f"\n✗ {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
