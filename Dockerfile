FROM python:3.9-slim

WORKDIR /app

# Install OS deps that pip might need (git for git+ URLs, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
 && rm -rf /var/lib/apt/lists/*

# 1) Copy and install at_bat exactly like you do locally
RUN git clone http://www.github.com/oneping-1/at_bat
RUN cd at_bat \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -e .

RUN cd ..

# 2) Copy and install on_deck deps
COPY ./ ./on_deck/
RUN cd on_deck \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -e .

# 3) Default: run the server (module form is a bit cleaner)
CMD ["python", "-m", "on_deck.on_deck_server"]
