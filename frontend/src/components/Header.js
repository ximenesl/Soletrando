import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';

const HeaderContainer = styled.header`
  background-color: #fff;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Logo = styled.div`
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
`;

const Nav = styled.nav`
  a {
    margin-left: 20px;
    text-decoration: none;
    color: #555;
    font-weight: 500;

    &:hover {
      color: #007bff;
    }
  }
`;

const Header = () => {
  return (
    <HeaderContainer>
      <Logo>Soletrando</Logo>
      <Nav>
        <Link to="/">Início</Link>
        <Link to="/game">Jogo</Link>
      </Nav>
    </HeaderContainer>
  );
};

export default Header;
