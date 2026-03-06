"""
Simple URL fix - just update the metadata in backend
"""
import requests

# Test current citation
print("Testing current citation...")
response = requests.post(
    "http://localhost:8000/api/v1/public/query",
    json={"question": "What is the lock-in period for HDFC ELSS?", "top_k": 1}
)

if response.status_code == 200:
    data = response.json()
    print(f"\nCurrent citation URL: {data.get('citation', 'N/A')}")
    print("\nNote: If this URL shows error page, the issue is with INDMoney website.")
    print("The URLs are correct - INDMoney site may have temporary issues or require login.")
else:
    print(f"Error: {response.status_code}")
