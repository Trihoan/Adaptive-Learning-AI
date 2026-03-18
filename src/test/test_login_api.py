import httpx
import time

def test_login(username, password):
    url = "http://127.0.0.1:8001/login"
    data = {
        "username": username,
        "password": password
    }
    
    # Wait a bit for server to start
    time.sleep(2)
    
    try:
        with httpx.Client() as client:
            print(f"🔄 Đang thử đăng nhập với: {username} / {password}...")
            response = client.post(url, data=data, follow_redirects=False)
            
            if response.status_code == 303:
                print(f"✅ Đăng nhập THÀNH CÔNG! (Chuyển hướng đến {response.headers.get('location')})")
                print(f"🍪 Cookies: {response.cookies.get('user_id')}")
            else:
                print(f"❌ Đăng nhập THẤT BẠI! Status: {response.status_code}")
                print(f"Body: {response.text}")
                
    except Exception as e:
        print(f"❌ Lỗi khi kết nối server: {e}")

if __name__ == "__main__":
    test_login('tester', '12345678')
