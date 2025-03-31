import requests

def test_stock_adjustment():
    try:
        response = requests.post(
            'http://127.0.0.1:8001/api/stock/adjust/85',
            json={
                'action': 'subtract',
                'quantity': 1,
                'reason': 'Test order completed'
            },
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_stock_adjustment() 