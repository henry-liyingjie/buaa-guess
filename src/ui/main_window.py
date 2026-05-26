# src/ui/main_window.py
import os
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox, QProgressBar
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer

# 导入地图控件
from .map_controller import MapLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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
        self.hint_btn.setEnabled(False)
        
        self.next_btn = QPushButton("下一轮")
        self.next_btn.setFont(QFont("Microsoft YaHei", 11))
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #0056b3; }
            QPushButton:disabled { background-color: #6c757d; }
        """)
        self.next_btn.clicked.connect(self.next_round)
        self.next_btn.setEnabled(False)
        
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
        button_layout.addWidget(self.next_btn)
        button_layout.addWidget(self.end_btn)
        
        left_layout.addLayout(button_layout)
        left_layout.addStretch()
        
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
        self.start_btn.setEnabled(False)
        self.hint_btn.setEnabled(True)
        self.next_btn.setEnabled(True)
        self.end_btn.setEnabled(True)
        
        # 加载第一张实际图片
        self.load_actual_images_or_create_test()
        
        self.status_label.setText("游戏开始！请在地图上选择位置")
        self.location_label.setText("当前地点：天空之境")
        self.score_label.setText("得分: 0")
        self.progress_bar.setValue(1)
        
        print("🎮 游戏开始")
    
    def on_map_click(self, x: int, y: int):
        """地图点击事件"""
        if not self.start_btn.isEnabled():  # 游戏进行中
            self.coord_label.setText(f"坐标: ({x}, {y})")
            
            # 模拟猜测结果
            distance = ((x - 2500)**2 + (y - 1500)**2)**0.5
            score = max(0, 100 - int(distance / 10))
            
            result_text = f"""
            🎯 猜测结果：
            坐标: ({x}, {y})
            距离目标: {int(distance)} 像素
            本轮得分: {score}
            累计得分: {score}
            """
            
            self.status_label.setText(result_text)
            self.score_label.setText(f"得分: {score}")
            
            if distance < 200:
                self.status_label.setStyleSheet("""
                    QLabel {
                        padding: 10px;
                        background-color: #d4edda;
                        border: 2px solid #c3e6cb;
                        border-radius: 8px;
                        color: #155724;
                    }
                """)
            else:
                self.status_label.setStyleSheet("""
                    QLabel {
                        padding: 10px;
                        background-color: #f8d7da;
                        border: 2px solid #f5c6cb;
                        border-radius: 8px;
                        color: #721c24;
                    }
                """)
    
    def get_hint(self):
        """获取提示"""
        self.hint_label.setText("💡 提示：这是一个现代建筑，玻璃幕墙设计")
    
    def next_round(self):
        """下一轮"""
        current_value = self.progress_bar.value()
        if current_value < self.progress_bar.maximum():
            self.progress_bar.setValue(current_value + 1)
            self.location_label.setText(f"当前地点：末秋午后 (第{current_value + 1}轮)")
            self.hint_label.setText("提示：")
            self.status_label.setText("请在地图上选择位置")
            self.status_label.setStyleSheet("""
                QLabel {
                    padding: 10px;
                    background-color: #f8f9fa;
                    border: 2px solid #dee2e6;
                    border-radius: 8px;
                    color: #495057;
                }
            """)
    
    def end_game(self):
        """结束游戏"""
        final_score = 150  # 模拟分数
        result_text = f"""
        🎮 游戏结束！
        最终得分: {final_score}
        感谢游玩！
        """
        
        self.status_label.setText(result_text)
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #cce7ff;
                border: 2px solid #99ceff;
                border-radius: 8px;
                color: #004085;
            }
        """)
        
        self.start_btn.setEnabled(True)
        self.hint_btn.setEnabled(False)
        self.next_btn.setEnabled(False)
        self.end_btn.setEnabled(False)
    
    def show_error(self, title: str, message: str):
        """显示错误对话框"""
        QMessageBox.critical(self, title, message)

# 运行应用程序
if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())
