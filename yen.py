#!/usr/bin/env python3
import os, sys, subprocess, re, glob, shutil, threading, datetime, time, json, urllib.request, urllib.parse, base64, py_compile
import tkinter as tk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORIA_DIR = os.path.join(BASE_DIR, "1_Memoria")
DESPEJO_DIR = os.path.join(BASE_DIR, "2_Arquivo_de_Despejo")
CHAVE_FILE = os.path.join(MEMORIA_DIR, "chave_api.txt")
SELF_FILE = os.path.abspath(__file__)
PENDENTE = {"link": None, "tema": None}

HAB_DIR = os.path.join(BASE_DIR, "3_Habilidades")
os.makedirs(HAB_DIR, exist_ok=True)

def listar_habilidades():
    arqs = [os.path.basename(f)[:-3] for f in glob.glob(os.path.join(HAB_DIR, "*.py"))]
    return ", ".join(arqs) if arqs else "nenhuma"

def ler_chave():
    if os.path.exists(CHAVE_FILE):
        with open(CHAVE_FILE, "r", encoding="utf-8") as f:
            k = f.read().strip()
            if k and "COLE_SUA_CHAVE" not in k: return k
    return ""

PROIBIDOS = ["rm -rf /", "rm -rf /*", "rm -rf ~", "mkfs", "dd if=", "wipefs", "fdisk", "parted", "chmod -R 777 /", "> /dev/sd", "shutdown", "reboot", "poweroff"]

def comando_seguro(cmd):
    c = " ".join(cmd.lower().split())
    for p in PROIBIDOS:
        if p in c: return False, p
    if re.search(r"\brm\s+-[a-z]*r[a-z]*f?\s+(/|/home|/etc|/usr|/var|/boot|\*|~/?$)", c):
        return False, "remoção crítica"
    return True, ""

def raio_x_pc():
    t, d = [int(x) for x in open("/proc/meminfo").read().split() if x.isdigit()][:2]
    _, _, l = shutil.disk_usage(BASE_DIR)
    return f"RAM: {int((t-d)/1024)}/{int(t/1024)}MB | Pendrive: {round(l/(1024**3),1)}GB livres"

def organizar_pasta(alvo):
    m = {"Imagens_JPG": {".jpg",".jpeg"}, "Imagens_PNG": {".png",".webp"}, "Musicas_MP3": {".mp3",".wav"}, "Videos_MP4": {".mp4",".mkv"}}
    c = 0
    for f in os.listdir(alvo):
        fp = os.path.join(alvo, f)
        if not os.path.isfile(fp): continue
        for pasta, exts in m.items():
            if os.path.splitext(f)[1].lower() in exts:
                os.makedirs(os.path.join(alvo, pasta), exist_ok=True)
                shutil.move(fp, os.path.join(alvo, pasta, f)); c += 1; break
    return f"Organizei {c} arquivo(s) em pastas!" if c else "Tudo organizado por aqui."

def organizar_musicas():
    base = os.path.expanduser("~/Músicas")
    c = 0
    for f in os.listdir(base):
        fp = os.path.join(base, f)
        if not os.path.isfile(fp) or not f.lower().endswith(".mp3"): continue
        limpo = f.replace("_", " ")
        artista = limpo.split(" - ")[0].strip() if " - " in limpo else "Outros"
        artista = re.sub(r'[\\/*?:"<>|]', "", artista)[:35] or "Outros"
        os.makedirs(os.path.join(base, artista), exist_ok=True)
        shutil.move(fp, os.path.join(base, artista, f)); c += 1
    return f"Separei {c} músicas por artista em ~/Músicas!" if c else "Músicas já estão separadas por artista."

def espiar_pastas():
    res = []
    for nome, d in [("Despejo", DESPEJO_DIR), ("Downloads", os.path.expanduser("~/Downloads")), ("Musicas", os.path.expanduser("~/Músicas"))]:
        if os.path.exists(d):
            arqs = os.listdir(d)[:12]
            res.append(f"{nome}({len(os.listdir(d))} itens): {', '.join(arqs)}")
    return " | ".join(res)

def apps_abertos():
    apps = ["firefox", "chrome", "chromium", "brave", "falkon", "discord", "audacious", "thunar", "zzzfm", "pcsx2"]
    try:
        ps = subprocess.check_output(["ps", "-e", "-o", "comm="], text=True).lower()
        return sorted(set(a for a in apps if a in ps))
    except Exception: return []

def extrair_url_real(link):
    if "imgurl=" in link:
        m = re.search(r"imgurl=([^&]+)", link)
        if m: return urllib.parse.unquote(m.group(1))
    if "url=" in link and "google." in link:
        m = re.search(r"[?&]url=([^&]+)", link)
        if m: return urllib.parse.unquote(m.group(1))
    return link

def baixar_imagem_busca(tema, ext="jpg"):
    try:
        q = urllib.parse.quote(tema)
        for lang in ["pt", "en"]:
            host = f"{lang}.wikipedia.org"
            api_s = "https" + chr(58) + "//" + host + "/w/api.php?action=opensearch&search=" + q + "&limit=3&format=json"
            req_s = urllib.request.Request(api_s, headers={"User-Agent": "YenAssistant/1.0"})
            res_s = json.loads(urllib.request.urlopen(req_s, timeout=10).read().decode("utf-8"))
            it = iter(res_s); next(it, None); titulos = next(it, [])
            for titulo in titulos:
                t_enc = urllib.parse.quote(titulo)
                api_i = "https" + chr(58) + "//" + host + "/w/api.php?action=query&titles=" + t_enc + "&prop=pageimages&piprop=thumbnail&pithumbsize=1000&format=json"
                req_i = urllib.request.Request(api_i, headers={"User-Agent": "YenAssistant/1.0"})
                dados = json.loads(urllib.request.urlopen(req_i, timeout=10).read().decode("utf-8"))
                for p in dados.get("query", {}).get("pages", {}).values():
                    img_url = p.get("thumbnail", {}).get("source", "")
                    if img_url:
                        nome = re.sub(r"[^a-zA-Z0-9_-]", "_", titulo.lower())[:25]
                        dest = os.path.join(DESPEJO_DIR, f"{nome}_{int(time.time())}.{ext}")
                        subprocess.run(["curl", "-4", "-L", "-s", "--max-time", "15", "-A", "Mozilla/5.0", img_url, "-o", dest], check=False)
                        if os.path.exists(dest) and os.path.getsize(dest) > 4000:
                            tipo = subprocess.check_output(["file", "-b", "--mime-type", dest], text=True).strip()
                            if tipo.startswith("image/"):
                                return f"Foto de '{titulo}' salva em 2_Arquivo_de_Despejo/{os.path.basename(dest)}!"
                            os.remove(dest)
        return f"Não achei foto para '{tema}', tenta escrever só o nome principal."
    except Exception as e:
        return f"Erro ao buscar foto: {e}"

def evoluir_codigo_ia(pedido):
    api_key = ler_chave()
    if not api_key: return "Sem chave de API para auto-evolução."
    try:
        with open(SELF_FILE, "r", encoding="utf-8") as f: codigo_atual = f.read()
        prompt = (
            f"Você é o próprio código Python do assistente Yen. Aplique esta melhoria solicitada pelo Ian:\n"
            f"MELHORIA: {pedido}\n\n"
            f"Regras: mantenha todas as funções existentes, a interface Tkinter e as travas de segurança intactas. "
            f"Devolva o arquivo yen.py COMPLETO dentro de ```python ... ```.\n\nCÓDIGO ATUAL:\n{codigo_atual}"
        )
        payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.2, "maxOutputTokens": 8192}}
        host = "generativelanguage" + "." + "googleapis" + ".com"
        url = "https" + chr(58) + "//" + host + "/v1beta/models/gemini-flash-lite-latest" + chr(58) + "generateContent?key=" + api_key
        out = subprocess.check_output(["curl", "-4", "-s", "-X", "POST", url, "-H", "Content-Type: application/json", "-d", json.dumps(payload)], text=True, timeout=60)
        res = json.loads(out)
        cand = next(iter(res["candidates"]))
        part = next(iter(cand["content"]["parts"]))
        blocos = re.findall(r"```python\n(.*?)\n```", part["text"], re.DOTALL)
        if not blocos: return "Não consegui gerar o código atualizado."
        novo_cod = next(iter(blocos)).strip()
        tmp_py = SELF_FILE + ".tmp"
        with open(tmp_py, "w", encoding="utf-8") as f: f.write(novo_cod)
        py_compile.compile(tmp_py, doraise=True)
        shutil.copy2(SELF_FILE, SELF_FILE + ".bak")
        os.replace(tmp_py, SELF_FILE)
        return "Auto-evolução aplicada com sucesso! (Backup salvo em yen.py.bak). Feche e abra o Yen para ativar."
    except Exception as e:
        if os.path.exists(SELF_FILE + ".tmp"): os.remove(SELF_FILE + ".tmp")
        return f"Auto-evolução abortada (código original preservado): {e}"

def reflexo_rapido(msg):
    raw = msg.strip(); m = raw.lower(); ab = apps_abertos()
    navs = [n for n in ["firefox", "chrome", "chromium", "brave", "falkon"] if n in ab]
    if raw == "Yen me ajuda" or m == "yen me ajuda":
        return (
            "=== COMANDOS DO YEN ===\n"
            "• yen status                               -> Raio-X de RAM e pendrive\n"
            "• yen organiza [downloads | musicas]      -> Separa arquivos e artistas\n"
            "• yen baixa <link, musica, base64 ou foto> -> Baixa mp3, mp4, pdf, jpg ou png\n"
            "• yen cria <nome> / yen apaga <nome>      -> Gerencia 2_Arquivo_de_Despejo\n"
            "• yen evolui <melhoria>                   -> Reprograma o próprio yen.py com backup\n"
            "• yen abre youtube / discord / audacious / despejo\n"
            "• yen conecta note / yen fone note\n"
            "• salve na memoria: <texto>\n\n"
            "=== COMANDOS LINUX (MINT / ANTIX) ===\n"
            "• df -h (espaço disco) | free -h (RAM) | lsblk (discos) | inxi -Fz (PC)\n"
            "• sudo apt update && sudo apt upgrade -y (atualizar sistema)\n"
            "• pkill -f nome_app (fechar app travado)"
        )
    if m.startswith("yen aprende "):
        pedido = raw[12:].strip()
        nome = re.sub(r"[^a-z0-9_]", "_", pedido.lower())[:25].strip("_") or "skill"
        arq = os.path.join(HAB_DIR, f"{nome}.py")
        return f"Criando habilidade '{nome}'...\n```bash\ncat << 'EOF' > {arq}\n# Habilidade: {pedido}\nimport os, sys\nprint('Habilidade {nome} pronta!')\nEOF\n```"
    if m.startswith("yen evolui "):
        pedido = raw[11:].strip()
        if pedido: return evoluir_codigo_ia(pedido)
    if (PENDENTE["link"] or PENDENTE["tema"]) and m in ["mp3", "mp4", "pdf", "jpg", "png"]:
        link, tema = PENDENTE["link"], PENDENTE["tema"]
        PENDENTE["link"], PENDENTE["tema"] = None, None
        if tema: return baixar_imagem_busca(tema, m)
        link = extrair_url_real(link)
        if m == "mp3":
            dest = next((os.path.expanduser(p) for p in ["~/Músicas", "~/Música", "~/Music"] if os.path.exists(os.path.expanduser(p))), os.path.expanduser("~/Músicas")); os.makedirs(dest, exist_ok=True)
            alvo_yt = link if link.startswith("http") else f"ytsearch1:{link}"
            return f"Baixando e convertendo MP3 para ~/Música...\n```bash\n/usr/local/bin/yt-dlp -4 --js-runtimes node --no-playlist -f bestaudio -x --audio-format mp3 --audio-quality 0 -o \"{dest}/%(title)s.%(ext)s\" \"{alvo_yt}\"\n```"
        elif m == "mp4":
            return f"Baixando vídeo MP4 para 2_Arquivo_de_Despejo...\n```bash\nyt-dlp --no-playlist -f \"bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]\" -o \"{DESPEJO_DIR}/%(title)s.%(ext)s\" \"{link}\"\n```"
        nome_arq = f"arquivo_{int(time.time())}.{m}"
        subprocess.Popen(f'curl -4 -L -s -A "Mozilla/5.0" "{link}" -o "{DESPEJO_DIR}/{nome_arq}"', shell=True)
        return f"Baixando {m.upper()} como {nome_arq}!"
    if ("baixa" in m or "baixar" in m) and any(w in m for w in ["musica", "música", "mp3", "foto", "imagem", "http://", "https://", "data:image/", "yen baixa", "yem baixa"]):
        resto = re.sub(r"^.*?(ye[nm]\s*(me)?\s*baixa:?|baixar? uma foto|baixar? foto|baixar? uma imagem)\s*", "", raw, flags=re.I).strip()
        if resto.startswith("data:image/"):
            try:
                cab, b64 = resto.split(",", 1)
                ext_orig = "webp" if "webp" in cab else ("png" if "png" in cab else "jpg")
                tmp = os.path.join(DESPEJO_DIR, f"tmp_{int(time.time())}.{ext_orig}")
                dest = os.path.join(DESPEJO_DIR, f"imagem_{int(time.time())}.jpg")
                with open(tmp, "wb") as f: f.write(base64.b64decode(b64))
                if ext_orig == "webp" and shutil.which("dwebp"):
                    subprocess.run(["dwebp", tmp, "-o", dest], check=False); os.remove(tmp)
                else: os.rename(tmp, dest)
                return f"Imagem salva em 2_Arquivo_de_Despejo/{os.path.basename(dest)}!"
            except Exception as e: return f"Erro ao salvar imagem: {e}"
        if "http://" in resto or "https://" in resto:
            partes = resto.split()
            it_p = iter(partes); p1 = next(it_p, ""); p2 = next(it_p, "")
            if p2 and p1.lower() in ["mp3", "mp4", "pdf", "jpg", "png"]:
                PENDENTE["link"] = p2; return reflexo_rapido(p1.lower())
            PENDENTE["link"] = p1; return "Quer que eu baixe mp4, mp3, pdf, jpg ou png?"
        if any(w in m for w in ["musica", "música", "mp3"]):
            nome_mus = re.sub(r"\b(musica|música|mp3|uma|um|a|o|de|do|da)\b|[?!.,]", " ", resto, flags=re.I)
            PENDENTE["link"] = " ".join(nome_mus.split()) or resto
            return reflexo_rapido("mp3")
        ext = "png" if "png" in m else "jpg"
        tema = re.sub(r"\b(yen|yem|voce|você|vocẽ|pode|me|baixa|baixar|uma|um|a|o|foto|imagem|serie|série|filme|jogo|chamada|chamado|em jpg|em png|jpg|png|de|do|da|dos|das|ex-presidente|presidente)\b|[?!.,]", " ", resto, flags=re.I)
        tema = " ".join(tema.split())
        return baixar_imagem_busca(tema or resto, ext)
    if "musica" in m and "organiza" in m: return organizar_musicas()
    if m.startswith("yen organiza"): return organizar_pasta(os.path.expanduser("~/Downloads") if "download" in m else DESPEJO_DIR)
    if "limpa ram" in m or "limpar ram" in m:
        antes = raio_x_pc()
        os.system("sync && echo 1 | sudo tee /proc/sys/vm/drop_caches >/dev/null")
        return f"Cache limpo! Antes: {antes} | Agora: {raio_x_pc()}"
    if m in ["yen status", "status pc", "raio x"]: return raio_x_pc()
    if m.startswith("yen cria "):
        nome = raw[9:].strip().replace("..", "")
        if nome: os.makedirs(os.path.join(DESPEJO_DIR, nome), exist_ok=True); return f"Pasta criada: {nome}"
    if m.startswith("yen apaga "):
        nome = raw[10:].strip().replace("..", "").lstrip("/")
        alvo = os.path.join(DESPEJO_DIR, nome)
        if nome and os.path.exists(alvo):
            shutil.rmtree(alvo) if os.path.isdir(alvo) else os.remove(alvo); return f"Apagado: {nome}"
        return f"Não achei '{nome}' na pasta de despejo."
    for g in ["salve na memoria:", "salva na memoria:", "salve na memória:", "salva na memória:", "lembra que "]:
        if m.startswith(g):
            dado = msg[len(g):].strip()
            if dado:
                with open(os.path.join(MEMORIA_DIR, "memorias_salvas.txt"), "a", encoding="utf-8") as f: f.write(f"- {dado}\n")
                return f"Salvo na memória: {dado}"
    if m in ["oi", "ola", "olá", "eae", "e aí", "eai", "opa", "bom dia", "boa tarde", "boa noite", "yen"]: return "E aí, Ian. Tô pronto, manda."
    if any(p in m for p in ["que horas", "que dia", "data de hoje", "horário"]): return datetime.datetime.now().strftime("%d/%m/%Y - %H:%M")
    if any(k in m for k in ["que musica", "que música", "minhas musicas", "minhas músicas", "listar mp3", "quais mp3"]):
        return "Listando seus arquivos MP3 no PC...\n```bash\nfind ~ -iname \"*.mp3\" 2>/dev/null\n```"
    if "espaço" in m or "quanto tem livre" in m:
        _, _, livre = shutil.disk_usage(BASE_DIR); return f"{round(livre / (1024**3), 1)} GB livres no pendrive."
    if "youtube" in m and any(v in m for v in ["abre", "abrir", "abra", "entra", "bota", "coloca"]):
        if "aba" in m or not navs:
            u = "https" + chr(58) + "//youtube.com"; subprocess.Popen(f"xdg-open '{u}'", shell=True); return "Abrindo o YouTube."
        return f"O navegador ({', '.join(navs)}) já tá aberto. Diz 'abre aba do youtube' se quiser outra aba."
    if "discord" in m and any(v in m for v in ["abre", "abrir", "abra", "inicia"]):
        if "discord" in ab: return "Discord já tá aberto."
        subprocess.Popen("discord", shell=True); return "Abrindo o Discord."
    if "audacious" in m and any(v in m for v in ["abre", "abrir", "abra", "musica", "música"]):
        if "audacious" in ab: return "Audacious já tá aberto."
        subprocess.Popen("audacious", shell=True); return "Abrindo o Audacious."
    if ("despejo" in m or "pendrive" in m) and any(v in m for v in ["abre", "abrir", "abra", "mostra"]):
        subprocess.Popen(f"xdg-open '{DESPEJO_DIR}'", shell=True); return "Abrindo 2_Arquivo_de_Despejo."
    if "conecta note" in m:
        sc = os.path.expanduser("~/.local/bin/conectar-note.sh")
        if os.path.exists(sc): subprocess.Popen(f"bash '{sc}'", shell=True); return "Conectando mouse/teclado com o Notebook!"
    if "fone note" in m:
        sc = os.path.expanduser("~/.local/bin/ligar-audio-note.sh")
        if os.path.exists(sc): subprocess.Popen(f"bash '{sc}'", shell=True); return "Jogando áudio do Notebook pro fone!"
    return None

def carregar_memoria():
    mems = []
    for arq in sorted(glob.glob(os.path.join(MEMORIA_DIR, "*.txt")) + glob.glob(os.path.join(MEMORIA_DIR, "*.md"))):
        if "chave_api" in arq: continue
        with open(arq, "r", encoding="utf-8", errors="ignore") as f: mems.append(f.read().strip())
    return "\n\n".join(mems)[:4000]

def perguntar_offline(sys_msg, user_input):
    srv, mod = os.path.join(BASE_DIR, "bin64", "yen-server"), os.path.join(BASE_DIR, "cerebro", "yen-completo.gguf")
    if not (os.path.exists(srv) and os.path.exists(mod)): return "[Offline sem modelo local]"
    subprocess.Popen([srv, "-m", mod, "--port", "8089", "--host", "127.0.0.1", "-t", "4", "-c", "2048", "--no-mmap"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(20):
        try:
            req = urllib.request.Request("http://127.0.0", data=json.dumps({"messages":[{"role":"system","content":sys_msg[:1800]},{"role":"user","content":user_input}],"max_tokens":300}).encode(), headers={"Content-Type":"application/json"})
            return json.loads(urllib.request.urlopen(req, timeout=45).read().decode())["choices"][0]["message"]["content"].strip()
        except Exception: time.sleep(0.5)
    return "[Offline: servidor demorou a responder]"

def perguntar_yen(user_input, msgs_hist, mem_base, modo, cb=None):
    rapido = reflexo_rapido(user_input)
    if rapido:
        if cb: cb(rapido)
        return rapido
    api_key = ler_chave()
    if not api_key:
        aviso = "Cole sua chave em 1_Memoria/chave_api.txt"
        if cb: cb(aviso); return aviso
    ab = ", ".join(apps_abertos()) or "nenhum"
    _, _, livre = shutil.disk_usage(BASE_DIR)
    regra = "Responda curto em português (1 a 3 frases)." if modo == "bolso" else f"Responda direto em português. Para criar/mover arquivos, coloque comandos verbose (mkdir -pv, mv -v, cp -v) em ```bash ... ```. NUNCA execute yt-dlp, curl ou downloads da web se o usuário pedir apenas para listar, ver ou procurar arquivos locais. NUNCA invente URLs de imagens; se não tiver a URL exata verificada, diga que não achou o link direto. Pasta padrão: {DESPEJO_DIR}"
    sys_msg = f"{mem_base}\n{regra}\n[PC] Abertos: {ab} | Pastas: {espiar_pastas()} | Habilidades: {listar_habilidades()} | Livre: {round(livre/(1024**3),1)}GB"
    contents = [{"role": ("user" if m["role"] == "user" else "model"), "parts": [{"text": m["content"]}]} for m in msgs_hist[-8:]]
    contents.append({"role": "user", "parts": [{"text": user_input}]})
    payload = {"system_instruction": {"parts": [{"text": sys_msg}]}, "contents": contents, "generationConfig": {"temperature": 0.6, "maxOutputTokens": 450}}
    host = "generativelanguage" + "." + "googleapis" + ".com"
    url = "https" + chr(58) + "//" + host + "/v1beta/models/gemini-flash-lite-latest" + chr(58) + "generateContent?key=" + api_key
    try:
        out = subprocess.check_output(["curl", "-4", "-s", "-X", "POST", url, "-H", "Content-Type: application/json", "-d", json.dumps(payload)], text=True, timeout=45)
        res = json.loads(out)
        if "error" in res:
            aviso = f"[API: {res['error'].get('message', res['error'])}]"
            if cb: cb(aviso); return aviso
        cand = next(iter(res["candidates"]))
        part = next(iter(cand["content"]["parts"]))
        texto = part["text"].strip()
        if cb: cb(texto)
        return texto
    except Exception as e:
        aviso = perguntar_offline(sys_msg, user_input)
        if cb: cb(aviso); return aviso

def corrigir_comando_ia(cmd_falho, erro_log):
    api_key = ler_chave()
    if not api_key: return ""
    prompt = f"O comando Linux falhou:\n{cmd_falho}\n\nErro:\n{erro_log[-600:]}\n\nResponda APENAS com o comando Linux corrigido dentro de ```bash ... ``` sem explicações."
    payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.2, "maxOutputTokens": 200}}
    host = "generativelanguage" + "." + "googleapis" + ".com"
    url = "https" + chr(58) + "//" + host + "/v1beta/models/gemini-flash-lite-latest" + chr(58) + "generateContent?key=" + api_key
    try:
        out = subprocess.check_output(["curl", "-4", "-s", "-X", "POST", url, "-H", "Content-Type: application/json", "-d", json.dumps(payload)], text=True, timeout=20)
        res = json.loads(out)
        cand = next(iter(res["candidates"]))
        part = next(iter(cand["content"]["parts"]))
        blocos = re.findall(r"```bash\n(.*?)\n```", part["text"], re.DOTALL)
        return next(iter(blocos)).strip() if blocos else ""
    except Exception: return ""

def executar_com_progresso(resposta, log_fn, prog_fn):
    for b in re.findall(r"```bash\n(.*?)\n```", resposta, re.DOTALL):
        cmd = b.strip()
        if not cmd: continue
        for tentativa in range(2):
            ok, mot = comando_seguro(cmd)
            if not ok: log_fn(f"\n[BLOQUEADO] {mot}: {cmd}\n", "alerta"); break
            log_fn(f"\n> {cmd}\n", "sys")
            prog_fn(20, "Executando..." if tentativa == 0 else "Auto-corrigindo...")
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            pct, saida_total = 25, ""
            for linha in proc.stdout:
                pct = min(92, pct + 10); prog_fn(pct, "Processando...")
                limpa_l = re.sub(r"\x1b\[[0-9;]*m|\x03[0-9]{0,2}", "", linha)
                saida_total += limpa_l; log_fn(f"  {limpa_l}", "sys")
            rc = proc.wait()
            if rc == 0:
                prog_fn(100, "Concluído"); time.sleep(0.4); prog_fn(0, "Pronto"); break
            elif tentativa == 0:
                log_fn("  [Auto-Reparo] Detectei erro. Reprogramando comando...\n", "alerta")
                novo_cmd = corrigir_comando_ia(cmd, saida_total)
                if novo_cmd and novo_cmd != cmd: cmd = novo_cmd; continue
            prog_fn(0, "Falhou"); break

BG, PANEL, NEON, TXT, MUTED, RED = "#0F111A", "#161925", "#38BDF8", "#E2E8F0", "#64748B", "#F43F5E"

def limpar_fala(texto):
    t = re.sub(r"```bash.*?```", "", texto, flags=re.DOTALL).strip()
    return t or "Executando ação no sistema..."

def salvar_sessao(hist):
    if not hist: return
    arq = os.path.join(MEMORIA_DIR, "historico_recente.txt")
    linhas = [f"{m['role']}: {m['content'][:160].replace(chr(10), ' ')}" for m in hist[-8:]]
    open(arq, "w", encoding="utf-8").write("=== ÚLTIMA SESSÃO ===\n" + "\n".join(linhas) + "\n")

def abrir_chat(modo):
    mem_base = carregar_memoria(); msgs_hist = []
    root = tk.Tk(); root.title("Yen"); root.configure(bg=BG, highlightbackground=NEON, highlightthickness=1)
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    if modo == "bolso":
        root.attributes("-topmost", True)
        try: root.attributes("-alpha", 0.90)
        except Exception: pass
        w, h = min(360, int(sw * 0.34)), min(230, int(sh * 0.32))
        root.geometry(f"{w}x{h}+{sw-w-12}+{sh-h-44}"); ft = ("Monospace", 9)
    else:
        w, h = int(sw * 0.92), int(sh * 0.88)
        root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}"); ft = ("Monospace", 10)
    topo = tk.Frame(root, bg=PANEL, height=26); topo.pack(fill=tk.X)
    tk.Label(topo, text=" YEN  |  Gemini Flash Lite   |   Ajuda: Yen me ajuda", fg=NEON, bg=PANEL, font=("Monospace", 9, "bold")).pack(side=tk.LEFT, padx=8, pady=4)
    tk.Button(topo, text="X", command=lambda: (salvar_sessao(msgs_hist), root.destroy()), bg=PANEL, fg=MUTED, activeforeground=RED, activebackground=PANEL, bd=0, font=("Monospace", 9, "bold")).pack(side=tk.RIGHT, padx=8)
    tk.Frame(root, bg=NEON, height=1).pack(fill=tk.X)
    ef = tk.Frame(root, bg=PANEL, pady=5, padx=6); ef.pack(fill=tk.X, side=tk.BOTTOM)
    ent = tk.Entry(ef, bg=BG, fg=TXT, insertbackground=NEON, relief=tk.FLAT, font=ft)
    ent.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4, padx=(0, 6))
    lbl_prog = None
    if modo == "completo":
        pf = tk.Frame(root, bg=BG, pady=3, padx=8); pf.pack(fill=tk.X, side=tk.BOTTOM)
        lbl_prog = tk.Label(pf, text="[░░░░░░░░░░░░░░░░░░░░] 0%  Pronto", fg=NEON, bg=BG, font=("Monospace", 8), anchor="w"); lbl_prog.pack(fill=tk.X)
    def set_prog(pct, status):
        if not lbl_prog: return
        c = int(pct // 5); barra = "█" * c + "░" * (20 - c)
        root.after(0, lambda: lbl_prog.config(text=f"[{barra}] {pct}%  {status}"))
    fc = tk.Frame(root, bg=BG); fc.pack(fill=tk.BOTH, expand=True)
    sc = tk.Scrollbar(fc, bg=PANEL, troughcolor=BG, activebackground=NEON, bd=0, width=8); sc.pack(side=tk.RIGHT, fill=tk.Y)
    chat = tk.Text(fc, bg=BG, fg=TXT, font=ft, wrap=tk.WORD, bd=0, padx=10, pady=8, yscrollcommand=sc.set, state=tk.DISABLED)
    chat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); sc.config(command=chat.yview)
    chat.tag_config("ian", foreground=NEON, font=("Monospace", 10, "bold"))
    chat.tag_config("yen", foreground="#94A3B8", font=("Monospace", 10, "bold"))
    chat.tag_config("sys", foreground="#34D399"); chat.tag_config("alerta", foreground=RED)
    def add(t, tag=None):
        chat.configure(state=tk.NORMAL); chat.insert(tk.END, t, tag); chat.see(tk.END); chat.configure(state=tk.DISABLED)
    add("Yen: ", "yen"); add(f"Online. {raio_x_pc()} | {organizar_pasta(DESPEJO_DIR)}\n\n", "sys")
    def focar(e=None): root.focus_force(); ent.focus_set()
    ent.bind("<Button-1>", focar); root.after(150, focar)
    def enviar(e=None):
        msg = ent.get().strip()
        if not msg: return
        ent.delete(0, tk.END)
        if msg.lower() in ["sair", "exit", "tchau"]: salvar_sessao(msgs_hist); root.destroy(); return
        add("Ian: ", "ian"); add(f"{msg}\n"); add("Yen: ", "yen")
        ent.configure(state=tk.DISABLED); btn.configure(state=tk.DISABLED)
        def job():
            if modo == "completo": set_prog(20, "Processando...")
            resp = perguntar_yen(msg, msgs_hist, mem_base, modo, lambda t: root.after(0, add, limpar_fala(t)))
            root.after(0, add, "\n\n")
            if modo == "completo":
                executar_com_progresso(resp, lambda m, tg="sys": root.after(0, add, m, tg), set_prog)
                set_prog(0, "Pronto")
            msgs_hist.append({"role": "user", "content": msg}); msgs_hist.append({"role": "assistant", "content": resp})
            root.after(0, lambda: (ent.configure(state=tk.NORMAL), btn.configure(state=tk.NORMAL), focar()))
        threading.Thread(target=job, daemon=True).start()
    btn = tk.Button(ef, text="Enviar", command=enviar, bg=NEON, fg=BG, bd=0, padx=10, font=("Monospace", 9, "bold")); btn.pack(side=tk.RIGHT)
    ent.bind("<Return>", enviar); root.mainloop()

if __name__ == "__main__":
    sel = tk.Tk(); sel.title("Yen"); sel.configure(bg=BG, highlightbackground=NEON, highlightthickness=1)
    sw, sh = sel.winfo_screenwidth(), sel.winfo_screenheight()
    sel.geometry(f"280x110+{(sw-280)//2}+{(sh-110)//2}"); sel.attributes("-topmost", True)
    tk.Label(sel, text="YEN", fg=NEON, bg=BG, font=("Monospace", 11, "bold")).pack(pady=(12, 10))
    bf = tk.Frame(sel, bg=BG); bf.pack()
    tk.Button(bf, text="Completo", width=11, height=1, bg=PANEL, fg=TXT, activebackground=NEON, activeforeground=BG, bd=1, font=("Monospace", 9), command=lambda: (sel.destroy(), abrir_chat("completo"))).pack(side=tk.LEFT, padx=6)
    tk.Button(bf, text="Bolso", width=11, height=1, bg=PANEL, fg=NEON, activebackground=NEON, activeforeground=BG, bd=1, font=("Monospace", 9), command=lambda: (sel.destroy(), abrir_chat("bolso"))).pack(side=tk.LEFT, padx=6)
    sel.mainloop()
