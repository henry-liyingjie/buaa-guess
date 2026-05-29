# src/game_logic.py
import json
import os

class GameLogic:
    def __init__(self):
        self.load_locations()
    
    def load_locations(self):
        """读取 locations.json"""
        try:
            with open('data/locations.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.locations = data['locations']
                print(f"加载了 {len(self.locations)} 个地点")
        except Exception as e:
            print(f"读取地点数据失败: {e}")
            self.locations = []
