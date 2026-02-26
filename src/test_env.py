try:
    import sklearn
    import pandas
    import flask
    print("✅ Chúc mừng! Môi trường học tập AI của bạn đã sẵn sàng.")
except ImportError as e:
    print(f"❌ Vẫn thiếu thư viện: {e}")