# Soletrando com o Robô NAO

Este é um jogo interativo de soletração desenvolvido em Python, onde o jogador interage com o robô NAO para soletrar palavras. O jogo possui uma interface gráfica moderna e diversas funcionalidades para auxiliar no aprendizado e na diversão.

## ✨ Funcionalidades

- **Interface Gráfica Moderna:** Desenvolvido com CustomTkinter para um visual agradável.
- **Múltiplos Níveis de Dificuldade:** Contém listas de palavras que vão do 1º ao 6º ano do ensino fundamental, aumentando a complexidade gradualmente.
- **Dicas com Emojis:** Para cada palavra, um emoji correspondente é exibido como uma dica visual.
- **Dupla Opção de Microfone:** O jogador pode escolher usar o microfone do próprio robô NAO ou o microfone do computador para o reconhecimento de voz.
- **Controles por Toque:** Interaja diretamente com o robô:
  - Toque no sensor da **mão esquerda** para apagar a soletração atual.
  - Toque no sensor da **mão direita** para confirmar a palavra soletrada.
- **Gerenciamento de Palavras:** As palavras de um nível não se repetem até que toda a lista seja percorrida.

## 🚀 Como Rodar o Projeto

Siga os passos abaixo para configurar e rodar o projeto:

**1. Clone o Repositório (se ainda não o fez)**

```bash
# Se estiver usando Git
git clone <URL_DO_REPOSITORIO>
# Ou simplesmente baixe e extraia o arquivo ZIP do projeto.
```

**2. Crie e Ative um Ambiente Virtual (Recomendado)**

Isso isola as dependências do seu projeto e evita conflitos.

```bash
# No Windows
python -m venv venv
venv\Scripts\activate

# No macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Instale as Dependências**

Com o ambiente virtual ativado, execute o comando abaixo na raiz do projeto para instalar todas as bibliotecas necessárias.

```bash
pip install -r requirements.txt
```

**4. Execute o Jogo**

Agora, basta rodar o arquivo `main.py` que está na pasta `src`.

```bash
python src/main.py
```

**5. Como Jogar**

- Ao iniciar, a primeira tela pedirá o **endereço de IP** do seu robô NAO.
- Após a conexão, você irá para a tela de início, onde poderá escolher o **nível de dificuldade** (1º ao 6º ano) e a **fonte do microfone** (NAO ou PC).
- Clique em "Iniciar Jogo" e divirta-se!

## ⚙️ Pré-requisitos

- Python 3.8 ou superior
- Acesso a um robô NAO na mesma rede que o computador
- Um microfone (caso queira usar a opção "PC")

## 📂 Estrutura do Projeto

```
Soletrando/
├── src/                  # Contém todo o código fonte da aplicação
│   ├── main.py           # Arquivo principal que executa a aplicação
│   ├── app/              # Módulos da interface gráfica e controle do jogo
│   ├── config/           # Configurações, como caminhos de arquivos
│   ├── data/             # Arquivos de dados, como o mapa de emojis
│   ├── game/             # Lógica principal do jogo
│   ├── services/         # Módulos de serviços (NAO, reconhecimento de voz)
│   └── ...
├── word_lists/           # Contém os arquivos .txt com as palavras para cada nível
├── assets/               # Contém os recursos de imagem, como o logo
├── requirements.txt      # Lista de dependências do projeto
└── README.md             # Este arquivo
```

## 👥 Integrantes

- **Lucas Ximenes:** [https://github.com/ximenesl](https://github.com/ximenesl)
- **Moisés Carlos:** [https://github.com/moises-carlos](https://github.com/moises-carlos)
- **Vanda Vitorio:** [https://github.com/vandinha01](https://github.com/vandinha01)
- **Ygor Sampaio:** (GitHub não informado)

## 💡 Motivação e Contexto do Projeto

*Este documento foi baseado no documento de ideação do grupo "Quarteto Fantástico" para a linha de projeto NAOv6.*

### Problemática Observada

A alfabetização ainda representa um desafio significativo para muitas crianças, especialmente no que se refere à prática da soletração e ao reconhecimento de palavras de forma lúdica e interativa. Dificuldades nesse estágio inicial podem impactar negativamente toda a trajetória escolar, refletindo no desempenho dos estudantes nas etapas posteriores do ensino.

Segundo o Instituto pela Educação, 33% dos alunos do ensino médio não alcançaram o nível básico de proficiência em Língua Portuguesa, o que evidencia falhas estruturais no ensino básico brasileiro e reforça a necessidade de soluções pedagógicas eficazes desde os primeiros anos escolares.

Diante desse cenário, torna-se essencial desenvolver estratégias que tornem o aprendizado mais atrativo, interativo e eficaz, prevenindo lacunas futuras e promovendo o domínio da leitura e da escrita desde os primeiros anos da educação.

### Ideia de Solução

O projeto propõe a utilização do robô NAOv6 como ferramenta de apoio no processo de alfabetização, aproveitando seu potencial interativo para criar um ambiente de aprendizagem mais dinâmico e envolvente. O robô será programado para pronunciar palavras em voz alta, incentivando a criança a soletrá-las corretamente. Após a tentativa, o robô fornecerá um retorno imediato, informando se a resposta está correta e encorajando a continuidade da prática de forma positiva, fortalecendo a autoconfiança e o interesse pelo aprendizado.

A escolha pelo uso do NAOv6 se baseia na necessidade de inovar as práticas pedagógicas, incorporando metodologias ativas que estimulem a curiosidade dos alunos. A atividade principal será um jogo de soletração, que une ludicidade e aprendizado. Essa dinâmica transforma uma prática tradicionalmente repetitiva em uma experiência divertida e interativa, contribuindo para o desenvolvimento da ortografia, da memória auditiva, da atenção, da disciplina e da capacidade de autocorreção.

### Impacto e Diferencial

O projeto tem potencial para transformar o processo de alfabetização em algo mais interativo e engajador. O grande diferencial está no uso de um robô humanoide como mediador do ensino, capaz de oferecer retorno imediato e estimular a participação dos alunos de forma lúdica.

A presença do robô contribui para reduzir a timidez e o medo de errar. Muitas crianças se sentem constrangidas em errar na frente da turma. O NAOv6 cria um ambiente seguro e sem julgamentos, onde o erro é tratado como parte natural do aprendizado. Isso promove mais confiança e coragem para enfrentar novos desafios linguísticos.
