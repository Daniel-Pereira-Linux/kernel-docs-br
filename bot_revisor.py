#!/usr/bin/env python3
"""
Miguel - Bot Revisor de Patches pt_BR do Kernel Linux.

Dois modos de operação:
1. LISTAGEM (cron): Busca todos os patches pt_BR e salva metadados. Sem IA.
2. ANÁLISE (botão): Recebe um Message-ID específico e roda IA + Checkpatch + Sphinx.
"""

import os
import re
import json
import mailbox
import subprocess
import urllib.request

# ── Configuração ──────────────────────────────────────────────
ANALISAR_MSG_ID = os.environ.get("ANALISAR_MSG_ID", "").strip()
API_KEY = os.environ.get("GEMINI_API_KEY", "")
DB_URL = "https://daniel-pereira-linux.github.io/kernel-docs-br/data_reviews.json"


def run_cmd(cmd, cwd="linux"):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, shell=True)
        return r.returncode, r.stdout + r.stderr
    except Exception as e:
        return 1, str(e)


def carregar_historico():
    """Baixa o banco de dados atual do site (preserva histórico)."""
    try:
        req = urllib.request.Request(DB_URL)
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except:
        print("Banco de dados não encontrado. Iniciando novo.")
        return []


def extrair_patches_do_mbox():
    """Extrai metadados de todos os patches pt_BR do arquivo .mbx."""
    patches = []
    if not os.path.exists("patches"):
        return patches

    for fname in os.listdir("patches"):
        if not fname.endswith(".mbx"):
            continue
        mbox = mailbox.mbox(os.path.join("patches", fname))
        for msg in mbox:
            subj = msg.get("Subject", "")
            if "pt_BR" not in subj and "pt-br" not in subj.lower():
                continue

            msg_id = msg.get("Message-ID", "")
            autor = msg.get("From", "")
            data = msg.get("Date", "")

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode("utf-8", errors="replace")
                        break
            else:
                body = msg.get_payload(decode=True).decode("utf-8", errors="replace")

            patches.append({
                "message_id": msg_id,
                "assunto": subj,
                "autor": autor,
                "data": data,
                "body": body,
            })

    return patches


def analisar_com_ia(patch):
    """Executa análise completa: estrutura, checkpatch, sphinx e gramática via Gemini."""
    from google import genai
    client = genai.Client(api_key=API_KEY)

    body = patch["body"]
    resultado = {
        "analisado": True,
        "erros_estrutura": [],
        "status_git": "⏳ Não testado",
        "checkpatch": "",
        "sphinx": "",
        "revisao_ia": "",
    }

    # 1. Verificar estrutura (Signed-off-by)
    if "Signed-off-by:" not in body:
        resultado["erros_estrutura"].append("Falta a tag 'Signed-off-by' (DCO obrigatório).")

    # 2. Salvar patch temporário
    patch_path = os.path.abspath("temp_patch.patch")
    with open(patch_path, "w", encoding="utf-8") as f:
        f.write(body)

    # 3. Checkpatch
    if os.path.exists("linux"):
        code, out = run_cmd(f"./scripts/checkpatch.pl --strict {patch_path}")
        resultado["checkpatch"] = out[:2000]

        # 4. Tentar aplicar via git am
        run_cmd("git am --abort")
        code, out = run_cmd(f"git am {patch_path}")

        if code == 0:
            resultado["status_git"] = "✅ Aplicado com sucesso"
        else:
            run_cmd("git am --abort")
            resultado["status_git"] = "❌ Falha ao aplicar (conflito)"

        # 5. Sphinx (se aplicou)
        if "✅" in resultado["status_git"]:
            code, out = run_cmd("make SPHINXDIRS=translations/pt_BR htmldocs")
            avisos = [l for l in out.split("\n") if "WARNING:" in l or "ERROR:" in l]
            resultado["sphinx"] = "\n".join(avisos[:20]) if avisos else "Nenhum erro de Sphinx ✅"

        run_cmd("git reset --hard HEAD")
        run_cmd("git clean -fdx")

    # 6. Gramática via Gemini
    diff_lines = []
    for line in body.split("\n"):
        if line.startswith("+") and not line.startswith("+++"):
            limpa = line[1:].strip()
            if len(limpa) > 3 and not limpa.startswith(".. "):
                diff_lines.append(limpa)

    texto = "\n".join(diff_lines)
    if len(texto) > 10:
        try:
            prompt = (
                "Revise APENAS erros de gramática e ortografia no texto pt_BR abaixo. "
                "Ignore formatação técnica RST/Sphinx. Liste apenas os erros encontrados "
                "com a correção sugerida. Se não houver erros, diga 'Nenhum erro encontrado.'\n\n"
                f"TEXTO:\n{texto}"
            )
            resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            resultado["revisao_ia"] = resp.text.strip()
        except Exception as e:
            resultado["revisao_ia"] = f"Erro ao conectar com Gemini: {e}"
    else:
        resultado["revisao_ia"] = "Texto muito curto para revisão gramatical."

    return resultado


def main():
    historico = carregar_historico()
    banco = {item.get("message_id"): item for item in historico if "message_id" in item}

    # ── MODO ANÁLISE: Analisa UM patch específico ──
    if ANALISAR_MSG_ID:

        if ANALISAR_MSG_ID in banco and banco[ANALISAR_MSG_ID].get("analisado"):
            print(f"⏭️ Patch {ANALISAR_MSG_ID} já foi analisado antes! Pulando análise da IA para economizar tokens.")
            return


        # Procura no banco existente ou nos patches baixados
        print(f"\n🔍 Modo ANÁLISE: Buscando patch {ANALISAR_MSG_ID}")
        if ANALISAR_MSG_ID in banco and "body" in banco[ANALISAR_MSG_ID]:
            patch = banco[ANALISAR_MSG_ID]
        else:
            # Tenta encontrar nos patches do mbox
            todos = extrair_patches_do_mbox()
            patch = None
            for p in todos:
                if p["message_id"] == ANALISAR_MSG_ID:
                    patch = p
                    break
            if not patch:
                print(f"❌ Patch {ANALISAR_MSG_ID} não encontrado!")
                # Salva o que temos e sai
                with open("reviews.json", "w", encoding="utf-8") as f:
                    json.dump(list(banco.values()), f, ensure_ascii=False, indent=2)
                return

        if API_KEY:
            resultado = analisar_com_ia(patch)
            patch.update(resultado)
            banco[ANALISAR_MSG_ID] = patch
            print(f"✅ Análise concluída para: {patch.get('assunto', 'sem título')}")
        else:
            print("❌ GEMINI_API_KEY não configurada!")

    # ── MODO LISTAGEM: Busca todos os patches e salva metadados ──
    else:
        print("📋 Modo LISTAGEM: Buscando todos os patches pt_BR...")
        todos = extrair_patches_do_mbox()
        novos = 0
        for p in todos:
            mid = p["message_id"]
            if mid not in banco:
                # Salva metadados SEM análise (sem gastar token)
                banco[mid] = {
                    "message_id": mid,
                    "assunto": p["assunto"],
                    "autor": p["autor"],
                    "data": p["data"],
                    "body": p["body"],
                    "analisado": False,
                    "erros_estrutura": [],
                    "status_git": "⏳ Aguardando análise",
                    "checkpatch": "",
                    "sphinx": "",
                    "revisao_ia": "",
                }
                novos += 1
                print(f"  📩 Novo: {p['assunto']}")
            else:
                print(f"  ⏭️ Já no histórico: {p['assunto']}")

        print(f"\n📊 Total: {len(banco)} patches | {novos} novos")

    # Salva tudo (histórico completo preservado)
    resultados = list(banco.values())
    # Remove o body para não poluir o JSON público (economiza banda)
    for r in resultados:
        r.pop("body", None)

    with open("reviews.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    print("💾 reviews.json salvo com sucesso!")


if __name__ == "__main__":
    main()
