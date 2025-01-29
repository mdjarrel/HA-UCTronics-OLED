ARG BUILD_FROM
FROM ${BUILD_FROM}
ENV LANG C.UTF-8

RUN set -xe \
    && apk add --no-cache gcc build-base git i2c-tools nano linux-headers cmake pacman
	
RUN \
    set -xe \
    && apk add --no-cache \
    procps\
    bash \
    jq \
    tzdata \
    curl \
    nano \
    ca-certificates \
	font-dejavu \
    python3 \
    python3-dev \
    py3-pip \
	py3-requests \
	py3-pillow \
	py3-websocket-client \
	py3-numpy \
	libjpeg \
	jpeg-dev \
	libjpeg-turbo-dev \
	freetype-dev \
	openjpeg
	
RUN pip3 install --break-system-packages smbus2 gpiozero

# Copy over the Python project
COPY /python* /UCTronics_OLED/

COPY run.sh /
COPY start.sh /
WORKDIR /data
RUN chmod a+x /run.sh
RUN chmod a+x /start.sh

CMD [ "/start.sh" ]