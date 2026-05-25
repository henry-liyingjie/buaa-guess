import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from src.core.game_engine import GameEngine

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.game = GameEngine()  # 初始化游戏引擎
        self.initUI()
        self.start_new_round()

    def initUI(self):
        self.setWindowTitle('北航图寻 - 原型')
        self.setGeometry(100, 100, 1000, 700)

        # 中央部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # 左侧：图片展示区
        self.image_label = QLabel()
        self.image_label.setFixedSize(600, 500)
        self.image_label.setStyleSheet("border: 2px solid black;")
        layout.addWidget(self.image_label)

        # 右侧：地图交互区（暂用标签代替）
        self.map_label = QLabel()
        self.map_label.setFixedSize(300, 500)
        self.map_label.setText("地图区域\n（点击功能待实现）")
        self.map_label.setStyleSheet("border: 2px solid blue;")
        layout.addWidget(self.map_label)

        # 底部：控制按钮
        btn_new_round = QPushButton('下一回合')
        btn_new_round.clicked.connect(self.start_new_round)
        layout.addWidget(btn_new_round)

    def start_new_round(self):
        image_path, location_name = self.game.start_new_round()
        print(f"新回合开始，正确地点是：{location_name}")
        print(f"图片路径（原始）: {image_path}")

        import os
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        absolute_image_path = os.path.join(project_root, image_path)

        print(f"绝对路径: {absolute_image_path}")
        print(f"文件存在: {os.path.exists(absolute_image_path)}")

        # 深度调试：检查QPixmap加载的每个环节
        pixmap = QPixmap(absolute_image_path)
        print(f"QPixmap是否为空: {pixmap.isNull()}")
        print(f"QPixmap尺寸: {pixmap.width()} x {pixmap.height()}")

        if not pixmap.isNull():
            # 检查QLabel的当前尺寸
            label_size = self.image_label.size()
            print(f"QLabel当前尺寸: {label_size.width()} x {label_size.height()}")

            # 进行缩放
            scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            print(f"缩放后尺寸: {scaled_pixmap.width()} x {scaled_pixmap.height()}")

            # 设置到QLabel
            self.image_label.setPixmap(scaled_pixmap)
            print("✅ 图片已设置到QLabel")

            # 强制重绘
            self.image_label.repaint()
            print("✅ 已强制重绘")
        else:
            self.image_label.setText("图片加载失败")
            print("❌ QPixmap加载失败")

        print("--- 回合初始化完成 ---")
