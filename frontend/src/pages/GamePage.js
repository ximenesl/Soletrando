import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import api from '../services/api';

const GamePageContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
`;

const WordContainer = styled.div`
  margin-bottom: 20px;
  font-size: 2rem;
  font-weight: bold;
`;

const SpellingContainer = styled.div`
  margin-bottom: 20px;
  font-size: 1.5rem;
  color: #555;
  min-height: 30px;
`;

const ControlsContainer = styled.div`
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
`;

const Button = styled.button`
  padding: 10px 20px;
  font-size: 1rem;
  background-color: #007bff;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;

  &:hover {
    background-color: #0056b3;
  }

  &:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
`;

const GamePage = () => {
  const [gameState, setGameState] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const ws = useRef(null);

  useEffect(() => {
    const fetchGameState = async () => {
      try {
        const response = await api.get('/game/state');
        setGameState(response.data);
      } catch (error) {
        console.error('Failed to fetch game state', error);
      }
    };

    fetchGameState();

    ws.current = new WebSocket('ws://localhost:8000/ws/game');

    ws.current.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setGameState(data);
    };

    ws.current.onclose = () => {
      console.log('WebSocket disconnected');
    };

    return () => {
      ws.current.close();
    };
  }, []);

  const handleSpell = async () => {
    setIsListening(true);
    try {
      await api.post('/game/spell');
    } catch (error) {
      console.error('Failed to start spelling', error);
      setIsListening(false);
    }
  };

  const handleStopSpelling = async () => {
    setIsListening(false);
    try {
      await api.post('/game/stop-spelling');
    } catch (error) {
      console.error('Failed to stop spelling', error);
    }
  };

  const handleCheck = async () => {
    try {
      await api.post('/game/check');
    } catch (error) {
      console.error('Failed to check spelling', error);
    }
  };

  const handleNextRound = async () => {
    try {
      await api.post('/game/next-round');
    } catch (error) {
      console.error('Failed to start next round', error);
    }
  };

  const handleBackspace = async () => {
    try {
      await api.post('/game/backspace');
    } catch (error) {
      console.error('Failed to backspace', error);
    }
  };

  if (!gameState) {
    return <div>Carregando...</div>;
  }

  return (
    <GamePageContainer>
      <WordContainer>{gameState.palavra_atual?.palavra || '...'}</WordContainer>
      <SpellingContainer>{gameState.soletracao_usuario || ''}</SpellingContainer>
      <ControlsContainer>
        <Button onClick={handleSpell} disabled={isListening}>
          Soletrar
        </Button>
        <Button onClick={handleStopSpelling} disabled={!isListening}>
          Parar de Ouvir
        </Button>
        <Button onClick={handleCheck}>Verificar</Button>
        <Button onClick={handleBackspace}>Apagar</Button>
        <Button onClick={handleNextRound}>Próxima Palavra</Button>
      </ControlsContainer>
    </GamePageContainer>
  );
};

export default GamePage;
