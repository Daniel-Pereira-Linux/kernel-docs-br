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

if ! command -v docker &> /dev/null; then
    echo "🐳 Docker nao encontrado no seu sistema."
    echo "Instalando Docker automaticamente (suporta Ubuntu, Debian, Fedora, Arch, ChromeOS...)"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
    echo "✅ Docker instalado com sucesso!"
else
    echo "✅ Docker detectado no sistema."
fi

echo ""
echo "[1/4] Preparando diretorio local..."
mkdir -p ~/kernelbase-vm
cd ~/kernelbase-vm

echo "[2/4] Baixando a infraestrutura oficial..."
curl -sO https://kernelbase.com.br/dev-env/Dockerfile
curl -sO https://kernelbase.com.br/dev-env/atualizar-kernel.sh
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

echo "[3/4] Construindo sua Maquina Virtual..."
echo "Aviso: Isso vai baixar o Kernel inteiro. Pode demorar uns 15-20 minutos dependendo da sua internet."
sudo docker build -t kernelbase-dev .

echo "[4/4] Criando atalho global 'kernelbase'..."
sudo sh -c 'cat <<BIN > /usr/local/bin/kernelbase
#!/bin/bash
echo "🚀 Entrando na Maquina Isolada KernelBase..."
sudo docker start -ai kernelbase-machine
BIN'
sudo chmod +x /usr/local/bin/kernelbase

echo ""
echo "================================================="
echo " ✅ SUCESSO ABSOLUTO! O ambiente foi instalado!"
echo " A partir de hoje, basta abrir o seu terminal e digitar:"
echo ""
echo "    kernelbase"
echo ""
echo " Voce caira direto dentro da maquina isolada de"
echo " desenvolvimento. Para atualizar o kernel lá dentro,"
echo " basta digitar 'atualizar-vm'."
echo "================================================="
echo ""

echo "Iniciando a maquina pela primeira vez..."
if sudo docker ps -a | grep -q "kernelbase-machine"; then
    sudo docker rm -f kernelbase-machine
fi

sudo docker run -it --name kernelbase-machine \
    -v $(pwd)/.gitconfig_dev:/root/.gitconfig \
    kernelbase-dev
