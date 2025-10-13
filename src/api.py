
"""Arquivo principal da API do Soletrando."""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from game.gerenciador_jogo import GerenciadorJogo

app = FastAPI(
    title="Soletrando com NAO - API",
    description="API para gerenciar o jogo Soletrando, com integração ao robô NAO.",
    version="1.0.0"
)

# --- Configuração do CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restrinja para o domínio do front-end
    allow_credentials=True,
    allow_methods=["*"]
,
    allow_headers=["*"]
,
)

# --- Singleton do Gerenciador do Jogo ---
game_manager = GerenciadorJogo()

# --- WebSocket para atualizações em tempo real ---
@app.websocket("/ws/game")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Apenas para manter a conexão viva, o back-end envia o estado
            await websocket.receive_text()
    except WebSocketDisconnect:
        print("Cliente WebSocket desconectado")

async def broadcast_state():
    # Esta função será chamada para enviar o estado atual para todos os clientes
    # (Implementação de broadcast necessária)
    pass

# Sobrescrever o método de atualização do gerenciador para usar o broadcast
game_manager._atualizar_soletracao = lambda soletracao: (
    setattr(game_manager, 'soletracao_usuario', soletracao),
    # asyncio.create_task(broadcast_state()) # Descomente quando o broadcast for implementado
)

# --- Endpoints da API ---

@app.post("/game/start", tags=["Game"])
async def start_game():
    return game_manager.iniciar_jogo()

@app.post("/game/next-round", tags=["Game"])
async def next_round():
    return game_manager.iniciar_nova_rodada()

@app.post("/game/spell", tags=["Game"])
async def spell(device: str | int | None = None):
    return game_manager.iniciar_soletracao(device)

@app.post("/game/stop-spelling", tags=["Game"])
async def stop_spelling():
    return game_manager.parar_escuta_voz()

@app.post("/game/check", tags=["Game"])
async def check_spelling():
    return game_manager.verificar_soletracao()

@app.post("/game/backspace", tags=["Game"])
async def backspace():
    return game_manager.apagar_ultima_letra()

@app.post("/game/level", tags=["Game"])
async def set_level(level: str):
    return game_manager.definir_nivel(level)

@app.post("/game/mic-source", tags=["Game"])
async def set_mic_source(source: str):
    return game_manager.definir_fonte_microfone(source)

@app.get("/game/state", tags=["Game"])
async def get_state():
    return game_manager.obter_estado()

# --- Endpoints do NAO ---

@app.post("/nao/connect", tags=["NAO"])
async def connect_nao(ip: str):
    return game_manager.conectar_nao(ip)

@app.post("/nao/disconnect", tags=["NAO"])
async def disconnect_nao():
    return game_manager.desconectar_nao()

# --- Para executar a API localmente ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
