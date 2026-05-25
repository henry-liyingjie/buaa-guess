"""
test_engine.py
对 core/game_engine.py 中的 GameEngine 类进行单元测试。
"""
import sys
import os
import unittest
import pandas as pd

# 将项目根目录添加到 Python 路径，以便导入 src 下的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.game_engine import GameEngine


class TestGameEngine(unittest.TestCase):
    """测试 GameEngine 类的测试用例集合"""

    # 准备一个用于测试的小型CSV数据
    TEST_CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'locations_test.csv')
    
    @classmethod
    def setUpClass(cls):
        """在所有测试开始前执行一次。创建一个测试用的CSV文件。"""
        test_data = [
            {"id": 1, "name": "测试点A", "description": "描述A", "x": 100, "y": 100, "image_path": "images/a1.jpg"},
            {"id": 2, "name": "测试点B", "description": "描述B", "x": 200, "y": 200, "image_path": "images/b1.jpg"},
            {"id": 3, "name": "测试点C", "description": "描述C", "x": 300, "y": 300, "image_path": "images/c1.jpg"},
        ]
        df = pd.DataFrame(test_data)
        # 确保目录存在
        os.makedirs(os.path.dirname(cls.TEST_CSV_PATH), exist_ok=True)
        df.to_csv(cls.TEST_CSV_PATH, index=False)

    @classmethod
    def tearDownClass(cls):
        """在所有测试结束后执行一次。删除测试用的CSV文件。"""
        if os.path.exists(cls.TEST_CSV_PATH):
            os.remove(cls.TEST_CSV_PATH)

    def setUp(self):
        """在每个测试方法开始前执行。初始化一个新的GameEngine实例。"""
        # 使用我们创建的测试数据文件
        self.engine = GameEngine(self.TEST_CSV_PATH)

    def tearDown(self):
        """在每个测试方法结束后执行。清理资源（这里暂无）。"""
        pass

    # --- 测试1：初始化与数据加载 ---
    def test_initialization_loads_data(self):
        """测试引擎初始化后是否正确加载了CSV数据"""
        # 断言：加载的数据行数应为3
        self.assertEqual(len(self.engine.locations_df), 3)
        # 断言：列名应包含预期的字段
        expected_columns = {'id', 'name', 'description', 'x', 'y', 'image_path'}
        self.assertTrue(expected_columns.issubset(set(self.engine.locations_df.columns)))

    # --- 测试2：新回合逻辑 ---
    def test_start_new_round_selects_location_and_image(self):
        """测试 start_new_round 方法是否返回图片路径和地点名，且内容来自数据"""
        image_path, location_name = self.engine.start_new_round()
        
        # 断言：返回的图片路径应该在数据集中
        all_image_paths = self.engine.locations_df['image_path'].tolist()
        self.assertIn(image_path, all_image_paths)
        
        # 断言：返回的地点名应该在数据集中
        all_location_names = self.engine.locations_df['name'].tolist()
        self.assertIn(location_name, all_location_names)
        
        # 断言：返回的图片路径和地点名应来自同一行数据（一致性）
        # 根据返回的地点名，在数据集中找到对应的行
        selected_row = self.engine.locations_df[self.engine.locations_df['name'] == location_name]
        # 该行的图片路径应与返回的图片路径一致
        self.assertEqual(selected_row['image_path'].iloc[0], image_path)

    def test_start_new_round_sets_current_location(self):
        """测试 start_new_round 方法是否正确设置了内部状态（current_location）"""
        # 初始时 current_location 应为 None
        self.assertIsNone(self.engine.current_location)
        
        self.engine.start_new_round()
        # 调用后，current_location 应该被设置为一个pandas Series（一行数据）
        self.assertIsNotNone(self.engine.current_location)
        self.assertTrue(hasattr(self.engine.current_location, 'name'))  # 检查是否为Series

    # --- 测试3：提交猜测逻辑 ---
    def test_submit_guess_correct_within_threshold(self):
        """测试当猜测点非常接近真实点时，应判定为正确，并得到满分"""
        # 启动一个新回合，获取一个真实地点
        self.engine.start_new_round()
        actual_x = self.engine.current_location['x']
        actual_y = self.engine.current_location['y']
        
        # 猜测点与真实点完全相同（距离为0）
        result = self.engine.submit_guess(actual_x, actual_y)
        
        # 断言：应判定为正确，距离为0，得分为100（根据你的算法）
        self.assertTrue(result['is_correct'])
        self.assertEqual(result['distance'], 0)
        self.assertEqual(result['score'], 100)  # 100 - 0 = 100

    def test_submit_guess_incorrect_beyond_threshold(self):
        """测试当猜测点距离真实点很远（超过阈值）时，应判定为错误，得分为0"""
        self.engine.start_new_round()
        actual_x = self.engine.current_location['x']
        actual_y = self.engine.current_location['y']
        
        # 猜测一个非常远的点（例如距离1000像素，远大于阈值50）
        guess_x = actual_x + 1000
        guess_y = actual_y + 1000
        
        result = self.engine.submit_guess(guess_x, guess_y)
        
        # 断言：应判定为错误，距离应大于50，得分为0
        self.assertFalse(result['is_correct'])
        self.assertGreater(result['distance'], 50)  # 距离应大于阈值
        self.assertEqual(result['score'], 0)

    def test_submit_guess_calculation_and_edge_case(self):
        """测试边缘情况：猜测点恰好落在阈值边界上（距离=50）"""
        self.engine.start_new_round()
        actual_x = self.engine.current_location['x']
        actual_y = self.engine.current_location['y']
        
        # 猜一个点，使其与真实点的距离恰好为50（例如，水平距离50，垂直距离0）
        guess_x = actual_x + 50  # 水平移动50像素
        guess_y = actual_y       # 垂直不变
        
        result = self.engine.submit_guess(guess_x, guess_y)
        
        # 断言：根据你的算法，距离为50正好是“小于阈值”的判断吗？
        # 注意：你的算法是 `distance < threshold`，所以距离=50应判为错误。
        self.assertEqual(result['distance'], 50)
        self.assertFalse(result['is_correct'])  # 因为 50 < 50 为假
        self.assertEqual(result['score'], 0)    # 错误时得分为0

    def test_submit_guess_before_starting_round(self):
        """测试如果在未开始回合时提交猜测，应优雅地处理错误"""
        # 确保未调用 start_new_round
        self.engine.current_location = None
        
        # 断言：应抛出异常或返回特定错误。这里我们期望它会引发一个错误。
        # 根据你的实际实现，这里可能需要调整。
        with self.assertRaises(Exception):  # 更精确地，可以使用 AttributeError 或自定义异常
            self.engine.submit_guess(100, 100)

if __name__ == '__main__':
    # 运行所有测试
    unittest.main()
