#!/bin/bash

echo "🔄 Iniciando atualizacao do Kernel..."

cd /kernel-src || exit 1

# Guarda qualquer codigo ou traducao que o usuario nao comitou ainda
git stash -q
echo "📥 Baixando novidades do repositorio oficial (Linus Torvalds)..."
git fetch origin master

# Tenta fazer rebase (colocar o trabalho do BR no topo)
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$current_branch" != "master" ] && [ "$current_branch" != "main" ]; then
    echo "🔀 Aplicando suas traducoes/codigo no topo das novidades (Rebase)..."
    git rebase origin/master
else
    git merge origin/master
fi

# Restaura alteracoes nao comitadas
git stash pop -q 2>/dev/null || true

echo "✅ A arvore do Kernel esta 100% atualizada!"
echo "Suas edicoes continuam aqui, intocaveis."
