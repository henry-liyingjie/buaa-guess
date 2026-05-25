"""
run.py - 北航图寻应用启动脚本
"""
import sys
import os

# 确保当前目录（项目根目录）在Python模块搜索路径中
# 这会让Python将当前目录视为一个包（包含src子目录）
sys.path.insert(0, os.path.dirname(__file__))

from src.ui.main_window import MainWindow
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
