#src/ui/round_result_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class RoundResultDialog(QDialog):
    def __init__(self, round_num, round_score, total_score, correct_pos, parent=None):
        super().__init__(parent)
        self.round_num = round_num
        self.round_score = round_score
        self.total_score = total_score
        self.correct_pos = correct_pos
        
        self.setWindowTitle(f"第 {round_num} 轮结果")
        self.setFixedSize(350, 200)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel(f"第 {self.round_num} 轮结果")
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 得分信息
        score_info = QLabel(f"本轮得分: {self.round_score} 分")
        score_info.setFont(QFont("Microsoft YaHei", 12))
        score_info.setAlignment(Qt.AlignCenter)
        
        total_info = QLabel(f"累计总分: {self.total_score} 分")
        total_info.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        total_info.setAlignment(Qt.AlignCenter)
        
        pos_info = QLabel(f"正确位置: ({self.correct_pos[0]}, {self.correct_pos[1]})")
        pos_info.setFont(QFont("Microsoft YaHei", 10))
        pos_info.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(score_info)
        layout.addWidget(total_info)
        layout.addWidget(pos_info)
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
