"""Admin runner: cross-platform helper to run tests, migrations and start services.

Usage examples:
  python scripts/admin_run_tasks.py --tests
  python scripts/admin_run_tasks.py --migrate --start-api --start-ui

This script attempts to detect elevated privileges and warns if not running as admin/root.
"""
import os
import sys
import argparse
import subprocess
import shutil


def is_admin() -> bool:
    try:
        if os.name == 'nt':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception:
        return False


def run(cmd, check=True, capture=False):
    print(f"> {cmd}")
    res = subprocess.run(cmd, shell=True, check=False, capture_output=capture, text=True)
    if res.returncode != 0 and check:
        print(res.stdout or res.stderr)
        raise SystemExit(res.returncode)
    return res


def main():
    parser = argparse.ArgumentParser(description='Admin runner for MaestroIA / EcoOptima')
    parser.add_argument('--tests', action='store_true')
    parser.add_argument('--migrate', action='store_true')
    parser.add_argument('--start-api', action='store_true')
    parser.add_argument('--start-ui', action='store_true')
    parser.add_argument('--env', type=str, default='.env')
    args = parser.parse_args()

    if not is_admin():
        print('Aviso: o script não está sendo executado com privilégios de administrador/root.')
        print('Algumas operações (ex.: portas baixas, instalação global) podem falhar.')

    # Load .env if exists (do not expose secrets)
    env_path = os.path.abspath(args.env)
    if os.path.exists(env_path):
        print(f'Carregando .env de {env_path}')
        from dotenv import load_dotenv
        load_dotenv(env_path)

    # Run tests
    if args.tests:
        run('python -m unittest discover maestroia/tests')

    # Apply migrations if alembic available
    if args.migrate:
        if shutil.which('alembic'):
            run('alembic upgrade head')
        else:
            print('Alembic não encontrado no PATH — pular migrações.')

    # Start API
    if args.start_api:
        if shutil.which('uvicorn'):
            # Start uvicorn in background
            run('python -m uvicorn maestroia.api.routes:app --host 0.0.0.0 --port 8000 --reload', check=False)
        else:
            print('uvicorn não encontrado — instale dependências ou execute manualmente.')

    # Start UI (Streamlit)
    if args.start_ui:
        if shutil.which('streamlit'):
            run('python -m streamlit run ui_app.py', check=False)
        else:
            print('streamlit não encontrado — instale dependências ou execute manualmente.')

    print('admin_run_tasks concluído.')


if __name__ == '__main__':
    main()
