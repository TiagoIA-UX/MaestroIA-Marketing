<#
.SYNOPSIS
    Script para executar tarefas administrativas do projeto MaestroIA/EcoOptima.

.DESCRIPTION
    Solicita elevação (Admin) no Windows e executa uma série de passos úteis:
    - executar testes unitários
    - aplicar migrações (se Alembic presente)
    - iniciar a API (uvicorn) e a UI (streamlit) opcionalmente

.PARAMETER TestsOnly
    Executa apenas os testes.

.PARAMETER RunServer
    Inicia a API (`uvicorn maestroia.api.routes:app --port 8000`).

.PARAMETER RunUI
    Inicia a UI Streamlit (`streamlit run ui_app.py`).

.EXAMPLE
    .\admin_run_tasks.ps1 -TestsOnly
    .\admin_run_tasks.ps1 -RunServer -RunUI
#>

param(
    [switch]$TestsOnly,
    [switch]$RunServer,
    [switch]$RunUI
)

function Ensure-Admin {
    $current = [Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()
    if (-not $current.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Host "Elevando para privilégios administrativos..."
        Start-Process -FilePath pwsh -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -TestsOnly:$TestsOnly -RunServer:$RunServer -RunUI:$RunUI" -Verb RunAs
        exit
    }
}

Ensure-Admin

Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Definition)

Write-Host "Ambiente: $(Get-Location)"

if ($TestsOnly) {
    Write-Host "Executando testes unitários..."
    python -m unittest discover maestroia/tests
    exit $LASTEXITCODE
}

# Executar testes como verificação inicial
Write-Host "Executando testes unitários..."
python -m unittest discover maestroia/tests

# Aplicar migrações Alembic se existir
if (Test-Path "alembic.ini") {
    Write-Host "Aplicando migrações Alembic..."
    alembic upgrade head
} else {
    Write-Host "Alembic não encontrado — pulando migrações."
}

if ($RunServer) {
    Write-Host "Iniciando API (uvicorn) em segundo plano..."
    Start-Process -NoNewWindow -FilePath python -ArgumentList "-m uvicorn maestroia.api.routes:app --host 0.0.0.0 --port 8000 --reload"
}

if ($RunUI) {
    Write-Host "Iniciando UI Streamlit em segundo plano..."
    Start-Process -NoNewWindow -FilePath python -ArgumentList "-m streamlit run ui_app.py"
}

Write-Host "Tarefas administrativas concluídas."
