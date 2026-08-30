import os
import re
import json
import mailbox
import subprocess
from google import genai

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("GEMINI_API_KEY não encontrada.")
    exit(1)

client = genai.Client(api_key=api_key)

def run_cmd(cmd, cwd="linux"):
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, shell=True)
        return result.returncode, result.stdout + result.stderr
    except Exception as e:
        return 1, str(e)

def resolver_conflito_ia(patch_text, erro_git):
    prompt = f"""
    Você é um Engenheiro de Kernel Linux. O patch abaixo falhou ao ser aplicado via 'git am' na documentação pt_BR.
    
    ERRO DO GIT:
    {erro_git}
    
    PATCH ORIGINAL:
    {patch_text}
    
    Corrija o patch para que ele seja aplicado com sucesso. 
    Retorne APENAS o código do patch (diff unificado) em texto puro, sem formatação markdown (```).
    """
    try:
        response = client.models.generate_content(model='gemini-2.5-pro', contents=prompt)
        text = response.text.replace('```diff\n', '').replace('```', '')
        return text.strip()
    except:
        return None

def analisar_patch(msg):
    subject = msg.get('Subject', '')
    autor = msg.get('From', '')
    
    # Extrair corpo
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                break
    else:
        body = msg.get_payload(decode=True).decode('utf-8', errors='replace')

    erros_estrutura = []
    if "Signed-off-by:" not in body:
        erros_estrutura.append("Falta a tag 'Signed-off-by' (DCO obrigatório).")

    # Salva o patch temporário
    patch_path = os.path.abspath("temp_patch.patch")
    with open(patch_path, "w", encoding="utf-8") as f:
        f.write(str(msg)) # salva o email cru como patch
        
    checkpatch_log = ""
    sphinx_log = ""
    status_aplicacao = "✅ Aplicado com sucesso"

    if os.path.exists("linux"):
        # 1. Rodar Checkpatch
        code, out = run_cmd(f"./scripts/checkpatch.pl --strict {patch_path}")
        checkpatch_log = out

        # 2. Aplicar o Patch (git am)
        run_cmd("git am --abort") # limpar estado anterior
        code, out = run_cmd(f"git am {patch_path}")
        
        if code != 0:
            run_cmd("git am --abort")
            status_aplicacao = "❌ Falha ao aplicar (Conflito). Acionando IA para resolução..."
            
            # Tentar resolver via IA
            novo_patch = resolver_conflito_ia(body, out)
            if novo_patch:
                with open(patch_path, "w", encoding="utf-8") as f:
                    f.write(novo_patch)
                # Tenta aplicar com git apply porque o email header pode ter sumido
                code2, out2 = run_cmd(f"git apply {patch_path}")
                if code2 == 0:
                    status_aplicacao = "⚠️ Aplicado com sucesso após correção automática da IA!"
                else:
                    status_aplicacao = "❌ Falha total: Nem a IA conseguiu resolver o conflito."
                    run_cmd("git apply --abort")
            
        # 3. Rodar Make HTMLDOCS (Apenas pt_BR para ser rápido)
        if "Sucesso" in status_aplicacao or "Aplicado" in status_aplicacao:
            code, out = run_cmd("make SPHINXDIRS=translations/pt_BR htmldocs")
            # Extrair apenas os avisos/erros
            avisos = [linha for linha in out.split('\n') if 'WARNING:' in linha or 'ERROR:' in linha]
            sphinx_log = "\n".join(avisos) if avisos else "Nenhum erro de Sphinx (Make HTMLDOCS 100% OK)."
        
        # 4. Limpar a árvore para o próximo patch
        run_cmd("git reset --hard HEAD")
        run_cmd("git clean -fdx")

    # Analisar gramática do diff original com Gemini
    diff_lines = [line[1:] for line in body.split('\n') if line.startswith('+') and not line.startswith('+++')]
    texto_traduzido = "\n".join(diff_lines).strip()
    
    revisao_ia = "Sem texto."
    if len(texto_traduzido) > 10:
        prompt = f"""Você é um revisor gramatical para documentação pt_BR do Linux. Aponte APENAS erros gramaticais e ortográficos. TEXTO: {texto_traduzido}"""
        try:
            revisao_ia = client.models.generate_content(model='gemini-2.5-pro', contents=prompt).text.strip()
        except:
            revisao_ia = "Erro Gemini."

    return {
        "assunto": subject,
        "autor": autor,
        "data": msg.get('Date', ''),
        "erros_estrutura": erros_estrutura,
        "status_git": status_aplicacao,
        "checkpatch": checkpatch_log[:1000], # Limitar tamanho
        "sphinx": sphinx_log[:1000],
        "revisao_ia": revisao_ia
    }

def main():
    if not os.path.exists("patches"):
        return

    resultados = []
    for filename in os.listdir("patches"):
        if filename.endswith(".mbx"):
            mbox = mailbox.mbox(os.path.join("patches", filename))
            for msg in mbox:
                subj = msg.get('Subject', '')
                if 'pt_BR' in subj or 'pt-br' in subj.lower():
                    resultados.append(analisar_patch(msg))
                    
    with open("reviews.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
