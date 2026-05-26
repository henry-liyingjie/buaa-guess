# src/ui/main_window.py
import os
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox, QProgressBar
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QPainter  # 确保有这个导入

# 导入地图控件
from .map_controller import MapLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 图片轮换相关状态变量
        self.game_started = False
        self.current_round = 0
        self.total_rounds = 3
        self.correct_positions = {
            "天空之境.jpg": (2800, 1600),
            "末秋午后.jpg": (2200, 1200), 
            "湖上旅者.jpg": (1900, 1800)
        }
        self.game_images = ["天空之境.jpg", "末秋午后.jpg", "湖上旅者.jpg"]
        self.current_image_index = 0
        
        self.initUI()        
    def initUI(self):
        """初始化界面"""
        self.setWindowTitle('航寻 v1.0')
        self.setGeometry(100, 100, 1400, 800)
        
        # 中央部件
        central = QWidget()
        self.setCentralWidget(central)
        
        # 主布局
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # ============ 左侧：游戏区 ============
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)
        
        # 1. 标题
        title = QLabel("航寻")
        title.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        title.setStyleSheet("color: #003366; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title)
        
        # 2. 游戏状态
        self.status_label = QLabel("点击'开始游戏'开始")
        self.status_label.setFont(QFont("Microsoft YaHei", 14))
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                color: #495057;
            }
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setMinimumHeight(60)
        left_layout.addWidget(self.status_label)
        
        # 3. 地点图片
        self.image_label = QLabel()
        self.image_label.setMinimumSize(500, 375)
        self.image_label.setMaximumSize(600, 450)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 3px solid #ff6b6b;
                border-radius: 8px;
                background-color: white;
                qproperty-alignment: AlignCenter;
            }
        """)
        left_layout.addWidget(self.image_label)
        
        # 4. 地点信息
        self.location_label = QLabel("等待游戏开始...")
        self.location_label.setFont(QFont("Microsoft YaHei", 12))
        self.location_label.setStyleSheet("color: #6c757d;")
        self.location_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.location_label)
        
        # 5. 提示
        self.hint_label = QLabel("提示：")
        self.hint_label.setFont(QFont("Microsoft YaHei", 11))
        self.hint_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 5px;
                color: #856404;
            }
        """)
        self.hint_label.setWordWrap(True)
        left_layout.addWidget(self.hint_label)
        
        # 6. 游戏进度
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 10)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("第 %v/%m 轮")
        left_layout.addWidget(self.progress_bar)
        
        # 7. 得分
        self.score_label = QLabel("得分: 0")
        self.score_label.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        self.score_label.setStyleSheet("color: #dc3545;")
        self.score_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.score_label)
        
        # 8. 控制按钮
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("开始游戏")
        self.start_btn.setFont(QFont("Microsoft YaHei", 12))
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #218838; }
        """)
        self.start_btn.clicked.connect(self.start_game)
        
        self.hint_btn = QPushButton("获取提示")
        self.hint_btn.setFont(QFont("Microsoft YaHei", 11))
        self.hint_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #138496; }
            QPushButton:disabled { background-color: #6c757d; }
        """)
        self.hint_btn.clicked.connect(self.get_hint)
        self.hint_btn.setEnabled(True)
        
        self.confirm_btn = QPushButton("确认位置")  # 原来是 self.next_btn = QPushButton("下一轮")
        self.confirm_btn.setFont(QFont("Microsoft YaHei", 11))
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #0056b3; }
            QPushButton:disabled { background-color: #6c757d; }
        """)
        self.confirm_btn.clicked.connect(self.confirm_selection)  # 原来是 .clicked.connect(self.next_round)
        self.confirm_btn.setEnabled(False)
        
        self.end_btn = QPushButton("结束游戏")
        self.end_btn.setFont(QFont("Microsoft YaHei", 11))
        self.end_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #c82333; }
            QPushButton:disabled { background-color: #6c757d; }
        """)
        self.end_btn.clicked.connect(self.end_game)
        self.end_btn.setEnabled(False)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.hint_btn)
        button_layout.addWidget(self.confirm_btn)
        button_layout.addWidget(self.end_btn)
        
        left_layout.addLayout(button_layout)
        left_layout.addStretch()
        # 总分显示 - 添加这个关键元素
        self.total_score_label = QLabel("总分: 0")
        self.total_score_label.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        self.total_score_label.setAlignment(Qt.AlignCenter)
        self.total_score_label.setStyleSheet("color: #ff6b35; padding: 10px;")
        left_layout.addWidget(self.total_score_label)
        
    


        
        # ============ 右侧：地图区 ============
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)
        
        # 地图标题
        map_title = QLabel("北航校园地图")
        map_title.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        map_title.setStyleSheet("color: #003366;")
        map_title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(map_title)
        
        # 地图控件
        self.map_label = MapLabel()
        self.map_label.setMinimumSize(700, 525)
        self.map_label.setStyleSheet("""
            QLabel {
                border: 3px solid #17a2b8;
                border-radius: 8px;
                background-color: white;
            }
        """)
        
        # 加载地图
        map_path = "data/map.png"
        if os.path.exists(map_path):
            if not self.map_label.load_map(map_path):
                self.show_error("地图加载失败", "无法加载地图文件")
        else:
            print(f"地图文件不存在: {map_path}")
            # 创建测试地图
            self.map_label.create_test_map()
        
        # 连接地图点击信号
        self.map_label.mapClicked.connect(self.on_map_click)
        
        right_layout.addWidget(self.map_label)
        
        # 操作说明
        instructions = QLabel("""
        🎮 操作说明：
        • 鼠标滚轮：缩放地图
        • 左键拖拽：移动地图
        • 右键点击：选择位置进行猜测
        • 开始游戏后，根据左侧图片在地图上找到对应位置
        """)
        instructions.setFont(QFont("Microsoft YaHei", 11))
        instructions.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #e7f5ff;
                border: 1px solid #a5d8ff;
                border-radius: 8px;
                color: #1864ab;
            }
        """)
        instructions.setWordWrap(True)
        right_layout.addWidget(instructions)
        
        # 坐标显示
        self.coord_label = QLabel("坐标: (0, 0)")
        self.coord_label.setFont(QFont("Microsoft YaHei", 10))
        self.coord_label.setStyleSheet("color: #495057;")
        self.coord_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.coord_label)
        
        right_layout.addStretch()
        
        # ============ 设置布局比例 ============
        main_layout.addWidget(left_panel, stretch=5)
        main_layout.addWidget(right_panel, stretch=7)
        
        # 初始化显示测试图片
        self.load_actual_images_or_create_test()
        
        print("✅ 界面初始化完成")
    def load_current_game_image(self):
        """加载当前图片"""
        if not hasattr(self, 'game_images') or not self.game_images:
            return

        image_name = self.game_images[self.current_image_index]
        image_path = f"data/images/{image_name}"

        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.image_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                print(f"✅ 加载图片: {image_name}")
        else:
            # 创建占位图
            self.create_placeholder_image(image_name)

    def create_placeholder_image(self, image_name):
        """创建占位图片"""
        pixmap = QPixmap(400, 300)
        pixmap.fill(Qt.lightGray)

        from PyQt5.QtGui import QPainter
        painter = QPainter(pixmap)
        painter.setFont(QFont("Microsoft YaHei", 14))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, f"{image_name}\n(图片加载中)")
        painter.end()

        self.image_label.setPixmap(pixmap)
    def load_actual_images_or_create_test(self):
        """尝试加载实际图片，否则创建测试图片"""
        actual_images = [
            "data/images/天空之境.jpg",
            "data/images/末秋午后.jpg", 
            "data/images/湖上行者.jpg"
        ]
        
        for image_path in actual_images:
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        self.image_label.size(), 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                    print(f"✅ 成功加载: {image_path}")
                    return
        
        # 如果所有图片都不存在，创建简单测试图片
        print("❌ 未找到任何实际图片，使用测试图片")
        self.create_simple_test_image()
    
    def create_simple_test_image(self):
        """创建简单的测试图片"""
        from PyQt5.QtGui import QPixmap, QPainter, QColor
        
        pixmap = QPixmap(500, 375)
        pixmap.fill(QColor(240, 248, 255))
        
        painter = QPainter(pixmap)
        painter.setPen(QColor(255, 0, 0))
        painter.drawRect(0, 0, 499, 374)
        
        painter.setFont(QFont("Arial", 16, QFont.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "北航图寻\n测试图片\n500×375")
        
        painter.end()
        self.image_label.setPixmap(pixmap)
    
    # ============ 游戏逻辑方法 ============
    
    def start_game(self):
        """开始游戏"""
        # 清除结算区域，恢复提示
        self.hint_label.setText("提示：仔细观察图片特征，在地图上找到对应位置")

        self.game_started = True
        self.current_round = 0
        self.total_score = 0
        self.round_scores = []
        self.current_selection = None

        # 更新界面
        self.total_score_label.setText("总分: 0")
        self.status_label.setText("游戏开始！请在地图上选择位置")

        # 开始第一轮
        self.next_round()


    def on_map_click(self, x, y):
        """地图点击事件 - 支持多次点击调整"""
        if not self.game_started:
            return
    
        print(f"📍 选择位置: ({x}, {y})")
        self.current_selection = (x, y)
    
        # 启用确认按钮
        self.confirm_btn.setEnabled(True)
    
     # 更新状态提示
        self.status_label.setText(f"已选择位置 ({x}, {y})，点击'确认位置'提交")

        # 在地图上显示标记
        if hasattr(self.map_label, 'last_marker_pos'):
            self.map_label.last_marker_pos = (x, y)
            self.map_label.update_display()
    def get_hint(self):
        """获取提示"""
        if not self.game_started:
            return

        image_name = self.game_images[self.current_image_index]
        hint_map = {
            "天空之境.jpg": "💡 这是一个现代建筑，玻璃幕墙设计",
            "末秋午后.jpg": "💡 秋季景观，落叶满地，阳光温暖", 
            "湖上旅者.jpg": "💡 湖边景观，有步行道，水面平静"
        }

        hint = hint_map.get(image_name, "💡 仔细观察图片特征")

        # 在提示区域显示提示
        self.hint_label.setText(hint)

    def submit_round(self):
        """提交本轮选择并在原页面显示结算"""
        if not self.current_selection:
            return

        # 计算得分（基于距离的简单算法）
        current_image = self.game_images[self.current_image_index]
        target_pos = self.correct_positions.get(current_image, (2500, 1500))
        user_pos = self.current_selection

        # 计算欧几里得距离
        distance = ((user_pos[0] - target_pos[0])**2 + (user_pos[1] - target_pos[1])**2)**0.5

        # 距离越近得分越高（最大100分）
        round_score = max(0, 100 - int(distance / 10))

        # 更新总分
        self.total_score += round_score
        self.round_scores.append(round_score)

        # 在原页面显示结算信息
        self.show_inline_result(round_score, target_pos, distance)

        # 更新界面显示
        self.update_after_round()

    def show_inline_result(self, round_score, target_pos, distance):
        """在原页面显示结算信息"""
        result_text = f"""
        🎯 第 {self.current_round} 轮结果

        您的选择: ({self.current_selection[0]}, {self.current_selection[1]})
        正确位置: ({target_pos[0]}, {target_pos[1]})
        距离偏差: {int(distance)} 像素
    
        本轮得分: {round_score} 分
        累计总分: {self.total_score} 分
        """
    
        # 使用现有的提示区域显示结算信息
        self.hint_label.setText(result_text)

        # 更新总分显示
        self.total_score_label.setText(f"总分: {self.total_score}")

        # 更新状态栏
        self.status_label.setText(f"第 {self.current_round} 轮结算完成")


    def update_after_round(self):
        """回合结束后的界面更新"""
        # 更新总分显示
        self.total_score_label.setText(f"总分: {self.total_score}")

        # 清除当前选择
        self.current_selection = None

        # 如果是最后一轮，显示游戏结束
        if self.current_round >= self.total_rounds:
            self.show_inline_game_summary()
        else:
            # 准备下一轮
            self.prepare_next_round()

    def show_inline_game_summary(self):
        """在原页面显示游戏总结"""
        summary = f"""
        🎮 游戏结束！

        最终得分: {self.total_score} 分

        各轮得分:
        """

        for i, score in enumerate(self.round_scores, 1):
            summary += f"\n第 {i} 轮: {score} 分"

        # 使用提示区域显示游戏总结
        self.hint_label.setText(summary)

        # 重置游戏状态
        self.game_started = False
        self.status_label.setText("游戏已结束，点击'开始游戏'重新开始")
    def confirm_selection(self):
        """确认当前选择并结算本轮"""
        if not self.current_selection:
            return
    
        print(f"✅ 确认提交: {self.current_selection}")
    
        # 禁用确认按钮，防止重复提交
        self.confirm_btn.setEnabled(False)

        # 调用原有的结算逻辑
        self.submit_round()
    def prepare_next_action(self):
        """准备下一步动作"""
        # 如果是最后一轮，显示游戏结束
        if self.current_round >= self.total_rounds:
            self.show_inline_game_summary()
            # 重置游戏状态
            self.game_started = False
        else:
            # 不自动进入下一轮，等待用户操作
            # 可以在这里添加一个"下一轮"按钮或者保持当前状态
            self.status_label.setText("本轮结算完成")
    def prepare_next_round(self):
        """准备下一轮"""
        # 清除地图标记
        if hasattr(self.map_label, 'clear_markers'):
            self.map_label.clear_markers()

        # 延迟2秒后进入下一轮
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(2000, self.next_round_with_clear)

    def next_round_with_clear(self):
        """清除结算信息并进入下一轮"""
        # 清除结算信息，恢复提示区域
        self.hint_label.setText("提示：仔细观察图片特征，在地图上找到对应位置")

        # 进入下一轮
        self.next_round()


    def show_game_summary(self):
        """显示游戏总结（简单版本）"""
        from PyQt5.QtWidgets import QMessageBox

        summary = f"""
        🎮 游戏结束！

        最终得分: {self.total_score} 分

        各轮得分:
        """

        for i, score in enumerate(self.round_scores, 1):
            summary += f"\n第 {i} 轮: {score} 分"

        QMessageBox.information(self, "游戏结束", summary)

        # 重置游戏状态
        self.game_started = False
    def next_round(self):
        """进入下一轮"""
        if not self.game_started or self.current_round >= self.total_rounds:
            return

        self.current_round += 1
        self.current_image_index = (self.current_image_index + 1) % len(self.game_images)

        # 修复这里：使用正确的方法名
        self.load_current_game_image()  # 原来是 self.load_current_image()

        # 清除地图标记
        if hasattr(self.map_label, 'clear_markers'):
            self.map_label.clear_markers()

        # 更新状态
        self.status_label.setText(f"第 {self.current_round} 轮: 请在地图上选择位置")

        print(f"🔄 第 {self.current_round}/{self.total_rounds} 轮")

    
    
    
    def end_game(self):
        """结束游戏"""
        self.game_started = False

        result_text = f"""
        🎮 游戏结束！
        • 完成轮数: {self.current_round + 1}/{self.total_rounds}
        • 感谢游玩！点击'开始游戏'重新开始
        """

        self.status_label.setText(result_text)

        # 重置按钮状态
        self.start_btn.setEnabled(True)
        self.hint_btn.setEnabled(False)
        self.next_btn.setEnabled(False)
        self.end_btn.setEnabled(False)

        print("🎮 游戏结束")

    
    def show_error(self, title: str, message: str):
        """显示错误对话框"""
        QMessageBox.critical(self, title, message)
    
    def create_placeholder_image(self, image_name):
        """创建占位图片"""
        pixmap = QPixmap(500, 375)
        pixmap.fill(QColor(240, 248, 255))

        painter = QPainter(pixmap)
        painter.setPen(QColor(100, 100, 100))
        painter.drawRect(0, 0, 499, 374)

        painter.setFont(QFont("Microsoft YaHei", 16))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, f"{image_name}\n\n图片加载中...")
        painter.end()

        self.image_label.setPixmap(pixmap)
# 运行应用程序
if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())
