import pandas as pd
import math

class GameEngine:
    def __init__(self, data_path='data/locations.csv'):
        self.locations_df = pd.read_csv(data_path)
        self.current_location = None
        self.current_image = None

    def start_new_round(self):
        """随机选择一个地点和一张图片，开始新回合"""
        # 1. 从locations_df中随机选择一行
        self.current_location = self.locations_df.sample(n=1).iloc[0]
        # 2. 根据image_path加载图片（这里先返回路径，UI层加载）
        self.current_image = self.current_location['image_path']
        return self.current_image, self.current_location['name']  # 返回图片路径和地点名（用于调试）

    def submit_guess(self, guess_x, guess_y):
        """提交玩家猜测的坐标，返回结果"""
        actual_x = self.current_location['x']
        actual_y = self.current_location['y']

        # 计算直线距离（像素距离）
        distance = math.sqrt((guess_x - actual_x)**2 + (guess_y - actual_y)**2)

        # 判断是否猜中（例如，距离小于50像素算正确）
        threshold = 50
        is_correct = distance < threshold

        # 计算积分（例如，距离越近分越高）
        score = max(0, 100 - int(distance))

        return {
            'is_correct': is_correct,
            'distance': distance,
            'score': score if is_correct else 0,
            'actual_name': self.current_location['name']
        }
