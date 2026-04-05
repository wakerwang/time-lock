import numpy as np
from OpenGL.GL import *

class Globe:
    def __init__(self, radius=1.0, slices=64, stacks=32):
        """
        初始化球体
        radius: 球体半径
        slices: 经度方向的分割数 (类似于经线)
        stacks: 纬度方向的分割数 (类似于纬线)
        """
        self.radius = radius
        self.slices = slices
        self.stacks = stacks
        self.vertices = []
        self.normals = []
        self.tex_coords = []
        self.indices = []
        
        self._generate_sphere()
    
    def _generate_sphere(self):
        """生成球体的顶点、法线、纹理坐标和索引"""
        for i in range(self.stacks + 1):
            stack_angle = np.pi * i / self.stacks - np.pi / 2  # 从 -π/2 到 π/2
            xy = self.radius * np.cos(stack_angle)
            z = self.radius * np.sin(stack_angle)
            
            for j in range(self.slices + 1):
                slice_angle = 2 * np.pi * j / self.slices  # 从 0 到 2π
                
                x = xy * np.cos(slice_angle)
                y = xy * np.sin(slice_angle)
                
                # 顶点位置
                self.vertices.append([x, y, z])
                
                # 法线 (单位化的位置向量)
                length = np.sqrt(x*x + y*y + z*z)
                if length > 0:
                    self.normals.append([x/length, y/length, z/length])
                else:
                    self.normals.append([0, 0, 1])
                
                # 纹理坐标 (u, v)
                u = j / self.slices
                v = i / self.stacks
                self.tex_coords.append([u, v])
        
        # 生成索引 (三角形 strip)
        for i in range(self.stacks):
            for j in range(self.slices + 1):
                first = i * (self.slices + 1) + j
                second = first + self.slices + 1
                self.indices.append(first)
                self.indices.append(second)
                
                if i < self.stacks - 1:
                    self.indices.append(first + 1)
                    self.indices.append(second + 1)
    
    def get_vertices(self):
        """返回顶点数据"""
        return np.array(self.vertices, dtype=np.float32)
    
    def get_normals(self):
        """返回法线数据"""
        return np.array(self.normals, dtype=np.float32)
    
    def get_tex_coords(self):
        """返回纹理坐标数据"""
        return np.array(self.tex_coords, dtype=np.float32)
    
    def get_indices(self):
        """返回索引数据"""
        return np.array(self.indices, dtype=np.uint32)
    
    def draw(self):
        """使用OpenGL绘制球体"""
        from OpenGL.GL import (
            glEnableClientState, glVertexPointer, glNormalPointer, glTexCoordPointer,
            glDrawElements, GL_VERTEX_ARRAY, GL_NORMAL_ARRAY, GL_TEXTURE_COORD_ARRAY,
            GL_UNSIGNED_INT, GL_TRIANGLE_STRIP
        )
        
        vertices = self.get_vertices()
        normals = self.get_normals()
        tex_coords = self.get_tex_coords()
        indices = self.get_indices()
        
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        
        glVertexPointer(3, GL_FLOAT, 0, vertices)
        glNormalPointer(GL_FLOAT, 0, normals)
        glTexCoordPointer(2, GL_FLOAT, 0, tex_coords)
        
        glDrawElements(GL_TRIANGLE_STRIP, len(indices), GL_UNSIGNED_INT, indices)
        
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)