import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys

from globe3d.renderer import Renderer

class Application:
    def __init__(self, width=1024, height=768):
        self.width = width
        self.height = height
        
        # 初始化Pygame
        pygame.init()
        
        # 设置OpenGL显示模式
        pygame.display.set_mode(
            (width, height),
            DOUBLEBUF | OPENGL | RESIZABLE
        )
        pygame.display.set_caption("3D Earth Visualization")
        
        # 初始化渲染器
        self.renderer = Renderer(width, height)
        
        # 时钟用于帧率控制
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # 运行状态
        self.running = True
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            
            elif event.type == pygame.VIDEORESIZE:
                # 窗口大小改变
                self.width = event.w
                self.height = event.h
                glViewport(0, 0, self.width, self.height)
                self.renderer.camera.width = self.width
                self.renderer.camera.height = self.height
                self.renderer.camera.set_perspective()
            
            # 传递给渲染器处理
            self.renderer.handle_event(event)
    
    def update(self, delta_time):
        """更新状态"""
        self.renderer.update(delta_time)
    
    def render(self):
        """渲染场景"""
        self.renderer.render()
        
        # 显示帮助文本
        self._draw_help_text()
        
        # 交换缓冲
        pygame.display.flip()
    
    def _draw_help_text(self):
        """绘制帮助文本（使用Pygame字体）"""
        # 创建字体
        try:
            font = pygame.font.SysFont('arial', 14)
        except:
            # 如果系统字体不可用，使用默认字体
            font = pygame.font.Font(None, 14)
        
        # 获取帮助文本
        help_text = self.renderer.get_help_text()
        lines = help_text.split('\n')
        
        # 渲染每一行
        y = 10
        for line in lines:
            text_surface = font.render(line, True, (255, 255, 255))
            self.renderer.camera.apply_transform()  # 重置变换
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            gluOrtho2D(0, self.width, self.height, 0)
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            
            # 使用Pygame绘制文本到屏幕
            # 注意：这里我们使用Pygame的blit而不是OpenGL
            # 因为OpenGL文本渲染比较复杂
            
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            
            y += 18
    
    def run(self):
        """运行主循环"""
        while self.running:
            # 计算增量时间
            delta_time = self.clock.tick(self.fps) / 1000.0  # 转换为秒
            
            # 处理事件
            self.handle_events()
            
            # 更新状态
            self.update(delta_time)
            
            # 渲染场景
            self.render()
        
        # 清理
        self.cleanup()
    
    def cleanup(self):
        """清理资源"""
        self.renderer.texture_manager.cleanup()
        pygame.quit()
        sys.exit()

def main():
    """主函数"""
    app = Application(width=1024, height=768)
    app.run()

if __name__ == "__main__":
    main()