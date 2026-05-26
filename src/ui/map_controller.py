#src/ui/map_controller.py
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap, QWheelEvent, QMouseEvent, QPainter
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
import os

class MapLabel(QLabel):
    """修正版：精确的以光标为中心的缩放地图控件"""
    
    mapClicked = pyqtSignal(int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.original_pixmap = None
        self.scale_factor = 1.0
        self.min_scale = 0.1
        self.max_scale = 5.0
        self.offset = QPoint(0, 0)
        self.mouse_press_pos = QPoint()
        self.is_dragging = False
        
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 2px solid blue; background-color: #f0f0f0;")
        self.setMouseTracking(True)
        self.marker_icon = None
        self.load_marker_icon()  # 新增：加载图标
    def load_marker_icon(self):
        """加载并调整图标大小"""
        icon_path = "data/images/marker_icon.png"
        if os.path.exists(icon_path):
            original_icon = QPixmap(icon_path)
            if not original_icon.isNull():
                # 调整图标大小为合适尺寸（例如 32x32 像素）
                target_size = 32
                self.marker_icon = original_icon.scaled(
                    target_size, target_size, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                print(f"✅ 图标加载成功，调整为 {target_size}x{target_size} 像素")
            else:
                self.marker_icon = None
        else:
            print(f"❌ 图标文件不存在: {icon_path}")
            self.marker_icon = None
    def load_map(self, map_path):
        """加载地图图片"""
        pixmap = QPixmap(map_path)
        if pixmap.isNull():
            return False
            
        self.original_pixmap = pixmap
        self.scale_factor = 1.0
        self.offset = QPoint(0, 0)
        self.update_display()
        return True
    
    def wheelEvent(self, event: QWheelEvent):
        """修正版：精确的以光标为中心的缩放"""
        if not self.original_pixmap:
            return
            
        # 获取鼠标在控件内的位置
        mouse_pos = event.pos()
        
        # 计算缩放前的鼠标在原始图片中的位置
        original_mouse_pos = self.screen_to_original(mouse_pos)
        if original_mouse_pos is None:
            return
            
        # 计算缩放因子
        zoom_delta = event.angleDelta().y()
        zoom_in = zoom_delta > 0
        zoom_factor = 1.2 if zoom_in else 0.8
        
        # 计算新缩放比例
        new_scale = self.scale_factor * zoom_factor
        new_scale = max(self.min_scale, min(self.max_scale, new_scale))
        
        if new_scale != self.scale_factor:
            # 保存旧缩放比例
            old_scale = self.scale_factor
            
            # 更新缩放比例
            self.scale_factor = new_scale
            
            # 关键修正：重新计算偏移量，保持鼠标指向的原始位置不变
            # 计算缩放后该原始位置应该对应的屏幕位置
            target_screen_pos = self.original_to_screen(original_mouse_pos)
            if target_screen_pos:
                # 计算需要调整的偏移量
                delta_x = mouse_pos.x() - target_screen_pos.x()
                delta_y = mouse_pos.y() - target_screen_pos.y()
                
                self.offset += QPoint(int(delta_x), int(delta_y))
            
            self.update_display()
        
        event.accept()
    
    def screen_to_original(self, screen_pos):
        """将屏幕坐标转换为原始图片坐标（修正版）"""
        if not self.original_pixmap:
            return None
            
        original_size = self.original_pixmap.size()
        if original_size.width() == 0 or original_size.height() == 0:
            return None
        
        # 计算当前显示图片的左上角位置（考虑偏移量）
        scaled_width = int(original_size.width() * self.scale_factor)
        scaled_height = int(original_size.height() * self.scale_factor)
        
        display_left = (self.width() - scaled_width) // 2 + self.offset.x()
        display_top = (self.height() - scaled_height) // 2 + self.offset.y()
        
        # 检查鼠标是否在图片显示区域内
        if not (display_left <= screen_pos.x() <= display_left + scaled_width and
                display_top <= screen_pos.y() <= display_top + scaled_height):
            return None
        
        # 转换为原始图片坐标（考虑缩放因子）
        original_x = int((screen_pos.x() - display_left) / self.scale_factor)
        original_y = int((screen_pos.y() - display_top) / self.scale_factor)
        
        # 确保坐标在原始图片范围内
        original_x = max(0, min(original_x, original_size.width() - 1))
        original_y = max(0, min(original_y, original_size.height() - 1))
        
        return QPoint(original_x, original_y)
    
    def original_to_screen(self, original_pos):
        """将原始图片坐标转换为屏幕坐标（修正版）"""
        if not self.original_pixmap:
            return None
            
        original_size = self.original_pixmap.size()
        if original_size.width() == 0 or original_size.height() == 0:
            return None
        
        # 计算当前显示图片的左上角位置（考虑偏移量）
        scaled_width = int(original_size.width() * self.scale_factor)
        scaled_height = int(original_size.height() * self.scale_factor)
        
        display_left = (self.width() - scaled_width) // 2 + self.offset.x()
        display_top = (self.height() - scaled_height) // 2 + self.offset.y()
        
        # 转换为屏幕坐标（考虑缩放因子）
        screen_x = display_left + original_pos.x() * self.scale_factor
        screen_y = display_top + original_pos.y() * self.scale_factor
        
        return QPoint(int(screen_x), int(screen_y))
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.mouse_press_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
        elif event.button() == Qt.RightButton:
            # 右键点击获取坐标
            self.emit_map_coordinates(event.pos())
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件（拖拽）"""
        if self.is_dragging:
            delta = event.pos() - self.mouse_press_pos
            self.mouse_press_pos = event.pos()
            self.offset += QPoint(delta.x(), delta.y())
            self.update_display()
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.setCursor(Qt.ArrowCursor)
        
        super().mouseReleaseEvent(event)
    
    def update_display(self):
        """更新地图显示"""
        if not self.original_pixmap:
            return

        # 计算缩放后的尺寸
        original_size = self.original_pixmap.size()
        scaled_width = int(original_size.width() * self.scale_factor)
        scaled_height = int(original_size.height() * self.scale_factor)

        # 缩放图片
        scaled_pixmap = self.original_pixmap.scaled(
            scaled_width, scaled_height,
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        # 创建画布
        canvas = QPixmap(self.size())
        canvas.fill(Qt.white)

        # 绘制图片（考虑偏移）
        painter = QPainter(canvas)
        x_offset = (self.width() - scaled_pixmap.width()) // 2 + self.offset.x()
        y_offset = (self.height() - scaled_pixmap.height()) // 2 + self.offset.y()
        painter.drawPixmap(x_offset, y_offset, scaled_pixmap)

        # 新增：绘制图标标记
        self.draw_marker(painter, x_offset, y_offset, scaled_width, scaled_height)

        painter.end()

        self.setPixmap(canvas)
    def draw_marker(self, painter, x_offset, y_offset, scaled_width, scaled_height):
        """绘制图标标记"""
        if not hasattr(self, 'last_marker_pos') or not self.last_marker_pos:
            return

        if not self.marker_icon or self.marker_icon.isNull():
            return

        # 将原始坐标转换为屏幕坐标
        marker_x, marker_y = self.last_marker_pos

        # 计算标记在缩放后图片中的位置
        screen_x = x_offset + marker_x * self.scale_factor
        screen_y = y_offset + marker_y * self.scale_factor

        # 绘制图标：底部中点对准目标位置
        icon_width = self.marker_icon.width()
        icon_height = self.marker_icon.height()
        draw_x = screen_x - icon_width // 2
        draw_y = screen_y - icon_height

        painter.drawPixmap(int(draw_x), int(draw_y), self.marker_icon)

    def emit_map_coordinates(self, click_pos):
        """发射地图点击坐标"""
        original_pos = self.screen_to_original(click_pos)
        if original_pos:
            # 新增：保存最后一个标记位置
            self.last_marker_pos = (original_pos.x(), original_pos.y())
            self.mapClicked.emit(original_pos.x(), original_pos.y())
            self.update_display()  # 触发重绘显示图标
    def clear_markers(self):
        """清除所有标记"""
        if hasattr(self, 'last_marker_pos'):
            self.last_marker_pos = None
        self.update_display()

    def reset_view(self):
        """重置视图"""
        self.scale_factor = 1.0
        self.offset = QPoint(0, 0)
        self.update_display()
    def create_test_map(self):
        """创建测试地图"""
        from PyQt5.QtGui import QPixmap, QPainter, QColor
    
        pixmap = QPixmap(800, 600)
        pixmap.fill(QColor(200, 230, 255))  # 浅蓝色背景

        painter = QPainter(pixmap)

        # 绘制简单地图
        painter.setPen(QColor(0, 100, 0))
        painter.setBrush(QColor(100, 200, 100))
        painter.drawRect(100, 100, 600, 400)  # 校园区域

        # 绘制建筑
        buildings = [
            (200, 200, 100, 80, "主楼"),
            (400, 300, 80, 60, "图书馆"), 
            (500, 150, 60, 90, "体育馆")
        ]

        for x, y, w, h, name in buildings:
            painter.setBrush(QColor(200, 200, 255))
            painter.drawRect(x, y, w, h)
            painter.drawText(x, y - 5, name)

        painter.end()
        self.original_pixmap = pixmap
        self.scaled_pixmap = pixmap
        self.update()