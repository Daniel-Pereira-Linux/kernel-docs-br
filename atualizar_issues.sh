#!/bin/bash

# Garante que você está logado no GitHub CLI localmente
if ! gh auth status &>/dev/null; then
  echo "❌ Erro: Você precisa estar logado no GitHub CLI. Rode 'gh auth login' primeiro."
  exit 1
fi

echo "🔍 Buscando Issues ativas com a label 'aguardando-traducao'..."

# Lista todas as Issues abertas que possuem a label amarela
ISSUES=$(gh issue list --label "aguardando-traducao" --limit 100 --json number,title --jq '.[] | "\(.number)|\(.title)"')

if [ -z "$ISSUES" ]; then
  echo "⚠️ Nenhuma Issue ativa encontrada com a label 'aguardando-traducao'."
  exit 0
fi

echo "$ISSUES" | while IFS='|' read -r NUMERO TITULO; do
  # Extrai apenas o caminho do arquivo do título antigo (Ex: remove "[Ciclo: ...] Tradução de ")
  ARQ_LIMPO=$(echo "$TITULO" | sed -E 's/\[Ciclo: [0-9\/]+\] Tradução de //g' | xargs)
  
  echo "🔄 Atualizando descrição da Issue #${NUMERO} (${ARQ_LIMPO})..."

  # Monta o corpo com o manual completo e o layout do robô de patches
  CORPO_ISSUE="## 📑 Guia de Tradução: \`${ARQ_LIMPO}\`

Olá! Esta é uma discussão automatizada para coordenar a tradução do arquivo upstream.

Se você deseja assumir este arquivo, **comente nesta Issue** avisando o mantenedor @Daniel-Pereira-Linux!

---

### ⚙️ Passo 0: Configurando sua Identidade no Git
\`\`\`bash
git config --global user.name \"Seu Nome Completo\"
git config --global user.email \"seu_email@provedor.com\"
\`\`\`

### 🚀 Passo a Passo para Contribuir

#### 1. Configurando o Ambiente e o Upstream (Repositório do Corbet)
\`\`\`bash
git clone https://github.com/Daniel-Pereira-Linux/kernel-docs-br.git
cd kernel-docs-br

git remote add upstream https://git.kernel.org/pub/scm/linux/kernel/git/docs/linux.git
git fetch upstream docs-next
\`\`\`

#### 2. Criando sua Branch de Trabalho
\`\`\`bash
git checkout -b traducao-\$(basename ${ARQ_LIMPO} .rst) origin/docs-next
\`\`\`

#### 3. Traduzindo o Arquivo
- Crie ou edite o arquivo espelho exatamente em: \`pt_BR/${ARQ_LIMPO}\`.
- Mantenha tabelas e marcações Sphinx idênticos.

#### 4. Validando Localmente
\`\`\`bash
make htmldocs
\`\`\`

#### 5. Padronização do Commit (Formato Oficial do Kernel)
\`\`\`bash
git add pt_BR/${ARQ_LIMPO}
git commit -s -m \"docs: pt_BR: Tradução de \$(basename ${ARQ_LIMPO})\"
\`\`\`

---

### 🧪 🤖 Sistema de Pré-Revisão Automatizada (CI/CD na Issue)
Não tem o Sphinx instalado? O robô faz o teste para você!
1. Anexe o seu arquivo \`.patch\` em um comentário nesta Issue.
2. Escreva no mesmo comentário a frase: **\`analise o meu patch\`**.
3. O robô baixará o anexo, aplicará na árvore do Corbet e rodará o \`./scripts/checkpatch.pl\` e o \`make htmldocs\`, postando o veredito aqui e aguardando o mantenedor @Daniel-Pereira-Linux."

  # Executa a atualização da Issue na nuvem usando a API do GitHub
  gh issue edit "$NUMERO" --body "$CORPO_ISSUE"
  
  echo "✅ Issue #${NUMERO} atualizada com sucesso!"
  sleep 1 # Evita rate limit na API do GitHub
done

echo "🎉 Todas as suas Issues antigas foram atualizadas com o novo manual!"
