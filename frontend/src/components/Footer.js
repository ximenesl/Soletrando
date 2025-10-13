import React from 'react';
import styled from 'styled-components';

const FooterContainer = styled.footer`
  background-color: #333;
  color: #fff;
  padding: 20px;
  text-align: center;
  font-size: 0.9rem;
`;

const Footer = () => {
  return (
    <FooterContainer>
      <p>&copy; 2025 Soletrando. Todos os direitos reservados.</p>
    </FooterContainer>
  );
};

export default Footer;
