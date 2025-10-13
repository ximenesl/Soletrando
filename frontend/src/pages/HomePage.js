import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import api from '../services/api';

const HomePageContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 20px;
`;

const Form = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  max-width: 400px;
`;

const Input = styled.input`
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 5px;
`;

const Select = styled.select`
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 5px;
`;

const Button = styled.button`
  padding: 12px;
  font-size: 1.1rem;
  background-color: #007bff;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;

  &:hover {
    background-color: #0056b3;
  }
`;

const HomePage = () => {
  const [ip, setIp] = useState('');
  const [level, setLevel] = useState('1_ano');
  const [micSource, setMicSource] = useState('pc');
  const navigate = useNavigate();

  const handleStartGame = async () => {
    try {
      await api.post('/nao/connect', null, { params: { ip } });
      await api.post('/game/level', null, { params: { level } });
      await api.post('/game/mic-source', null, { params: { source: micSource } });
      await api.post('/game/start');
      navigate('/game');
    } catch (error) {
      console.error('Failed to start game', error);
      alert('Falha ao iniciar o jogo. Verifique o IP do robô e se o backend está rodando.');
    }
  };

  return (
    <HomePageContainer>
      <Title>Soletrando com NAO</Title>
      <Form>
        <Input
          type="text"
          placeholder="Endereço IP do NAO"
          value={ip}
          onChange={(e) => setIp(e.target.value)}
        />
        <Select value={level} onChange={(e) => setLevel(e.target.value)}>
          <option value="1_ano">1º Ano</option>
          <option value="2_ano">2º Ano</option>
          <option value="3_ano">3º Ano</option>
          <option value="4_ano">4º Ano</option>
          <option value="5_ano">5º Ano</option>
          <option value="6_ano">6º Ano</option>
        </Select>
        <Select value={micSource} onChange={(e) => setMicSource(e.target.value)}>
          <option value="pc">Microfone do PC</option>
          <option value="nao">Microfone do NAO</option>
        </Select>
        <Button onClick={handleStartGame}>Iniciar Jogo</Button>
      </Form>
    </HomePageContainer>
  );
};

export default HomePage;
