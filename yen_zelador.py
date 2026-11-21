#!/usr/bin/env python3
import os, time, shutil, re

BASE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
ORIGENS = [os.path.join(HOME, p) for p in ["Downloads", "Área de trabalho", "Desktop", "Imagens", "Vídeos", "Documentos", "Músicas"]] + [os.path.join(BASE, "2_Arquivo_de_Despejo")]
MAPA = {
    os.path.join(HOME, "Imagens", "JPG"): {".jpg", ".jpeg"},
    os.path.join(HOME, "Imagens", "PNG"): {".png", ".webp", ".svg"},
    os.path.join(HOME, "Imagens", "GIF"): {".gif"},
    os.path.join(HOME, "Vídeos", "MP4"): {".mp4", ".mov"},
    os.path.join(HOME, "Vídeos", "Outros_Videos"): {".mkv", ".webm", ".avi"},
    os.path.join(HOME, "Documentos", "PDF"): {".pdf"},
    os.path.join(HOME, "Documentos", "Textos_e_Planilhas"): {".docx", ".doc", ".xlsx", ".csv", ".ods", ".pptx", ".txt", ".md", ".epub"},
}

def mover_seguro(src, dest_dir):
    if os.path.dirname(src) == dest_dir: return
    os.makedirs(dest_dir, exist_ok=True)
    nome = os.path.basename(src)
    dst = os.path.join(dest_dir, nome)
    if os.path.exists(dst):
        b, e = os.path.splitext(nome)
        dst = os.path.join(dest_dir, f"{b}_{int(time.time())}{e}")
    shutil.move(src, dst)

def varrer():
    for pasta in ORIGENS:
        if not os.path.exists(pasta): continue
        for f in os.listdir(pasta):
            fp = os.path.join(pasta, f)
            if not os.path.isfile(fp) or f.startswith("."): continue
            ext = os.path.splitext(f)[1].lower()
            if ext in {".part", ".crdownload", ".tmp"} or time.time() - os.path.getmtime(fp) < 3: continue
            if ext in {".mp3", ".flac", ".ogg", ".wav", ".m4a"}:
                limpo = f.replace("_", " ")
                art = limpo.split(" - ")[0].strip() if " - " in limpo else "Outros"
                art = re.sub(r'[\\/*?:"<>|]', "", art)[:35] or "Outros"
                mover_seguro(fp, os.path.join(HOME, "Músicas", art))
                continue
            for dest, exts in MAPA.items():
                if ext in exts:
                    mover_seguro(fp, dest); break

while True:
    try: varrer()
    except Exception: pass
    time.sleep(5)
