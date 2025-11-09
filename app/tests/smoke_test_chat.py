import requests

def test_chat_endpoint():
    payload = {"question": "Hi", "model": "gemini-2.5-flash", "session_id": "smoke-1"}
    try:
        response = requests.post("http://127.0.0.1:8000/chat", json=payload, timeout=10)
        assert response.status_code == 200
        data = response.json()
        print("FastAPI /chat endpoint working correctly")
        print("Model response:", data.get("response", "<no response>")[:200])
    except AssertionError:
        print(f"Chat endpoint returned {response.status_code}")
    except Exception as e:
        print(f"Error connecting to API: {e}")

if __name__ == "__main__":
    test_chat_endpoint()