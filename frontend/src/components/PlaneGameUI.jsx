import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Plane, Trophy, Power } from 'lucide-react';

const PlaneGameUI = () => {
  const [ws, setWs] = useState(null);
  const [gameState, setGameState] = useState({
    activePlanes: {},
    scores: {},
    gameMode: false
  });
  const [playerName, setPlayerName] = useState('');
  const [selectedPlane, setSelectedPlane] = useState(null);
  const [guess, setGuess] = useState('');
  
  useEffect(() => {
    const websocket = new WebSocket('ws://localhost:8000/ws');
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setGameState(data);
    };
    
    websocket.onopen = () => {
      setWs(websocket);
    };
    
    return () => {
      websocket.close();
    };
  }, []);
  
  const submitGuess = () => {
    if (ws && selectedPlane && guess && playerName) {
      ws.send(JSON.stringify({
        type: 'guess',
        player: playerName,
        planeId: selectedPlane,
        airport: guess.toUpperCase()
      }));
      setGuess('');
      setSelectedPlane(null);
    }
  };
  
  const toggleGameMode = () => {
    if (ws) {
      ws.send(JSON.stringify({
        type: 'toggleGameMode'
      }));
    }
  };
  
  return (
    <div className="p-4 max-w-4xl mx-auto">
      <Card className="mb-4">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Plane className="h-6 w-6" />
            Plane Guessing Game
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 mb-4">
            <Input
              placeholder="Enter your name"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
              className="max-w-xs"
            />
            <Button
              onClick={toggleGameMode}
              variant={gameState.gameMode ? "destructive" : "default"}
              className="flex items-center gap-2"
            >
              <Power className="h-4 w-4" />
              {gameState.gameMode ? 'End Game' : 'Start Game'}
            </Button>
          </div>
          
          {gameState.gameMode && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Active Planes</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {Object.entries(gameState.activePlanes).map(([id, plane]) => (
                        <div
                          key={id}
                          className={`p-2 border rounded cursor-pointer ${
                            selectedPlane === id ? 'bg-blue-100' : ''
                          }`}
                          onClick={() => setSelectedPlane(id)}
                        >
                          Flight {id} at {Math.round(plane.altitude)}ft
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <Trophy className="h-5 w-5" />
                      Leaderboard
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {Object.entries(gameState.scores)
                        .sort(([,a], [,b]) => b - a)
                        .map(([name, score]) => (
                          <div key={name} className="flex justify-between">
                            <span>{name}</span>
                            <span className="font-bold">{score}</span>
                          </div>
                        ))
                      }
                    </div>
                  </CardContent>
                </Card>
              </div>
              
              {selectedPlane && (
                <div className="flex gap-2">
                  <Input
                    placeholder="Guess destination airport (e.g., JFK)"
                    value={guess}
                    onChange={(e) => setGuess(e.target.value)}
                    className="max-w-xs"
                  />
                  <Button onClick={submitGuess}>Submit Guess</Button>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default PlaneGameUI;