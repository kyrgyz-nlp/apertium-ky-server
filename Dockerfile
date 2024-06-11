FROM debian:bullseye-slim
LABEL maintainer sushain@skc.name
ENV LANG C.UTF-8

ADD https://apertium.projectjj.com/apt/apertium-packaging.public.gpg /etc/apt/trusted.gpg.d/apertium.gpg
RUN chmod 644 /etc/apt/trusted.gpg.d/apertium.gpg

ADD https://apertium.projectjj.com/apt/apertium.pref /etc/apt/preferences.d/apertium.pref
RUN chmod 644 /etc/apt/preferences.d/apertium.pref

RUN echo "deb http://apertium.projectjj.com/apt/release bullseye main" > /etc/apt/sources.list.d/apertium.list

RUN apt-get -qq update && apt-get -qq install apertium-all-dev autoconf automake libtool python-is-python3

COPY ./apertium-kir /home/apertium-kir
WORKDIR /home/apertium-kir

RUN cd /home/apertium-kir && ./autogen.sh --prefix=/home/apertium-kir
RUN make

CMD ["tail", "-f", "/dev/null"]
