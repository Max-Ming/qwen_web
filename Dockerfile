FROM nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04
LABEL org.opencontainers.image.authors="guopeiming.gpm@gmail.com"
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
        software-properties-common python3-pip openssh-server screen git htop vim curl ffmpeg && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3.10 /usr/bin/python && \
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
RUN pip install transformers
RUN pip install django
RUN pip install "numpy<2"
RUn rm -r /root/.cache/pip

RUN cd ~
RUN git clone https://github.com/Max-Ming/qwen_web & cd qwen_web/static
RUN git clone https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct & cd ../