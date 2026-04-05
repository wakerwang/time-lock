import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

class Camera:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        
        # 相机位置和方向
        self.distance = 3.0  # 从地球中心的距离
        self.rotation_x = 20.0  # 垂直旋转角度 (俯仰)
        self.rotation_y = 45.0  # 水平旋转角度 (偏航)
        
        # 鼠标交互状态
        self.mouse_pressed = False
        self.last_mouse_pos = (0, 0)
        
        # 缩放敏感度
        self.zoom_sensitivity = 0.1
        self.rotation_sensitivity = 0.5
        
        # 自动旋转
        self.auto_rotate = True
        self.auto_rotate_speed = 0.3
        
    def handle_event(self, event):
        """处理Pygame事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键按下
                self.mouse_pressed = True
                self.last_mouse_pos = event.pos
            elif event.button == 4:  # 滚轮上拉 (放大)
                self.distance = max(1.5, self.distance - self.zoom_sensitivity)
            elif event.button == 5:  # 滚轮下拉 (缩小)
                self.distance = min(10.0, self.distance + self.zoom_sensitivity)
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # 左键释放
                self.mouse_pressed = False
                
        elif event.type == pygame.MOUSEMOTION:
            if self.mouse_pressed:
                # 计算鼠标移动
                dx = event.pos[0] - self.last_mouse_pos[0]
                dy = event.pos[1] - self.last_mouse_pos[1]
                
                # 更新旋转角度
                self.rotation_y += dx * self.rotation_sensitivity
                self.rotation_x += dy * self.rotation_sensitivity
                
                # 限制垂直旋转避免翻转
                self.rotation_x = max(-89, min(89, self.rotation_x))
                
                self.last_mouse_pos = event.pos
    
    def update(self, delta_time):
        """更新相机状态"""
        if self.auto_rotate:
            # 自动旋转（水平方向）
            self.rotation_y += self.auto_rotate_speed * delta_time
            
            # 保持角度在合理范围内
            if self.rotation_y > 360:
                self.rotation_y -= 360
            elif self.rotation_y < 0:
                self.rotation_y += 360
    
    def apply_transform(self):
        """应用相机变换到OpenGL"""
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # 移动相机后退
        glTranslatef(0.0, 0.0, -self.distance)
        
        # 应用旋转
        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)  # X轴旋转 (俯仰)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)  # Y轴旋转 (偏航)
    
    def set_perspective(self):
        """设置透视投影"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, self.width / self.height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
    
    def get_position(self):
        """获取相机在世界空间中的位置"""
        # 根据距离和旋转计算实际位置
        rad_x = np.radians(self.rotation_x)
        rad_y = np.radians(self.rotation_y)
        
        x = self.distance * np.cos(rad_x) * np.sin(rad_y)
        y = self.distance * np.sin(rad_x)
        z = self.distance * np.cos(rad_x) * np.cos(rad_y)
        
        return np.array([x, y, z])
    
    def get_forward_vector(self):
        """获取相机前进方向（视线方向）"""
        pos = self.get_position()
        # 视线方向是从相机指向原点
        forward = -pos
        norm = np.linalg.norm(forward)
        if norm > 0:
            return forward / norm
        return np.array([0, 0, -1])