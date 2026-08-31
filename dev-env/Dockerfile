FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libncurses-dev \
    bison \
    flex \
    libssl-dev \
    libelf-dev \
    fakeroot \
    vim \
    nano \
    mutt \
    git-email \
    libauthen-sasl-perl \
    libnet-smtp-ssl-perl \
    libio-socket-ssl-perl \
    python3 \
    && rm -rf /var/lib/apt/lists/*

RUN echo "Clonando a arvore oficial do Kernel... (Isso demora um pouco, mas voce so faz uma vez!)"
# Apenas a arvore mainline oficial (vamos fazer shallow parcial para velocidade, mas que permite push)
RUN git clone https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git /kernel-src

WORKDIR /kernel-src

COPY atualizar-kernel.sh /usr/local/bin/atualizar-vm
RUN chmod +x /usr/local/bin/atualizar-vm

# Adiciona um bashrc amigavel
RUN echo 'export PS1="\[\e[32m\][KernelBase VM]\[\e[m\] \[\e[33m\]\w\[\e[m\] \$ "' >> /root/.bashrc

CMD ["/bin/bash"]
