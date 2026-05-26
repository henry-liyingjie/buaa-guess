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
        self.setGeometry(100, 100, 1200, 700)
        
        # 中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局：左右分栏
        layout = QHBoxLayout(central_widget)
        
        # ============ 左侧：游戏控制区 ============
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 图片显示区域 - 只定义一次！
        self.image_label = QLabel()
        self.image_label.setFixedSize(400, 300)
        self.image_label.setStyleSheet("border: 3px solid red; background-color: white;")
        
        # 加载地点图片
        self.load_location_image("main_building", 1)
        
        left_layout.addWidget(self.image_label)
        
        # 信息显示
        self.info_label = QLabel("等待游戏开始...")
        left_layout.addWidget(self.info_label)
        
        # 测试按钮
        test_button = QPushButton("测试图片加载")
        test_button.clicked.connect(self.test_image_load)
        left_layout.addWidget(test_button)
        
        # 猜测按钮
        self.guess_button = QPushButton("确认猜测")
        self.guess_button.clicked.connect(self.on_guess)
        left_layout.addWidget(self.guess_button)
        
        left_layout.addStretch()
        
        # ============ 右侧：地图交互区 ============
        # 使用MapLabel（支持缩放）
        self.map_label = MapLabel()
        self.map_label.setFixedSize(600, 500)
        
        # 加载地图
        map_path = "data/map.png"
        if os.path.exists(map_path):
            if not self.map_label.load_map(map_path):
                print("地图加载失败")
        else:
            print(f"地图文件不存在: {map_path}")
            self.map_label.setText(f"地图文件不存在\n{map_path}")
        
        # ============ 添加到主布局 ============
        layout.addWidget(left_panel)
        layout.addWidget(self.map_label)
        
        print("✅ 界面初始化完成")
        
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
