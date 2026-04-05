import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

from globe3d.camera import Camera
from globe3d.globe import Globe
from globe3d.textures import TextureManager
from globe3d.data_viz import DataVisualizer

class Renderer:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        
        # 初始化组件
        self.camera = Camera(width, height)
        self.globe = Globe(radius=1.0, slices=64, stacks=32)
        self.texture_manager = TextureManager()
        self.data_viz = DataVisualizer(globe_radius=1.0)
        
        # 纹理状态
        self.current_texture_mode = 'earth'  # 'earth', 'clouds', 'night', 'combined'
        self.texture_modes = ['earth', 'clouds', 'night', 'combined']
        self.texture_mode_index = 0
        
        # 大气效果
        self.show_atmosphere = True
        
        # 初始化OpenGL
        self._init_opengl()
        
        # 添加示例数据
        self.data_viz.add_sample_data()
    
    def _init_opengl(self):
        """初始化OpenGL状态"""
        # 启用纹理
        glEnable(GL_TEXTURE_2D)
        
        # 启用深度测试
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        
        # 启用混合（用于透明度）
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # 设置清除颜色
        glClearColor(0.0, 0.0, 0.0, 1.0)
        
        # 设置视口
        glViewport(0, 0, self.width, self.height)
        
        # 设置透视投影
        self.camera.set_perspective()
        
        # 启用光照
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        # 设置光源
        glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 5.0, 5.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        
        # 启用颜色材质
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # 加载纹理
        self._load_textures()
    
    def _load_textures(self):
        """加载所有纹理"""
        self.earth_texture = self.texture_manager.get_texture('earth.jpg')
        self.cloud_texture = self.texture_manager.get_texture('clouds.jpg')
        self.night_texture = self.texture_manager.get_texture('night.jpg')
    
    def handle_event(self, event):
        """处理事件"""
        # 相机交互
        self.camera.handle_event(event)
        
        # 键盘控制
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # 切换纹理模式
                self.texture_mode_index = (self.texture_mode_index + 1) % len(self.texture_modes)
                self.current_texture_mode = self.texture_modes[self.texture_mode_index]
                print(f"Texture mode: {self.current_texture_mode}")
            
            elif event.key == pygame.K_a:
                # 切换自动旋转
                self.camera.auto_rotate = not self.camera.auto_rotate
                print(f"Auto rotate: {self.camera.auto_rotate}")
            
            elif event.key == pygame.K_g:
                # 切换大气效果
                self.show_atmosphere = not self.show_atmosphere
                print(f"Atmosphere: {self.show_atmosphere}")
            
            elif event.key == pygame.K_r:
                # 重置相机
                self.camera.distance = 3.0
                self.camera.rotation_x = 20.0
                self.camera.rotation_y = 45.0
    
    def update(self, delta_time):
        """更新状态"""
        self.camera.update(delta_time)
    
    def _draw_atmosphere(self):
        """绘制大气光晕效果"""
        if not self.show_atmosphere:
            return
        
        # 保存当前状态
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        
        # 禁用光照和纹理
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        
        # 绘制大气光晕（背面渲染）
        glFrontFace(GL_CW)  # 反转正面
        
        # 创建大气光晕球体（比地球稍大）
        atmosphere_radius = 1.05
        atmosphere_globe = Globe(radius=atmosphere_radius, slices=32, stacks=16)
        
        # 使用渐变颜色
        glBegin(GL_TRIANGLES)
        
        # 简化的大气效果：在地球周围绘制半透明球体
        for i in range(32):
            angle1 = 2 * np.pi * i / 32
            angle2 = 2 * np.pi * (i + 1) / 32
            
            # 顶点1
            x1 = atmosphere_radius * np.cos(angle1)
            y1 = atmosphere_radius * np.sin(angle1)
            
            # 顶点2
            x2 = atmosphere_radius * np.cos(angle2)
            y2 = atmosphere_radius * np.sin(angle2)
            
            # 颜色渐变
            alpha = 0.3
            glColor4f(0.3, 0.6, 1.0, alpha)
            glVertex3f(x1, y1, 0.0)
            glVertex3f(x2, y2, 0.0)
            glVertex3f(0.0, 0.0, atmosphere_radius)
            
            glColor4f(0.3, 0.6, 1.0, alpha * 0.5)
            glVertex3f(x1, y1, 0.0)
            glVertex3f(x2, y2, 0.0)
            glVertex3f(0.0, 0.0, -atmosphere_radius)
        
        glEnd()
        
        # 恢复状态
        glFrontFace(GL_CCW)
        glPopAttrib()
    
    def _draw_globe_with_texture(self, texture_id, alpha=1.0):
        """使用指定纹理绘制地球"""
        if texture_id is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            
            # 设置纹理环境
            glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
            
            # 如果需要透明度
            if alpha < 1.0:
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # 绘制地球
        self.globe.draw()
        
        # 清理状态
        if texture_id is not None:
            if alpha < 1.0:
                glDisable(GL_BLEND)
    
    def render(self):
        """渲染场景"""
        # 清除屏幕和深度缓冲
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # 应用相机变换
        self.camera.apply_transform()
        
        # 根据当前纹理模式绘制
        if self.current_texture_mode == 'earth':
            # 仅地球纹理
            glDisable(GL_BLEND)
            self._draw_globe_with_texture(self.earth_texture)
            
        elif self.current_texture_mode == 'clouds':
            # 仅云层
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            self._draw_globe_with_texture(self.cloud_texture, alpha=0.8)
            
        elif self.current_texture_mode == 'night':
            # 夜间模式
            glDisable(GL_BLEND)
            self._draw_globe_with_texture(self.night_texture)
            
        elif self.current_texture_mode == 'combined':
            # 组合模式：地球 + 云层
            # 先绘制地球
            glDisable(GL_BLEND)
            self._draw_globe_with_texture(self.earth_texture)
            
            # 再绘制云层（带透明度）
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            self._draw_globe_with_texture(self.cloud_texture, alpha=0.6)
        
        # 绘制数据可视化
        self.data_viz.draw_points()
        self.data_viz.draw_routes()
        
        # 绘制大气效果
        self._draw_atmosphere()
    
    def get_help_text(self):
        """获取帮助文本"""
        return (
            f"Current Texture Mode: {self.current_texture_mode}\n"
            f"Auto Rotate: {self.camera.auto_rotate}\n"
            f"Atmosphere: {self.show_atmosphere}\n"
            f"Distance: {self.camera.distance:.1f}\n"
            f"Rotation: ({self.camera.rotation_x:.1f}, {self.camera.rotation_y:.1f})\n"
            f"\n"
            f"Controls:\n"
            f"  SPACE - Cycle texture modes\n"
            f"  A - Toggle auto-rotate\n"
            f"  G - Toggle atmosphere\n"
            f"  R - Reset camera\n"
            f"  Mouse drag - Rotate\n"
            f"  Mouse wheel - Zoom"
        )