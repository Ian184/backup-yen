# YEN — Assistente Pessoal Portátil para Linux

Assistente inteligente portátil escrito em Python + Tkinter, projetado para rodar direto de um pendrive ou em hardware modesto (4 GB RAM / Linux XFCE) com arquitetura híbrida (API Online + modelo local GGUF offline).

## Recursos Principais
- **Modo Bolso & Modo Completo:** janela flutuante compacta no canto da tela ou painel completo com execução de comandos Linux e barra de progresso.
- **Zelador Autônomo:** diagnóstico instantâneo de RAM/CPU/disco e organização automática de arquivos (`.jpg`, `.png`, `.mp3`, `.mp4`, `.pdf`) e bibliotecas de música por artista.
- **Memória Persistente & Habilidades (`3_Habilidades/`):** mantém contexto entre sessões e permite criar scripts modulares sob demanda.
- **Motor Híbrido:** alterna automaticamente para inferência local via `llama.cpp` (`yen-server` + `.gguf`) quando não há conexão com a internet.

## Como Usar
1. Adicione sua chave de API em `1_Memoria/chave_api.txt` (opcional se usar apenas o modelo local `.gguf` em `cerebro/`).
2. Execute `python3 yen.py` ou dê dois cliques em `ABRIR_YEN.desktop`.
