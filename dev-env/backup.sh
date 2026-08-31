#!/bin/bash

echo "🔒 Iniciando Backup Seguro (Cloud Save)..."
mkdir -p /tmp/kernelbase_backup
rm -f /tmp/kernelbase_backup/*

cd /kernel-src || exit 1

echo "Empacotando alteracoes nao salvas..."
git diff HEAD > /tmp/kernelbase_backup/working_tree.patch

echo "Empacotando seus commits locais..."
git bundle create /tmp/kernelbase_backup/commits.bundle origin/master..HEAD >/dev/null 2>&1 || true

echo "Empacotando credenciais de email..."
cp /root/.gitconfig /tmp/kernelbase_backup/gitconfig 2>/dev/null || true

cd /tmp
tar -czf backup.tar.gz kernelbase_backup

echo ""
echo "🔑 SEGURANCA: Crie uma senha para criptografar seu backup."
echo "   (Voce precisara dessa mesma senha para restaurar em outro PC)"
gpg --symmetric --cipher-algo AES256 -o backup.tar.gz.gpg backup.tar.gz

echo ""
echo "☁️ Fazendo upload seguro para a nuvem anonima..."
URL=$(curl -s -F'file=@backup.tar.gz.gpg' https://0x0.st)
TOKEN=$(basename "$URL")

echo ""
echo "================================================="
echo " ✅ BACKUP CONCLUIDO COM SUCESSO!"
echo " Seu TOKEN de recuperacao e: $TOKEN"
echo ""
echo " Guarde este token e a senha que voce inventou."
echo " Em outro PC, instale o ambiente e rode:"
echo "    kernelbase restore $TOKEN"
echo "================================================="

rm -rf /tmp/kernelbase_backup backup.tar.gz backup.tar.gz.gpg
