#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片桌面固定器 - Pin An Image

版本：1.0
创建时间：2026-04-28
创建人：Holy

功能说明：
- 打开并显示图片
- 将图片固定在桌面上
- 支持拖动调整窗口大小
- 支持保持最上层显示（不受Windows+D影响）
- 支持通过托盘图标操作
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QMenu, QAction,
                             QFileDialog, QSizePolicy, QSystemTrayIcon, QMenu, QStyle)
from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtCore import Qt, QSize, QPoint, QRect

class PinAnImage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # 设置窗口无边框
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # 初始窗口大小
        window_width, window_height = 400, 300
        
        # 获取屏幕尺寸，计算窗口居中位置
        screen_geometry = QApplication.desktop().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        
        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 设置窗口位置和大小
        self.setGeometry(x, y, window_width, window_height)
        
        # 创建图片标签
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setCentralWidget(self.image_label)
        
        # 为图片标签安装事件过滤器，用于处理鼠标移动事件
        self.image_label.installEventFilter(self)
        
        # 右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        
        # 当前图片路径
        self.current_image_path = None
        
        # 存储原始图片用于缩放
        self.original_image = None
        
        # 保持最上层显示标志
        self.stay_on_top = False
        
        # 调整大小相关
        self.resizing = False
        self.resize_edge = None
        self.resize_start_pos = None
        self.resize_start_geometry = None
        self.edge_threshold = 10  # 边缘检测阈值
        
        # 托盘图标
        self.createTrayIcon()
        
        # 设置背景样式
        self.setStyleSheet("background-color: rgba(200, 200, 200, 200);")
        
        # 设置窗口图标（任务栏图标）
        self.setWindowIcon(self.createAppIcon())
        
        # 显示初始提示
        self.showNoImageHint()
        
        # 显示窗口
        self.show()
        
        # 窗口激活到最前
        self.activateWindow()
        self.raise_()
        
    def createTrayIcon(self):
        """创建系统托盘图标"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.createAppIcon())
        
        # 托盘图标点击事件
        self.tray_icon.activated.connect(self.onTrayIconActivated)
        
        self.tray_menu = QMenu()
        
        # 托盘打开图片选项
        open_action = QAction("打开图片", self)
        open_action.triggered.connect(self.openImage)
        
        # 托盘保持最上层显示选项
        self.tray_stay_on_top_action = QAction("保持最上层显示", self, checkable=True)
        self.tray_stay_on_top_action.setChecked(self.stay_on_top)
        self.tray_stay_on_top_action.triggered.connect(self.toggleStayOnTop)
        
        close_action = QAction("退出软件", self)
        close_action.triggered.connect(self.quitApplication)
        
        self.tray_menu.addAction(open_action)
        self.tray_menu.addAction(self.tray_stay_on_top_action)
        self.tray_menu.addAction(close_action)
        
        # 菜单显示前更新状态
        self.tray_menu.aboutToShow.connect(self.updateTrayMenu)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        
    def updateTrayMenu(self):
        """更新托盘菜单状态"""
        self.tray_stay_on_top_action.setChecked(self.stay_on_top)
        
    def quitApplication(self):
        """退出应用程序"""
        # 隐藏托盘图标
        self.tray_icon.hide()
        # 关闭窗口
        self.close()
        # 退出应用程序
        QApplication.quit()
        
    def createAppIcon(self):
        """创建应用图标：图片被图钉钉着"""
        from PyQt5.QtGui import QPainter, QColor, QLinearGradient
        
        # 创建一个32x32的图标
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制图片边框（模拟相框）
        painter.setBrush(QColor(240, 240, 240))  # 白色背景
        painter.setPen(QColor(180, 180, 180))
        painter.drawRect(4, 8, 24, 18)
        
        # 绘制图片内容（模拟风景照片）
        # 天空渐变
        sky_gradient = QLinearGradient(5, 9, 5, 18)
        sky_gradient.setColorAt(0, QColor(100, 150, 255))
        sky_gradient.setColorAt(1, QColor(200, 220, 255))
        painter.setBrush(sky_gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRect(5, 9, 22, 12)
        
        # 太阳
        painter.setBrush(QColor(255, 255, 100))
        painter.drawEllipse(22, 10, 5, 5)
        
        # 地面/草地
        painter.setBrush(QColor(50, 150, 50))
        painter.drawRect(5, 20, 22, 6)
        
        # 简化的树
        painter.setBrush(QColor(30, 100, 30))
        painter.drawEllipse(10, 16, 6, 8)
        painter.setBrush(QColor(100, 80, 50))
        painter.drawRect(12, 22, 2, 4)
        
        # 图片边框阴影效果
        painter.setPen(QColor(150, 150, 150))
        painter.drawLine(28, 9, 28, 26)
        painter.drawLine(5, 26, 27, 26)
        
        # 绘制图钉
        # 图钉头部（圆形）
        painter.setBrush(QColor(255, 80, 80))  # 红色
        painter.setPen(QColor(150, 30, 30))
        painter.drawEllipse(12, 2, 8, 8)
        
        # 图钉高光
        painter.setBrush(QColor(255, 150, 150))
        painter.drawEllipse(13, 3, 3, 3)
        
        # 图钉针身
        painter.setPen(QColor(180, 180, 180))
        painter.setBrush(Qt.NoBrush)
        painter.drawLine(16, 9, 16, 13)
        
        # 图钉尖端
        painter.drawLine(16, 13, 14, 16)
        painter.drawLine(16, 13, 18, 16)
        
        painter.end()
        
        return QIcon(pixmap)
        
    def onTrayIconActivated(self, reason):
        """托盘图标激活事件处理"""
        if reason == QSystemTrayIcon.DoubleClick or reason == QSystemTrayIcon.Trigger:
            # 点击托盘图标时，将窗口显示到最前面
            self.show()
            self.activateWindow()
            self.raise_()
        
    def showContextMenu(self, pos):
        """显示右键菜单"""
        menu = QMenu(self)
        
        # 保持最上层显示选项
        stay_on_top_action = QAction("保持最上层显示", self, checkable=True)
        stay_on_top_action.setChecked(self.stay_on_top)
        stay_on_top_action.triggered.connect(self.toggleStayOnTop)
        
        open_action = QAction("打开图片", self)
        open_action.triggered.connect(self.openImage)
        
        close_action = QAction("退出软件", self)
        close_action.triggered.connect(self.quitApplication)
        
        menu.addAction(stay_on_top_action)
        menu.addAction(open_action)
        menu.addAction(close_action)
        
        menu.exec_(self.mapToGlobal(pos))
        
    def toggleStayOnTop(self, checked):
        """切换保持最上层显示功能"""
        self.stay_on_top = checked
        
        if checked:
            # 启用保持最上层显示
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            # 关闭保持最上层显示
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        
        # 重新显示窗口以应用新的标志
        self.show()
        
    def openImage(self):
        """打开图片文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", 
                                                   "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)")
        
        if file_path:
            self.loadImage(file_path)
            
    def showNoImageHint(self):
        """显示无图片提示"""
        self.image_label.setText("<h1 style='color: #666;'>点击打开图片</h1>")
        self.image_label.setStyleSheet("background-color: rgba(200, 200, 200, 200);")
        self.image_label.mousePressEvent = self.onLabelClick
        
    def onLabelClick(self, event):
        """点击标签打开图片"""
        if event.button() == Qt.LeftButton:
            if not self.current_image_path:
                self.openImage()
            else:
                # 已有图片时，调用父类的鼠标事件处理拖动
                QLabel.mousePressEvent(self.image_label, event)
                self.mousePressEvent(event)
        else:
            # 右键点击，调用父类的鼠标事件以显示右键菜单
            QLabel.mousePressEvent(self.image_label, event)
    
    def loadImage(self, file_path):
        """加载图片"""
        self.current_image_path = file_path
        
        # 加载图片
        self.original_image = QImage(file_path)
        
        if self.original_image.isNull():
            return
            
        # 获取屏幕尺寸
        screen_geometry = QApplication.desktop().availableGeometry()
        max_width = screen_geometry.width() - 20
        max_height = screen_geometry.height() - 20
        
        # 计算缩放比例
        image_ratio = self.original_image.width() / self.original_image.height()
        screen_ratio = max_width / max_height
        
        if image_ratio > screen_ratio:
            new_width = max_width
            new_height = int(max_width / image_ratio)
        else:
            new_height = max_height
            new_width = int(max_height * image_ratio)
        
        self.updateImageDisplay(new_width, new_height)
        
        # 计算居中位置
        x = (screen_geometry.width() - new_width) // 2
        y = (screen_geometry.height() - new_height) // 2
        
        # 设置窗口位置
        self.move(x, y)
        
        # 加载图片后，隐藏任务栏图标（使用工具窗口标志）
        self.setWindowFlags(self.windowFlags() | Qt.Tool)
        
        # 加载图片后保持在最前面
        self.show()
        self.activateWindow()
        self.raise_()
        
    def updateImageDisplay(self, width, height):
        """更新图片显示"""
        if self.original_image and not self.original_image.isNull():
            pixmap = QPixmap.fromImage(self.original_image).scaled(width, height,
                                                                  Qt.KeepAspectRatio,
                                                                  Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
            self.image_label.setStyleSheet("background-color: transparent;")
            self.resize(width, height)
        
    def zoomIn(self):
        """放大图片"""
        current_size = self.size()
        new_width = int(current_size.width() * 1.2)
        new_height = int(current_size.height() * 1.2)
        self.resize(new_width, new_height)
        
    def zoomOut(self):
        """缩小图片"""
        current_size = self.size()
        new_width = int(current_size.width() * 0.8)
        new_height = int(current_size.height() * 0.8)
        
        # 最小尺寸限制
        if new_width > 50 and new_height > 50:
            self.resize(new_width, new_height)
            
    def getResizeEdge(self, pos):
        """检测鼠标位置是否在窗口边缘，返回边缘类型"""
        width = self.width()
        height = self.height()
        x, y = pos.x(), pos.y()
        
        left = x < self.edge_threshold
        right = x > width - self.edge_threshold
        top = y < self.edge_threshold
        bottom = y > height - self.edge_threshold
        
        if left and top:    
            return 'topleft'
        elif right and top:
            return 'topright'
        elif left and bottom:
            return 'bottomleft'
        elif right and bottom:
            return 'bottomright'
        elif left:
            return 'left'
        elif right:
            return 'right'
        elif top:
            return 'top'
        elif bottom:
            return 'bottom'
        return None
        
    def updateCursor(self, edge):
        """根据边缘类型更新鼠标光标"""
        if edge in ['left', 'right']:
            cursor = Qt.SizeHorCursor
        elif edge in ['top', 'bottom']:
            cursor = Qt.SizeVerCursor
        elif edge in ['topleft', 'bottomright']:
            cursor = Qt.SizeFDiagCursor
        elif edge in ['topright', 'bottomleft']:
            cursor = Qt.SizeBDiagCursor
        else:
            cursor = Qt.ArrowCursor
        
        # 在窗口和图片标签上都设置光标
        self.setCursor(cursor)
        self.image_label.setCursor(cursor)
        
    def mousePressEvent(self, event):
        """鼠标按下事件，用于拖动窗口或调整大小"""
        if event.button() == Qt.LeftButton:
            # 检测是否在边缘
            edge = self.getResizeEdge(event.pos())
            
            if edge and self.current_image_path:
                # 开始调整大小
                self.resizing = True
                self.resize_edge = edge
                self.resize_start_pos = event.globalPos()
                self.resize_start_geometry = self.geometry()
            else:
                # 拖动窗口
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
    def eventFilter(self, obj, event):
        """事件过滤器，处理图片标签的鼠标移动事件"""
        if obj == self.image_label and event.type() == event.MouseMove:
            # 将标签的坐标转换为窗口坐标
            window_pos = self.image_label.mapTo(self, event.pos())
            
            if event.buttons() == Qt.LeftButton:
                if self.resizing:
                    # 调整窗口大小
                    self.doResize(event.globalPos())
                else:
                    # 拖动窗口
                    self.move(event.globalPos() - self.drag_position)
                return True
            else:
                # 仅移动鼠标时，更新光标样式
                edge = self.getResizeEdge(window_pos)
                self.updateCursor(edge)
                return True
                
        elif obj == self.image_label and event.type() == event.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                # 如果没有打开图片，左键点击打开选择图片窗口
                if not self.current_image_path:
                    self.openImage()
                    return True
                    
                # 将标签的坐标转换为窗口坐标
                window_pos = self.image_label.mapTo(self, event.pos())
                edge = self.getResizeEdge(window_pos)
                
                if edge and self.current_image_path:
                    # 开始调整大小
                    self.resizing = True
                    self.resize_edge = edge
                    self.resize_start_pos = event.globalPos()
                    self.resize_start_geometry = self.geometry()
                else:
                    # 拖动窗口
                    self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                return True
            # 右键点击不处理，让事件继续传递以显示右键菜单
            else:
                return False
                
        elif obj == self.image_label and event.type() == event.MouseButtonRelease:
            if event.button() == Qt.LeftButton:
                self.resizing = False
                self.resize_edge = None
                self.setCursor(Qt.ArrowCursor)
                self.image_label.setCursor(Qt.ArrowCursor)
                return True
                
        return super().eventFilter(obj, event)
        
    def mouseMoveEvent(self, event):
        """鼠标移动事件，用于拖动窗口或调整大小"""
        if event.buttons() == Qt.LeftButton:
            if self.resizing:
                # 调整窗口大小
                self.doResize(event.globalPos())
            else:
                # 拖动窗口
                self.move(event.globalPos() - self.drag_position)
            event.accept()
        else:
            # 仅移动鼠标时，更新光标样式
            edge = self.getResizeEdge(event.pos())
            self.updateCursor(edge)
            
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.resizing = False
            self.resize_edge = None
            self.setCursor(Qt.ArrowCursor)
            self.image_label.setCursor(Qt.ArrowCursor)
            event.accept()
            
    def doResize(self, global_pos):
        """执行调整大小操作"""
        if not self.resize_edge or not self.resize_start_geometry:
            return
            
        delta = global_pos - self.resize_start_pos
        geo = self.resize_start_geometry
        
        new_x = geo.x()
        new_y = geo.y()
        new_width = geo.width()
        new_height = geo.height()
        
        # 根据边缘类型计算新的大小和位置
        if 'left' in self.resize_edge:
            new_width = max(100, geo.width() - delta.x())
            new_x = geo.x() + geo.width() - new_width
        if 'right' in self.resize_edge:
            new_width = max(100, geo.width() + delta.x())
            
        if 'top' in self.resize_edge:
            new_height = max(100, geo.height() - delta.y())
            new_y = geo.y() + geo.height() - new_height
        if 'bottom' in self.resize_edge:
            new_height = max(100, geo.height() + delta.y())
        
        # 保持图片比例
        if self.original_image and not self.original_image.isNull():
            image_ratio = self.original_image.width() / self.original_image.height()
            
            # 根据调整方向决定以哪个维度为基准
            if self.resize_edge in ['left', 'right']:
                # 水平调整，以宽度为基准
                new_height = int(new_width / image_ratio)
            elif self.resize_edge in ['top', 'bottom']:
                # 垂直调整，以高度为基准
                new_width = int(new_height * image_ratio)
            else:
                # 角落调整，取变化较大的维度
                width_ratio = new_width / geo.width()
                height_ratio = new_height / geo.height()
                if width_ratio > height_ratio:
                    new_height = int(new_width / image_ratio)
                else:
                    new_width = int(new_height * image_ratio)
        
        # 设置新位置和大小
        self.setGeometry(new_x, new_y, new_width, new_height)
        
        # 更新图片显示
        if self.original_image and not self.original_image.isNull():
            pixmap = QPixmap.fromImage(self.original_image).scaled(new_width, new_height,
                                                                  Qt.KeepAspectRatio,
                                                                  Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置应用程序名称
    app.setApplicationName("图片桌面固定器")
    
    window = PinAnImage()
    
    sys.exit(app.exec_())