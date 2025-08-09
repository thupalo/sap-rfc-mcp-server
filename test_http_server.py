#!/usr/bin/env python3
"""Test script for SAP RFC MCP HTTP Server."""

import json
import time

import requests


def test_http_server():
    """Test the HTTP MCP server endpoints."""
    base_url = "http://127.0.0.1:8000"

    print("Testing SAP RFC MCP HTTP Server...")
    print("=" * 50)

    try:
        # Test root endpoint
        print("\n1. Testing root endpoint:")
        response = requests.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error: {response.text}")

        # Test tools endpoint
        print("\n2. Testing tools endpoint:")
        response = requests.get(f"{base_url}/tools")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            tools = response.json()
            print(f"Available tools: {len(tools)}")
            for tool in tools:
                print(
                    f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}"
                )
        else:
            print(f"Error: {response.text}")

        # Test health endpoint
        print("\n3. Testing health endpoint:")
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Health check: {response.json()}")
        else:
            print(f"Error: {response.text}")

    except requests.exceptions.ConnectionError:
        print(
            "ERROR: Could not connect to the server. Make sure it's running on port 8001."
        )
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    test_http_server()
