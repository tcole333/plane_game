from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
import asyncio
from datetime import datetime
import random
from typing import Dict, Set, List
import pygame
import uvicorn

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GameState:
    def __init__(self):
        self.active_planes: Dict[str, dict] = {}  # identifier -> plane data
        self.player_scores: Dict[str, int] = {}   # player name -> score
        self.connected_clients: Set[WebSocket] = set()
        self.game_mode = False
        self.CENTER_LAT = 0.0  # Replace with your latitude
        self.CENTER_LON = 0.0  # Replace with your longitude

    async def broadcast_state(self):
        """Broadcast current game state to all connected clients"""
        if not self.connected_clients:
            return
            
        game_data = {
            'activePlanes': self.active_planes,
            'scores': self.player_scores,
            'gameMode': self.game_mode
        }
        
        for client in self.connected_clients:
            try:
                await client.send_json(game_data)
            except:
                self.connected_clients.remove(client)

    def fetch_aircraft_data(self) -> List[dict]:
        """Fetch real aircraft data from OpenSky Network"""
        bounds = f"{self.CENTER_LAT-1},{self.CENTER_LAT+1},{self.CENTER_LON-1},{self.CENTER_LON+1}"
        url = f"https://opensky-network.org/api/states/all?lamin={bounds}"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            if not data or 'states' not in data:
                return []
                
            processed_data = []
            for aircraft in data['states']:
                if all(aircraft[i] is not None for i in [1, 5, 6, 7]):  # Check required fields exist
                    processed_data.append({
                        'id': aircraft[1],  # Using callsign as ID
                        'lat': aircraft[6],
                        'lon': aircraft[5],
                        'altitude': aircraft[7],
                        'origin': self.guess_origin(aircraft[5], aircraft[6]),
                        'destination': self.guess_destination(aircraft[5], aircraft[6])
                    })
            return processed_data
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []

    def guess_origin(self, lon, lat) -> str:
        """
        Guess the origin airport based on position and direction
        This is a simplified version - you'd want to enhance this with real flight data
        """
        # Example airports - replace with actual nearby airports
        nearby_airports = [
            {'code': 'JFK', 'lat': 40.6413, 'lon': -73.7781},
            {'code': 'LGA', 'lat': 40.7769, 'lon': -73.8740},
            {'code': 'EWR', 'lat': 40.6895, 'lon': -74.1745},
            # Add more airports relevant to your location
        ]
        
        # Simple logic - return random airport for now
        # You could enhance this with actual flight path analysis
        return random.choice(nearby_airports)['code']

    def guess_destination(self, lon, lat) -> str:
        """Similar to guess_origin, but for destination"""
        # For now, returning random airport
        # Enhance this with real flight path analysis
        common_destinations = ['LAX', 'ORD', 'ATL', 'MIA', 'DFW']
        return random.choice(common_destinations)

game_state = GameState()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    game_state.connected_clients.add(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data['type'] == 'guess':
                player_name = data['player']
                plane_id = data['planeId']
                guessed_airport = data['airport']
                
                if plane_id in game_state.active_planes:
                    actual_destination = game_state.active_planes[plane_id]['destination']
                    if guessed_airport == actual_destination:
                        game_state.player_scores[player_name] = \
                            game_state.player_scores.get(player_name, 0) + 1
                        
            elif data['type'] == 'toggleGameMode':
                game_state.game_mode = not game_state.game_mode
                
            await game_state.broadcast_state()
            
    except WebSocketDisconnect:
        game_state.connected_clients.remove(websocket)

async def update_aircraft_loop():
    """Background task to update aircraft data"""
    while True:
        aircraft_data = game_state.fetch_aircraft_data()
        game_state.active_planes = {
            plane['id']: plane for plane in aircraft_data
        }
        await game_state.broadcast_state()
        await asyncio.sleep(5)  # Update every 5 seconds

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(update_aircraft_loop())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)