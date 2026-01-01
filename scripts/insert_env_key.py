#!/usr/bin/env python3
"""Pequeno utilitário para inserir a OPENAI_API_KEY no arquivo .env do repositório.

Comportamento:
- Faz backup de `.env` para `.env.bak.TIMESTAMP` se já existir.
- Se existir `.env.example`, preserva seu conteúdo e atualiza/insere `OPENAI_API_KEY`.
- Caso contrário, cria um `.env` mínimo com `ENVIRONMENT` e `OPENAI_API_KEY`.

Uso:
  python scripts/insert_env_key.py

Nota: este script não comita nada. O repositório já ignora `.env` via `.gitignore`.
"""
from pathlib import Path
import shutil
import time
import sys


def backup_file(path: Path):
    ts = time.strftime("%Y%m%d-%H%M%S")
    dest = path.with_name(path.name + f".bak.{ts}")
    shutil.copy2(path, dest)
    print(f"Backup criado: {dest}")


def read_lines(path: Path):
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []


def write_lines(path: Path, lines):
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Arquivo gravado: {path}")


def set_key_in_lines(lines, key, value):
    found = False
    out = []
    for ln in lines:
        if ln.strip().startswith(f"{key}="):
            out.append(f"{key}={value}")
            found = True
        else:
            out.append(ln)
    if not found:
        out.append(f"{key}={value}")
    return out


def main():
    repo_root = Path(__file__).resolve().parent.parent
    env_path = repo_root / ".env"
    env_example = repo_root / ".env.example"

    keys = [
        ("OPENAI_API_KEY", "Chave da OpenAI (sk-...)"),
        ("MERCADOPAGO_ACCESS_TOKEN", "Token Mercado Pago"),
        ("META_ACCESS_TOKEN", "Token Meta (Facebook/Instagram)"),
        ("GOOGLE_ADS_CLIENT_ID", "Google Ads Client ID"),
        ("GOOGLE_ADS_CLIENT_SECRET", "Google Ads Client Secret"),
    ]

    print("Inserir chaves no arquivo .env do projeto (pressione Enter para pular uma chave)")

    # Fazer backup se .env existir
    if env_path.exists():
        backup_file(env_path)

    # Carregar base de .env.example ou .env existente
    base_lines = read_lines(env_example) if env_example.exists() else read_lines(env_path)
    if not base_lines:
        base_lines = ["ENVIRONMENT=development"]

    current_lines = base_lines
    for key, desc in keys:
        value = input(f"{desc} [{key}]: ").strip()
        if value:
            current_lines = set_key_in_lines(current_lines, key, value)

    write_lines(env_path, current_lines)
    print("Pronto. Verifique o arquivo .env e mantenha-o seguro.")


if __name__ == "__main__":
    main()
