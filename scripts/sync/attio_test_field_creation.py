#!/usr/bin/env python3
"""
Test creating a single field in Attio to debug API issues
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def test_create_field():
    api_key = os.getenv("ATTIO_API_KEY")
    if not api_key:
        print("❌ ATTIO_API_KEY not found")
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Test with a simple text field with all required fields
    test_field = {
        "data": {
            "api_slug": "test_chroma_field",
            "title": "Test Chroma Field",
            "type": "text",
            "description": "Test field for Chroma",
            "is_required": False,
            "is_unique": False,
            "is_multiselect": False,
            "config": {}
        }
    }

    url = "https://api.attio.com/v2/objects/companies/attributes"

    print("📤 Sending request to Attio...")
    print(f"URL: {url}")
    print(f"Headers: Authorization: Bearer {api_key[:10]}...")
    print(f"Body: {json.dumps(test_field, indent=2)}")

    response = requests.post(url, headers=headers, json=test_field)

    print(f"\n📥 Response Status: {response.status_code}")

    if response.status_code == 200 or response.status_code == 201:
        print("✅ Success!")
        print(json.dumps(response.json(), indent=2))
    else:
        print("❌ Failed!")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        # Try to parse error details
        try:
            error = response.json()
            print("\nError details:")
            print(json.dumps(error, indent=2))
        except:
            pass

if __name__ == "__main__":
    test_create_field()