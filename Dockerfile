FROM ubuntu:22.04

# Instalacja zależności systemowych
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    openssl \
    putty-tools \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Ustawienie katalogu roboczego
WORKDIR /app

# Kopiowanie plików aplikacji
# Kopiujemy wszystkie pliki z bieżącego katalogu
COPY . .

# Instalacja zależności Pythona
RUN pip3 install --no-cache-dir -r requirements.txt

# Ekspozycja portu
EXPOSE 5000

# Uruchomienie aplikacji
CMD ["python3", "app.py"] 