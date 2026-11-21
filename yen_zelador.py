#!/usr/bin/env python3
import os, time, shutil, re

BASE = os.path.dirname(os.path.abspath(__file__))
DESPEJO = os.path.join(BASE, "2_Arquivo_de_Despejo")
HOME = os.path.expanduser("~")
MAPA = {
    os.path.join(HOME, "Imagens"): {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"},
    os.path.join(HOME, "Vídeos"): {".mp4", ".mkv", ".webm", ".avi", ".mov"},
    os.path.join(HOME, "Documentos"): {".pdf", ".docx", ".doc", ".xlsx", ".pptx", ".txt", ".md", ".epub"},
    os.path.join(HOME, "Downloads", "Jogos_e_Apps"): {".zip", ".rar", ".7z", ".tar", ".gz", ".deb", ".appimage", ".exe", ".iso", ".sh"}
}

def mover_seguro(src, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    nome = os.path.basename(src)
    dst = os.path.join(dest_dir, nome)
    if os.path.exists(dst):
        b, e = os.path.splitext(nome)
        dst = os.path.join(dest_dir, f"{b}_{int(time.time())}{e}")
    shutil.move(src, dst)

def varrer():
    for pasta in [os.path.join(HOME, "Downloads"), DESPEJO, os.path.join(HOME, "Músicas")]:
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
