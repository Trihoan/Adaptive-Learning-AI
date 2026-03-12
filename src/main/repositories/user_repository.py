import pandas as pd 
import os 

class UserRepository: 
    def __init__(self, file_path):
        self.file_path = file_path
    def find_by_username(self , username):
        if not os.path.exists(self.file_path):
            return None
        df = pd.read_csv(self.file_path)
        user_row = df[df['username'] == username]
        return user_row.to_dict('records')[0] if not user_row.empty else None

    def save_user(self, user_dict):
        # Lưu người dùng mới vào CSV
        df = pd.DataFrame([user_dict])
        df.to_csv(self.file_path, mode='a', header=not os.path.exists(self.file_path), index=False)