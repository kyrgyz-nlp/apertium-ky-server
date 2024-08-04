ARG PYTHON_VERSION=3.11-slim-bookworm
FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ADD https://apertium.projectjj.com/apt/apertium-packaging.public.gpg /etc/apt/trusted.gpg.d/apertium.gpg
RUN chmod 644 /etc/apt/trusted.gpg.d/apertium.gpg

ADD https://apertium.projectjj.com/apt/apertium.pref /etc/apt/preferences.d/apertium.pref
RUN chmod 644 /etc/apt/preferences.d/apertium.pref

RUN echo "deb http://apertium.projectjj.com/apt/nightly bookworm main" > /etc/apt/sources.list.d/apertium.list

RUN apt-get -qq update && apt-get -qq upgrade -y \
    && apt-get install --no-install-recommends -y \ 
    bash \
    brotli \
    build-essential \
    libpq-dev \
    gcc \
    procps \
    apertium-all-dev \
    autoconf \
    automake \
    libtool \
    zip \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Build Apertium
COPY ./apertium-kir /home/app/apertium-kir
WORKDIR /home/app/apertium-kir
RUN ./autogen.sh --prefix=/home/app/apertium-kir && make

# Create app user and set up directories
RUN useradd -ms /bin/bash app
RUN mkdir -p /home/app/code /home/app/.local
RUN chown -R app:app /home/app/code /home/app/.local

# Switch to app user
USER app

WORKDIR /home/app/code

COPY --chown=app:app requirements.txt /home/app/code/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --user --no-cache-dir -r /home/app/code/requirements.txt

ENV PATH="/home/app/.local/bin:${PATH}"

COPY --chown=app:app . /home/app/code

EXPOSE 8000

ENTRYPOINT ["/home/app/code/entrypoint.sh"]

CMD ["gunicorn", "--workers", "2", "--threads", "3", "--timeout", "600", "--bind", ":8000", "corpus_builder.wsgi"]
