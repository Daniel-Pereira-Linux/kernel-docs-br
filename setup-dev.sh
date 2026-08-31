#!/bin/bash
set -e

echo "================================================="
echo "   🚀 KernelBase - Setup da Maquina Oficial BR"
echo "================================================="
echo ""
echo "Esta maquina isolada contem todos os compiladores,"
echo "ferramentas de e-mail e a arvore completa do Kernel"
echo "Linux pronta para voce contribuir."
echo ""

read -p "Seu Nome Completo (ex: Linus Torvalds): " GIT_NAME
read -p "Seu E-mail (ex: linus@gmail.com): " GIT_EMAIL
read -p "Senha de App de E-mail (ex: Gmail App Password): " SMTP_PASS

echo ""
echo "[1/3] Preparando diretorio local..."
mkdir -p ~/kernelbase-vm
cd ~/kernelbase-vm

echo "[2/3] Baixando a infraestrutura oficial..."
curl -sO https://daniel-pereira-linux.github.io/kernel-docs-br/dev-env/Dockerfile
curl -sO https://daniel-pereira-linux.github.io/kernel-docs-br/dev-env/atualizar-kernel.sh
chmod +x atualizar-kernel.sh

cat <<CONFIG > .gitconfig_dev
[user]
    name = $GIT_NAME
    email = $GIT_EMAIL
[sendemail]
    smtpencryption = tls
    smtpserver = smtp.gmail.com
    smtpuser = $GIT_EMAIL
    smtpserverport = 587
    smtppass = $SMTP_PASS
CONFIG

echo "[3/3] Construindo sua Maquina Virtual..."
echo "Aviso: Isso vai baixar o Kernel inteiro. Pode demorar uns 15-20 minutos dependendo da sua internet."
sudo docker build -t kernelbase-dev .

echo ""
echo "================================================="
echo " ✅ SUCESSO! Iniciando sua maquina isolada..."
echo " Sempre que quiser voltar a trabalhar nela, rode:"
echo "    sudo docker start -ai kernelbase-machine"
echo " Para atualizar o Kernel lá dentro, digite:"
echo "    atualizar-vm"
echo "================================================="
echo ""

sudo docker run -it --name kernelbase-machine \
    -v $(pwd)/.gitconfig_dev:/root/.gitconfig \
    kernelbase-dev
