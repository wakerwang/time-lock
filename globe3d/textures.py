import numpy as np
from PIL import Image
import os

class TextureManager:
    def __init__(self):
        self.textures = {}
        self.texture_dir = os.path.join(os.path.dirname(__file__), 'assets')
        
    def load_texture(self, filename):
        """加载图像文件作为OpenGL纹理"""
        filepath = os.path.join(self.texture_dir, filename)
        
        # 如果文件不存在，生成程序化纹理
        if not os.path.exists(filepath):
            print(f"Texture file {filename} not found, generating procedural texture...")
            texture_data = self.generate_procedural_texture(filename)
        else:
            # 加载实际图像文件
            image = Image.open(filepath)
            # 使用transpose方法进行垂直翻转，OpenGL期望的方向
            # PIL中FLIP_TOP_BOTTOM对应的数值是1
            image = image.transpose(1)
            img_data = np.array(image, dtype=np.uint8)
            texture_data = img_data
            
        # 生成OpenGL纹理ID
        from OpenGL.GL import glGenTextures, glBindTexture, glTexImage2D, glTexParameteri
        from OpenGL.GL import GL_TEXTURE_2D, GL_RGB, GL_RGBA, GL_UNSIGNED_BYTE
        from OpenGL.GL import GL_LINEAR, GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER
        
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        
        # 确定颜色格式
        if len(texture_data.shape) == 3:
            if texture_data.shape[2] == 4:
                gl_format = GL_RGBA
            else:
                gl_format = GL_RGB
        else:
            gl_format = GL_RGB  # 灰度图像转RGB
            
        glTexImage2D(GL_TEXTURE_2D, 0, gl_format, 
                    texture_data.shape[1], texture_data.shape[0], 
                    0, gl_format, GL_UNSIGNED_BYTE, texture_data)
        
        # 设置纹理参数
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        self.textures[filename] = texture_id
        return texture_id
    
    def generate_procedural_texture(self, filename):
        """生成程序化纹理用于演示"""
        width, height = 2048, 1024
        
        if 'earth' in filename.lower():
            # 生成简化的地球纹理：蓝色海洋 + 绿色/棕色陆地
            texture = np.zeros((height, width, 3), dtype=np.uint8)
            
            # 海洋 - 深蓝色
            texture[:] = [10, 50, 120]
            
            # 大陆区域 - 简单的几何形状
            for y in range(height):
                lat = (y / height) * 2 * np.pi - np.pi  # -π to π
                for x in range(width):
                    lon = (x / width) * 2 * np.pi  # 0 to 2π
                    
                    # 简单的陆地分布模式
                    land_factor = 0
                    
                    # 非洲-like
                    if -np.pi/3 < lon < np.pi/2 and np.pi/6 < lat < np.pi/2:
                        land_factor = 0.8
                    # 欧亚大陆-like
                    elif np.pi/3 < lon < np.pi and np.pi/4 < lat < np.pi/2:
                        land_factor = 0.7
                    # 北美洲-like
                    elif -np.pi < lon < -2*np.pi/3 and np.pi/3 < lat < np.pi/2:
                        land_factor = 0.6
                    # 南美洲-like
                    elif -np.pi/2 < lon < np.pi/6 and -np.pi/2 < lat < 0:
                        land_factor = 0.5
                    # 澳大利亚-like
                    elif np.pi/2 < lon < np.pi*5/6 and -np.pi/3 < lat < 0:
                        land_factor = 0.4
                    # 印度-东南亚-like
                    elif np.pi/2 < lon < np.pi and np.pi/6 < lat < np.pi/3:
                        land_factor = 0.5
                        
                    if land_factor > 0.3:
                        # 陆地 - 绿棕色
                        green_intensity = int(50 + land_factor * 100)
                        brown_intensity = int(30 + land_factor * 80)
                        texture[y, x] = [brown_intensity, green_intensity, 20]
                    # 添加一些随机性使其看起来更自然
                    elif np.random.random() > 0.98:  # 偶尔的绿色斑点
                        texture[y, x] = [20, 80, 20]
                        
        elif 'cloud' in filename.lower():
            # 生成云层纹理：白色半透明云朵
            texture = np.zeros((height, width, 4), dtype=np.uint8)  # RGBA
            
            # 基础透明蓝色背景
            texture[:] = [135, 206, 235, 30]  # 浅蓝色，低透明度
            
            # 添加云朵
            np.random.seed(42)  # 一致的云朵分布
            for _ in range(300):  # 云朵数量
                x = np.random.randint(0, width)
                y = np.random.randint(0, height)
                size_x = np.random.randint(30, 150)
                size_y = np.random.randint(20, 80)
                
                # 高斯分布的云朵
                for dy in range(-size_y//2, size_y//2):
                    for dx in range(-size_x//2, size_x//2):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            distance = np.sqrt((dx/size_x)**2 + (dy/size_y)**2)
                            if distance < 1.0:
                                alpha = int(200 * (1 - distance**2))
                                current_alpha = int(texture[ny, nx, 3])
                                new_alpha = min(255, current_alpha + alpha)
                                texture[ny, nx] = [255, 255, 255, new_alpha]
                                
        elif 'night' in filename.lower():
            # 生成夜间灯光纹理：黑色背景 + 城市灯光点
            texture = np.zeros((height, width, 3), dtype=np.uint8)
            
            # 添加城市灯光
            np.random.seed(123)  # 一致的灯光分布
            for _ in range(5000):  # 城市数量
                x = np.random.randint(0, width)
                y = np.random.randint(0, height)
                
                # 使灯光更多分布在陆地区域（简化判断）
                land_probability = 0.3
                if (np.pi/3 < (x/width)*2*np.pi < np.pi and  # 欧亚
                    np.pi/4 < (y/height)*2*np.pi-np.pi < np.pi/2) or \
                   (-np.pi < (x/width)*2*np.pi < -2*np.pi/3 and  # 北美
                    np.pi/3 < (y/height)*2*np.pi-np.pi < np.pi/2) or \
                   (-np.pi/2 < (x/width)*2*np.pi < np.pi/6 and  # 南美
                    -np.pi/2 < (y/height)*2*np.pi-np.pi < 0):
                    land_probability = 0.7
                    
                if np.random.random() < land_probability:
                    # 城市灯光 - 黄白色
                    intensity = np.random.randint(100, 255)
                    size = np.random.randint(1, 4)
                    
                    for dy in range(-size, size+1):
                        for dx in range(-size, size+1):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < width and 0 <= ny < height:
                                distance = np.sqrt(dx*dx + dy*dy)
                                if distance <= size:
                                    falloff = 1.0 - (distance / size)
                                    brightness = int(intensity * falloff * 0.7)
                                    texture[ny, nx] = [
                                        min(255, texture[ny, nx][0] + brightness),
                                        min(255, texture[ny, nx][1] + brightness//2),
                                        min(255, texture[ny, nx][2] + brightness//4)
                                    ]
        else:
            # 默认纹理：彩色棋盘纹理
            texture = np.zeros((height, width, 3), dtype=np.uint8)
            tile_size = 64
            for y in range(height):
                for x in range(width):
                    tile_x = (x // tile_size) % 2
                    tile_y = (y // tile_size) % 2
                    if (tile_x + tile_y) % 2 == 0:
                        texture[y, x] = [100, 149, 237]  # 玉米花蓝
                    else:
                        texture[y, x] = [255, 255, 255]  # 白色
                        
        return texture
    
    def get_texture(self, name):
        """获取纹理ID，如果不存在则加载"""
        if name not in self.textures:
            self.load_texture(name)
        return self.textures.get(name)
    
    def cleanup(self):
        """清理所有纹理"""
        from OpenGL.GL import glDeleteTextures
        if self.textures:
            glDeleteTextures(len(self.textures), list(self.textures.values()))
            self.textures.clear()