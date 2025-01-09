import requests
import time
import pygame
from math import sin, cos, radians
import json
from datetime import datetime

class PlaneTracker:
    def __init__(self):
        # Initialize Pygame for display
        pygame.init()
        self.width = 800
        self.height = 480  # Common portable display resolution
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Local Aircraft Tracker")
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (0, 0, 255)
        self.RED = (255, 0, 0)
        
        # Font
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Center coordinates (your location)
        self.CENTER_LAT = 0.0  # Replace with your latitude
        self.CENTER_LON = 0.0  # Replace with your longitude
        
        # Radar sweep animation
        self.sweep_angle = 0
        
    def fetch_aircraft_data(self):
        """
        Fetch aircraft data from OpenSky Network API
        Returns list of aircraft within range
        """
        # Define the bounding box (adjust these values based on your location)
        bounds = f"{self.CENTER_LAT-1},{self.CENTER_LAT+1},{self.CENTER_LON-1},{self.CENTER_LON+1}"
        url = f"https://opensky-network.org/api/states/all?lamin={bounds}"
        
        try:
            response = requests.get(url)
            data = response.json()
            return data['states'] if data and 'states' in data else []
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []
    
    def draw_radar_background(self):
        """Draw the radar circle and range rings"""
        self.screen.fill(self.BLACK)
        
        # Draw range rings
        for radius in range(50, 251, 50):
            pygame.draw.circle(self.screen, (30, 30, 30), 
                             (self.width//2, self.height//2), 
                             radius, 1)
        
        # Draw radar sweep
        sweep_end = (
            self.width//2 + cos(radians(self.sweep_angle)) * 250,
            self.height//2 - sin(radians(self.sweep_angle)) * 250
        )
        pygame.draw.line(self.screen, (0, 255, 0), 
                        (self.width//2, self.height//2),
                        sweep_end, 2)
        
    def draw_aircraft(self, aircraft_data):
        """Draw aircraft positions on the radar"""
        for aircraft in aircraft_data:
            if aircraft[6] and aircraft[5]:  # Check if latitude and longitude exist
                # Convert lat/lon to screen coordinates
                x = self.width//2 + (aircraft[5] - self.CENTER_LON) * 100
                y = self.height//2 - (aircraft[6] - self.CENTER_LAT) * 100
                
                # Draw aircraft blip
                pygame.draw.circle(self.screen, self.RED, (int(x), int(y)), 4)
                
                # Draw aircraft info
                if aircraft[1]:  # If callsign exists
                    text = self.small_font.render(aircraft[1], True, self.WHITE)
                    self.screen.blit(text, (x + 10, y - 10))
                
                # Draw altitude
                if aircraft[7]:  # If altitude exists
                    alt_text = f"{int(aircraft[7])}ft"
                    alt_surface = self.small_font.render(alt_text, True, self.WHITE)
                    self.screen.blit(alt_surface, (x + 10, y + 10))
    
    def run(self):
        """Main loop"""
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
            # Update radar sweep
            self.sweep_angle = (self.sweep_angle + 2) % 360
            
            # Draw radar background
            self.draw_radar_background()
            
            # Fetch and draw aircraft
            aircraft_data = self.fetch_aircraft_data()
            self.draw_aircraft(aircraft_data)
            
            # Update display
            pygame.display.flip()
            
            # Control frame rate
            clock.tick(30)
        
        pygame.quit()

if __name__ == "__main__":
    tracker = PlaneTracker()
    tracker.run()