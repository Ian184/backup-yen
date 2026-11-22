# YEN — Assistente Pessoal Portátil (Linux & Windows 10/11)

Assistente inteligente portátil em Python + Tkinter feito para rodar direto de um pendrive ou em PCs modestos (4 GB RAM), com arquitetura híbrida (API Online + modelo local GGUF offline) e zelador automático de arquivos.

## O que você precisa para rodar
- **Python 3** instalado (no Linux já vem instalado; no Windows, baixe em [python.org](https://python.org) marcando *"Add Python to PATH"*).
- **Para modo Online:** uma chave gratuita do Google Gemini AI Studio colada em `1_Memoria/chave_api.txt` (o arquivo é criado automaticamente ao abrir pela primeira vez).
- **Para modo Offline (Opcional):** coloque qualquer modelo `.gguf` renomeado para `yen-completo.gguf` dentro de `cerebro/` e o executável `llama-server` dentro de `bin64/` (Linux) ou `bin_win/yen-server.exe` (Windows).

## Como Iniciar
- **Linux:** dê dois cliques em `ABRIR_YEN.desktop` ou rode `python3 yen.py`.
- **Windows 10 / 11:** dê dois cliques em `ABRIR_YEN.bat`.
- **Zelador em Tempo Real (Opcional):** execute `python3 yen_zelador.py` para organizar automaticamente `Downloads`, `Imagens`, `Vídeos`, `Documentos` e `Músicas` por artista em segundo plano.
