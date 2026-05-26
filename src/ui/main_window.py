# src/ui/main_window.py
import os
import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

# 导入MapLabel
from src.ui.map_controller import MapLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle('北航图寻')
        self.setGeometry(100, 100, 1400, 800)  # 增大窗口

        # 中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局：左右分栏，设置比例
        layout = QHBoxLayout(central_widget)
        layout.setSpacing(20)  # 设置间距

        # ============ 左侧：游戏控制区 ============
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)

        # 标题
        title_label = QLabel("北航图寻")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #003366;")
        left_layout.addWidget(title_label)

        # 图片显示区域 - 增大尺寸
        self.image_label = QLabel()
        self.image_label.setMinimumSize(500, 375)  # 增大：500×375 (4:3比例)
        self.image_label.setMaximumSize(600, 450)  # 最大：600×450
        self.image_label.setStyleSheet("""
            QLabel {
                border: 3px solid #ff6b6b;
                background-color: white;
                qproperty-alignment: AlignCenter;
            }
        """)

        # 加载地点图片
        self.load_location_image("main_building", 1)

        left_layout.addWidget(self.image_label)

        # 图片说明
        self.image_desc = QLabel("当前目标地点")
        self.image_desc.setStyleSheet("font-size: 14px; color: #666;")
        left_layout.addWidget(self.image_desc)

        # 信息显示区域
        self.info_label = QLabel("等待游戏开始...")
        self.info_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                padding: 10px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
            }
        """)
        self.info_label.setMinimumHeight(100)
        left_layout.addWidget(self.info_label)

        # 游戏控制按钮
        button_layout = QHBoxLayout()

        start_button = QPushButton("开始游戏")
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)

        test_button = QPushButton("测试图片")
        test_button.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
            }
        """)
        test_button.clicked.connect(self.test_image_load)

        reset_button = QPushButton("重置视图")
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
            }
        """)
        reset_button.clicked.connect(lambda: self.map_label.reset_view())

        button_layout.addWidget(start_button)
        button_layout.addWidget(test_button)
        button_layout.addWidget(reset_button)

        left_layout.addLayout(button_layout)

        # 得分显示
        self.score_label = QLabel("得分: 0")
        self.score_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #dc3545;")
        left_layout.addWidget(self.score_label)

        left_layout.addStretch()

        # ============ 右侧：地图交互区 ============
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # 地图标题
        map_title = QLabel("北航校园地图")
        map_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #003366;")
        right_layout.addWidget(map_title)

        # 地图控件 - 增大但保持比例
        self.map_label = MapLabel()
        self.map_label.setMinimumSize(700, 525)  # 700×525 (与左侧保持比例)

        # 加载地图
        map_path = "data/map.png"
        if os.path.exists(map_path):
            if not self.map_label.load_map(map_path):
                print("地图加载失败")
        else:
            print(f"地图文件不存在: {map_path}")
            self.map_label.setText(f"地图文件不存在\n{map_path}")

        # 地图使用说明
        map_instructions = QLabel("使用说明：\n• 鼠标滚轮缩放\n• 左键拖拽移动\n• 右键点击选择位置")
        map_instructions.setStyleSheet("color: #666; font-size: 14px;")
    
        right_layout.addWidget(self.map_label)
        right_layout.addWidget(map_instructions)
        right_layout.addStretch()

        # ============ 设置布局比例 ============
        # 左侧:右侧 ≈ 5:7 (更平衡的比例)
        layout.addWidget(left_panel, stretch=5)   # 左侧占5份
        layout.addWidget(right_panel, stretch=7)  # 右侧占7份

        # 连接信号
        self.map_label.mapClicked.connect(self.on_map_click)

        print("✅ 界面初始化完成（优化布局）")

        
    def load_location_image(self, location_name, image_index=0):
        """加载指定地点的图片"""
        print(f"\n=== 加载地点图片: {location_name}_{image_index} ===")
        
        # 构建图片路径
        image_filename = f"{location_name}_{image_index}.jpg"
        image_path = os.path.join("data", "images", image_filename)
        
        # 如果指定文件不存在，尝试通用名称
        if not os.path.exists(image_path):
            image_path = "data/images/1.jpg"
        
        print(f"尝试加载: {image_path}")
        print(f"文件存在: {os.path.exists(image_path)}")
        
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # 缩放图片以适应标签
                scaled_pixmap = pixmap.scaled(
                    self.image_label.size(), 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                self.image_label.setAlignment(Qt.AlignCenter)
                print(f"✅ 图片加载成功: {image_path}")
                print(f"图片尺寸: {pixmap.size()} -> {scaled_pixmap.size()}")
                return True
            else:
                print("❌ QPixmap加载失败，图片可能损坏")
        else:
            print("❌ 文件不存在")
            
        # 加载失败时使用测试图片
        self.create_test_image()
        return False
        
    def create_test_image(self):
        """创建临时测试图片"""
        from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont
        
        print("⚠️ 使用生成的测试图片")
        
        # 创建400x300的图片
        pixmap = QPixmap(400, 300)
        pixmap.fill(QColor(240, 248, 255))  # 浅蓝色背景
        
        painter = QPainter(pixmap)
        
        # 画边框
        painter.setPen(QColor(255, 0, 0))  # 红色边框
        painter.drawRect(0, 0, 399, 299)
        
        # 写文字
        painter.setFont(QFont("Arial", 16, QFont.Bold))
        painter.setPen(QColor(25, 25, 112))  # 深蓝色文字
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "北航图寻\n地点图片\n400×300")
        
        # 画一个简单的建筑图标
        painter.setBrush(QColor(139, 0, 0))  # 深红色
        painter.drawRect(150, 100, 100, 80)  # 建筑主体
        painter.drawPolygon([(150, 100), (200, 50), (250, 100)])  # 屋顶
        
        painter.end()
        
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)
        
    def test_image_load(self):
        """测试图片加载功能"""
        print("\n=== 测试图片加载 ===")
        
        # 检查当前pixmap状态
        if self.image_label.pixmap():
            print(f"当前图片尺寸: {self.image_label.pixmap().size()}")
        else:
            print("当前没有图片")
            
        # 重新加载图片
        self.load_location_image("test", 0)
        
    def on_guess(self):
        """处理猜测按钮点击"""
        print("猜测按钮被点击")
        
    def on_map_click(self, x: int, y: int):
        """处理地图点击事件"""
        print(f"接收到地图坐标: x={x}, y={y}")
        self.info_label.setText(f"已选择坐标: ({x}, {y})")
        
    def showEvent(self, event):
        """窗口显示事件"""
        super().showEvent(event)
        
        # 窗口显示后检查图片状态
        print("\n=== 窗口显示状态检查 ===")
        print(f"图片标签尺寸: {self.image_label.size()}")
        print(f"图片标签是否可见: {self.image_label.isVisible()}")
        
        if self.image_label.pixmap():
            print(f"图片尺寸: {self.image_label.pixmap().size()}")
        else:
            print("警告: 图片标签没有pixmap")
