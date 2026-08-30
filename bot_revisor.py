import os
import re
import json
import mailbox
import subprocess
import urllib.request
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
    prompt = f"""Você é um Engenheiro de Kernel Linux. O patch abaixo falhou ao ser aplicado via 'git am' na documentação pt_BR.
ERRO DO GIT:
{erro_git}
PATCH ORIGINAL:
{patch_text}
Corrija o patch para que ele seja aplicado com sucesso. Retorne APENAS o código do patch (diff unificado) em texto puro, sem markdown."""
    try:
        response = client.models.generate_content(model='gemini-2.5-pro', contents=prompt)
        text = response.text.replace('```diff\n', '').replace('```', '')
        return text.strip()
    except:
        return None

def analisar_patch(msg):
    subject = msg.get('Subject', '')
    autor = msg.get('From', '')
    msg_id = msg.get('Message-ID', '')
    
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

    patch_path = os.path.abspath("temp_patch.patch")
    with open(patch_path, "w", encoding="utf-8") as f:
        f.write(str(msg))
        
    checkpatch_log = ""
    sphinx_log = ""
    status_aplicacao = "✅ Aplicado com sucesso"

    if os.path.exists("linux"):
        code, out = run_cmd(f"./scripts/checkpatch.pl --strict {patch_path}")
        checkpatch_log = out

        run_cmd("git am --abort")
        code, out = run_cmd(f"git am {patch_path}")
        
        if code != 0:
            run_cmd("git am --abort")
            status_aplicacao = "❌ Falha ao aplicar (Conflito). Acionando IA para resolução..."
            novo_patch = resolver_conflito_ia(body, out)
            if novo_patch:
                with open(patch_path, "w", encoding="utf-8") as f:
                    f.write(novo_patch)
                code2, out2 = run_cmd(f"git apply {patch_path}")
                if code2 == 0:
                    status_aplicacao = "⚠️ Aplicado com sucesso após correção automática da IA!"
                else:
                    status_aplicacao = "❌ Falha total: Nem a IA conseguiu resolver o conflito."
                    run_cmd("git apply --abort")
            
        if "Sucesso" in status_aplicacao or "Aplicado" in status_aplicacao:
            code, out = run_cmd("make SPHINXDIRS=translations/pt_BR htmldocs")
            avisos = [linha for linha in out.split('\n') if 'WARNING:' in linha or 'ERROR:' in linha]
            sphinx_log = "\n".join(avisos) if avisos else "Nenhum erro de Sphinx (Make HTMLDOCS 100% OK)."
        
        run_cmd("git reset --hard HEAD")
        run_cmd("git clean -fdx")

    diff_lines = []
    for line in body.split('\n'):
        if line.startswith('+') and not line.startswith('+++'):
            linha_limpa = line[1:].strip()
            if len(linha_limpa) > 3 and not linha_limpa.startswith('.. '):
                diff_lines.append(linha_limpa)
                
    texto_traduzido = "\n".join(diff_lines)
    
    revisao_ia = "Sem texto útil para revisar."
    if len(texto_traduzido) > 10:
        prompt = f"Revise a gramática/ortografia pt_BR. Ignore formatação técnica. TEXTO:\n{texto_traduzido}"
        try:
            revisao_ia = client.models.generate_content(model='gemini-2.5-pro', contents=prompt).text.strip()
        except:
            revisao_ia = "Erro ao conectar com Gemini."

    return {
        "message_id": msg_id,
        "assunto": subject,
        "autor": autor,
        "data": msg.get('Date', ''),
        "erros_estrutura": erros_estrutura,
        "status_git": status_aplicacao,
        "checkpatch": checkpatch_log[:1000],
        "sphinx": sphinx_log[:1000],
        "revisao_ia": revisao_ia
    }

def main():
    db_url = "https://raw.githubusercontent.com/Daniel-Pereira-Linux/kernel-docs-br/gh-pages/data_reviews.json"
    historico = []
    try:
        req = urllib.request.Request(db_url)
        with urllib.request.urlopen(req) as response:
            historico = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print("Banco de dados não encontrado ou vazio. Iniciando um novo cache.")

    # GARANTIA ABSOLUTA DE PRESERVAÇÃO HISTÓRICA
    # Transformamos a lista num dicionário onde TUDO o que já foi analisado no passado FICA GUARDADO.
    banco_de_dados = { item.get('message_id'): item for item in historico if 'message_id' in item }
    
    if os.path.exists("patches"):
        for filename in os.listdir("patches"):
            if filename.endswith(".mbx"):
                mbox = mailbox.mbox(os.path.join("patches", filename))
                for msg in mbox:
                    subj = msg.get('Subject', '')
                    if 'pt_BR' in subj or 'pt-br' in subj.lower():
                        msg_id = msg.get('Message-ID', '')
                        
                        if msg_id not in banco_de_dados:
                            print(f"🔍 Analisando NOVO patch: {subj}")
                            banco_de_dados[msg_id] = analisar_patch(msg)
                        else:
                            print(f"⏭️ Pulando análise IA (mas preservando no histórico do site): {subj}")
                        
    # Reverte o dicionário para uma lista para salvar no JSON do site
    resultados_finais = list(banco_de_dados.values())
    
    # Ordena para os mais recentes ficarem no topo (opcional, mas recomendado)
    resultados_finais.reverse()

    with open("reviews.json", "w", encoding="utf-8") as f:
        json.dump(resultados_finais, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
