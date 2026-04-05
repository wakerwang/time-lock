import numpy as np
import math

class DataVisualizer:
    def __init__(self, globe_radius=1.0):
        self.globe_radius = globe_radius
        self.data_points = []
        self.routes = []
        
    def add_data_point(self, latitude, longitude, value=1.0, color=None):
        if color is None:
            intensity = min(1.0, max(0.0, value))
            r = intensity
            b = 1.0 - intensity
            g = 0.0
            color = (r, g, b)
        
        self.data_points.append({
            'lat': latitude,
            'lon': longitude,
            'value': value,
            'color': color
        })
    
    def add_route(self, coordinates, color=(1.0, 1.0, 0.0), width=2.0):
        self.routes.append({
            'coordinates': coordinates,
            'color': color,
            'width': width
        })
    
    def lat_lon_to_cartesian(self, lat, lon, radius=None):
        if radius is None:
            radius = self.globe_radius
            
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        
        x = radius * math.cos(lat_rad) * math.cos(lon_rad)
        y = radius * math.cos(lat_rad) * math.sin(lon_rad)
        z = radius * math.sin(lat_rad)
        
        return (x, y, z)
    
    def draw_points(self):
        from OpenGL.GL import glPointSize, glBegin, glEnd, glColor3f, glVertex3f, GL_POINTS
        
        glPointSize(5.0)
        glBegin(GL_POINTS)
        
        for point in self.data_points:
            x, y, z = self.lat_lon_to_cartesian(
                point['lat'], 
                point['lon'], 
                self.globe_radius + 0.02
            )
            
            r, g, b = point['color']
            glColor3f(r, g, b)
            glVertex3f(x, y, z)
        
        glEnd()
    
    def draw_routes(self):
        from OpenGL.GL import glLineWidth, glBegin, glEnd, glColor3f, glVertex3f, GL_LINE_STRIP
        
        for route in self.routes:
            glLineWidth(route['width'])
            glBegin(GL_LINE_STRIP)
            
            r, g, b = route['color']
            glColor3f(r, g, b)
            
            for lat, lon in route['coordinates']:
                x, y, z = self.lat_lon_to_cartesian(
                    lat, 
                    lon, 
                    self.globe_radius + 0.01
                )
                glVertex3f(x, y, z)
            
            glEnd()
    
    def add_sample_data(self):
        cities = [
            ("Beijing", 39.9, 116.4, 0.9),
            ("Shanghai", 31.2, 121.5, 0.8),
            ("Guangzhou", 23.1, 113.3, 0.7),
            ("Shenzhen", 22.5, 114.1, 0.7),
            ("New York", 40.7, -74.0, 0.9),
            ("London", 51.5, -0.1, 0.8),
            ("Paris", 48.9, 2.4, 0.7),
            ("Tokyo", 35.7, 139.7, 0.8),
            ("Sydney", -33.9, 151.2, 0.6),
            ("Rio", -22.9, -43.2, 0.5),
            ("Cairo", 30.0, 31.2, 0.6),
            ("Cape Town", -33.9, 18.4, 0.5),
        ]
        
        for name, lat, lon, value in cities:
            self.add_data_point(lat, lon, value)
        
        routes = [
            [(39.9, 116.4), (51.5, -0.1)],
            [(31.2, 121.5), (40.7, -74.0)],
            [(22.5, 114.1), (35.7, 139.7)],
            [(51.5, -0.1), (48.9, 2.4)],
        ]
        
        colors = [(1.0, 0.5, 0.0), (0.0, 0.8, 1.0), (0.5, 1.0, 0.5), (1.0, 0.0, 1.0)]
        for i, route_coords in enumerate(routes):
            self.add_route(route_coords, color=colors[i % len(colors)])
