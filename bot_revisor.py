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

def analisar_patch(msg):
    erros = []
    subject = msg.get('Subject', '')
    
    # Extrair corpo
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                break
    else:
        body = msg.get_payload(decode=True).decode('utf-8', errors='replace')

    # 1. Checar Assinatura
    if "Signed-off-by:" not in body:
        erros.append("Falta a tag 'Signed-off-by' (DCO obrigatório).")

    # 2. Checar log de mudanças (Changes in vX)
    if re.search(r'\[.*v[2-9].*\]', subject, re.IGNORECASE):
        # Procura onde estão os '---'
        parts = body.split('---', 1)
        if len(parts) > 1:
            before_dashes = parts[0]
            if re.search(r'(?i)changes in v|v[2-9] changes', before_dashes):
                erros.append("O changelog da versão (ex: Changes in v2) está ACIMA dos '---'. Ele deve ficar abaixo para não poluir a mensagem de commit final.")
        else:
            erros.append("Separador '---' ausente no corpo do patch.")
            
    # 3. Analisar gramática do diff com Gemini
    diff_lines = []
    in_diff = False
    for line in body.split('\n'):
        if line.startswith('diff --git'):
            in_diff = True
        if in_diff and line.startswith('+') and not line.startswith('+++'):
            # Limpa o + inicial
            diff_lines.append(line[1:])
            
    texto_traduzido = "\n".join(diff_lines).strip()
    
    revisao_ia = "Sem trechos traduzidos encontrados."
    if len(texto_traduzido) > 10:
        prompt = f"""
        Você é um revisor restrito para documentação pt_BR do Linux.
        Analise o texto abaixo em busca APENAS de:
        - Erros gramaticais, ortografia e acentuação.
        - Erros de digitação (typos) e palavras grudadas.
        
        NÃO dê sugestões de estilo, NÃO reescreva o texto, NÃO avalie se a tradução é "boa". Ignore comandos técnicos (RST, Sphinx, C).
        Se estiver 100% correto, responda exatamente: "Nenhum erro gramatical encontrado."
        
        TEXTO:
        {texto_traduzido}
        """
        try:
            response = client.models.generate_content(
                model='gemini-2.5-pro',
                contents=prompt,
            )
            revisao_ia = response.text.strip()
        except Exception as e:
            revisao_ia = f"Erro ao consultar Gemini: {str(e)}"

    # 4. (Opcional) Poderíamos extrair o patch e rodar get_maintainer.pl aqui
    # Mas como não temos a árvore completa do linux extraída facilmente no script sem sujeira,
    # vamos listar a regra básica:
    to_cc = str(msg.get('To', '')) + " " + str(msg.get('Cc', ''))
    if "corbet@lwn.net" not in to_cc and "workflows@vger.kernel.org" not in to_cc:
        pass # Apenas um exemplo visual, o get_maintainer real pode ser bem ruidoso.

    return {
        "assunto": subject,
        "autor": msg.get('From', ''),
        "data": msg.get('Date', ''),
        "erros_estrutura": erros,
        "revisao_ia": revisao_ia
    }

def main():
    if not os.path.exists("patches"):
        print("Pasta de patches não encontrada.")
        return

    resultados = []
    
    # Ler os mboxes gerados pelo b4
    for filename in os.listdir("patches"):
        if filename.endswith(".mbx"):
            mbox = mailbox.mbox(os.path.join("patches", filename))
            for msg in mbox:
                # Filtrar apenas os que têm pt_BR no título
                subj = msg.get('Subject', '')
                if 'pt_BR' in subj or 'pt-br' in subj.lower():
                    print(f"Analisando: {subj}")
                    res = analisar_patch(msg)
                    resultados.append(res)
                    
    # Salva o json
    with open("reviews.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
