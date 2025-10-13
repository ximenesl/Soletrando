"""Módulo para processamento de áudio multicanal e cancelamento de ruído."""
import threading
import queue
import sys
import numpy as np
import sounddevice as sd
import speech_recognition as sr
from scipy.signal import correlate, stft, istft
from thefuzz import process

from services.conexao_nao import ReconhecimentoVozNAO
from services.reconhecimento_voz import MAPA_LETRAS_REVERSO, VOCABULARIO_LETRAS

class ProcessadorAudioMultiCanal:
    """Gerencia a captura de múltiplas fontes de áudio e aplica filtros."""
    def __init__(self, reconhecimento_nao: ReconhecimentoVozNAO, soletracao_inicial: str, callback_letra: callable, callback_final: callable, device_index: int | None = None):
        self.reconhecimento_nao = reconhecimento_nao
        self.device_index = device_index

        self.soletracao_atual = soletracao_inicial
        self.callback_letra = callback_letra
        self.callback_final = callback_final

        self.reconhecedor_sr = sr.Recognizer()

        self.taxa_amostragem = 16000
        self.canais_pc = 1
        self.dtype = 'int16'
        self.largura_amostra = 2

        self.fila_audio_pc = queue.Queue()
        self.fila_audio_nao = queue.Queue()

        self.rodando = False
        self.thread_processamento = None

        # --- Parâmetros de DSP ---
        self.atraso_calculado = 0
        self.sincronizado = False
        self.buffer_sinc_pc = np.array([], dtype=self.dtype)
        self.buffer_sinc_nao = np.array([], dtype=self.dtype)

        if self.reconhecimento_nao:
            self.reconhecimento_nao.processRemote = self._callback_nao

    def _callback_pc(self, indata, frames, time, status):
        if status:
            print(f"Status do stream do PC: {status}", file=sys.stderr)
        self.fila_audio_pc.put(indata.copy())

    def _callback_nao(self, nbOfChannels, nbrOfSamplesByChannel, timeStamp, inputBuffer):
        if not self.rodando:
            return
        audio_nao_raw = np.frombuffer(inputBuffer, dtype=self.dtype)
        audio_nao_deinterleaved = audio_nao_raw.reshape(-1, nbOfChannels).T
        self.fila_audio_nao.put(audio_nao_deinterleaved)

    def iniciar(self):
        print("Iniciando processador de áudio multicanal...")
        self.rodando = True

        self.stream_pc = sd.InputStream(
            samplerate=self.taxa_amostragem,
            device=self.device_index,
            channels=self.canais_pc,
            dtype=self.dtype,
            callback=self._callback_pc
        )
        self.stream_pc.start()

        if self.reconhecimento_nao:
            self.reconhecimento_nao.iniciar_escuta("")

        self.thread_processamento = threading.Thread(target=self._processar_filas, daemon=True)
        self.thread_processamento.start()
        print("Processador de áudio iniciado.")

    def parar(self):
        if not self.rodando:
            return
        print("Parando processador de áudio multicanal...")
        self.rodando = False

        if self.reconhecimento_nao:
            self.reconhecimento_nao.parar_escuta()
        
        if hasattr(self, 'stream_pc') and self.stream_pc:
            self.stream_pc.stop()
            self.stream_pc.close()

        if self.thread_processamento and self.thread_processamento.is_alive():
            self.thread_processamento.join(timeout=1)
        
        if self.callback_final:
            self.callback_final()
        print("Processador de áudio parado.")

    def _sincronizar_streams(self, sig, ref):
        """Calcula o atraso entre dois sinais usando correlação cruzada."""
        print("Calculando sincronização dos microfones...")
        # Normaliza os sinais para evitar problemas com amplitude
        sig = sig / np.max(np.abs(sig))
        ref = ref / np.max(np.abs(ref))
        correlation = correlate(sig, ref, mode='full')
        atraso = np.argmax(correlation) - (len(ref) - 1)
        print(f"Atraso calculado: {atraso} amostras.")
        self.atraso_calculado = atraso
        self.sincronizado = True

    def _subtracao_espectral(self, sinal_ruidoso, ref_ruido):
        """Aplica a subtração espectral para remover ruído."""
        # TODO: O tamanho da janela (nperseg) pode ser ajustado para melhores resultados.
        f_sinal, t_sinal, Zxx_sinal = stft(sinal_ruidoso, fs=self.taxa_amostragem, nperseg=256)
        f_ruido, t_ruido, Zxx_ruido = stft(ref_ruido, fs=self.taxa_amostragem, nperseg=256)

        mag_sinal = np.abs(Zxx_sinal)
        fase_sinal = np.angle(Zxx_sinal)
        mag_ruido = np.abs(Zxx_ruido)

        # TODO: Usar uma média do ruído ao longo do tempo em vez de uma estimativa instantânea.
        mag_ruido_medio = np.mean(mag_ruido, axis=1, keepdims=True)

        # A subtração em si
        mag_limpa = mag_sinal - mag_ruido_medio
        mag_limpa = np.maximum(mag_limpa, 0) # Garante que não há valores negativos

        # Reconstroi o sinal limpo
        Zxx_limpo = mag_limpa * np.exp(1j * fase_sinal)
        _, sinal_limpo = istft(Zxx_limpo, fs=self.taxa_amostragem)

        return sinal_limpo.astype(self.dtype)

    def _processar_filas(self):
        while self.rodando:
            try:
                dados_pc = self.fila_audio_pc.get(timeout=1).flatten()
                dados_nao = self.fila_audio_nao.get(timeout=1)
                ref_ruido_nao = dados_nao[0] # Usa o primeiro microfone do NAO como referência

                if not self.sincronizado:
                    # Acumula um buffer inicial para fazer a primeira sincronização
                    self.buffer_sinc_pc = np.append(self.buffer_sinc_pc, dados_pc)
                    self.buffer_sinc_nao = np.append(self.buffer_sinc_nao, ref_ruido_nao)
                    if len(self.buffer_sinc_pc) > self.taxa_amostragem: # Usa 1s de áudio
                        self._sincronizar_streams(self.buffer_sinc_pc, self.buffer_sinc_nao)
                    continue

                # Aplica o atraso para alinhar os sinais
                if self.atraso_calculado > 0: # PC atrasado em relação ao NAO
                    dados_pc_alinhado = dados_pc[self.atraso_calculado:]
                    ref_ruido_alinhado = ref_ruido_nao[:-self.atraso_calculado]
                else: # NAO atrasado em relação ao PC
                    dados_pc_alinhado = dados_pc[:self.atraso_calculado]
                    ref_ruido_alinhado = ref_ruido_nao[-self.atraso_calculado:]
                
                # Garante que os arrays tenham o mesmo tamanho após o alinhamento
                tamanho_min = min(len(dados_pc_alinhado), len(ref_ruido_alinhado))
                dados_pc_alinhado = dados_pc_alinhado[:tamanho_min]
                ref_ruido_alinhado = ref_ruido_alinhado[:tamanho_min]

                # Aplica o filtro
                audio_filtrado_np = self._subtracao_espectral(dados_pc_alinhado, ref_ruido_alinhado)

                audio_bytes = audio_filtrado_np.tobytes()
                if not audio_bytes:
                    continue

                audio_data = sr.AudioData(audio_bytes, self.taxa_amostragem, self.largura_amostra)

                texto = self.reconhecedor_sr.recognize_google(audio_data, language='pt-BR').lower()
                print(f"Texto filtrado: '{texto}'")

                melhor_correspondencia, pontuacao = process.extractOne(texto, VOCABULARIO_LETRAS)
                
                if pontuacao >= 75:
                    letra = MAPA_LETRAS_REVERSO[melhor_correspondencia]
                    self.soletracao_atual += letra
                    print(f"Letra (híbrido): '{letra}' -> Soletracao: '{self.soletracao_atual}'")
                    if self.callback_letra:
                        self.callback_letra(self.soletracao_atual)

            except queue.Empty:
                continue
            except (sr.UnknownValueError, sr.RequestError):
                continue
            except Exception as e:
                print(f"Erro no processamento das filas de áudio: {e}")
