#!/bin/bash

TOKEN=$1
if [ -z "$TOKEN" ]; then
    echo "❌ Erro: Voce precisa fornecer o Token. Ex: kernelbase restore XYZ.gpg"
    exit 1
fi

echo "☁️ Buscando backup criptografado na nuvem ($TOKEN)..."
curl -sL "https://0x0.st/$TOKEN" -o /tmp/backup.tar.gz.gpg

if [ ! -s /tmp/backup.tar.gz.gpg ] || grep -q "Not Found" /tmp/backup.tar.gz.gpg; then
     echo "❌ Erro: Token invalido, expirado ou arquivo nao encontrado."
     rm -f /tmp/backup.tar.gz.gpg
     exit 1
fi

echo ""
echo "🔓 Descriptografando backup (Digite sua senha)..."
gpg --decrypt /tmp/backup.tar.gz.gpg > /tmp/backup.tar.gz

if [ $? -ne 0 ]; then
    echo "❌ Erro: Senha incorreta ou arquivo corrompido!"
    rm -f /tmp/backup.tar.gz.gpg /tmp/backup.tar.gz
    exit 1
fi

echo "📦 Restaurando ambiente (Credenciais e Codigo)..."
cd /tmp
tar -xzf backup.tar.gz

cp kernelbase_backup/gitconfig /root/.gitconfig 2>/dev/null || true

cd /kernel-src
if [ -s /tmp/kernelbase_backup/commits.bundle ]; then
    git pull /tmp/kernelbase_backup/commits.bundle HEAD >/dev/null 2>&1 || true
fi

if [ -s /tmp/kernelbase_backup/working_tree.patch ]; then
    git apply /tmp/kernelbase_backup/working_tree.patch >/dev/null 2>&1 || true
fi

echo ""
echo "================================================="
echo " ✅ AMBIENTE RESTAURADO COM SUCESSO!"
echo " Bem-vindo de volta! Voce ja pode digitar 'kernelbase'"
echo " para entrar na sua maquina e continuar de onde parou."
echo "================================================="

rm -rf /tmp/kernelbase_backup backup.tar.gz backup.tar.gz.gpg
