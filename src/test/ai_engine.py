from src.main.ai.ai_engine import ALEngine

def test_ai_system():
    print("🧪 Bắt đầu kiểm thử hệ thống AI...")
    engine = ALEngine()
    
    # 1. Kiểm tra huấn luyện
    success = engine.train_all()
    if success:
        print("✅ Huấn luyện thành công.")
        
        # 2. Kiểm tra dự đoán
        # Giả lập: Điểm 9, 9, Học 20h, Xem video 100%
        result = engine.predict_all(9.0, 9.0, 20.0, 1.0)
        print(f"📊 Kết quả dự đoán mẫu: {result}")
        
        if result['group'] == "Giỏi" and result['is_passed'] == "Đạt":
            print("✨ AI hoạt động chính xác cho sinh viên giỏi.")
    else:
        print("❌ Huấn luyện thất bại. Hãy kiểm tra dữ liệu đầu vào.")

if __name__ == "__main__":
    test_ai_system()
