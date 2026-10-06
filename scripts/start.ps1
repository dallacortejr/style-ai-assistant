param(
    [switch]$Install,
    [switch]$Index,
    [string]$PythonPath = "python",
    [string]$PackageManagerPath = "pnpm"
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$projectPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
if ($Install) {
    if (-not (Test-Path -LiteralPath $projectPython)) {
        & $PythonPath -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Falha ao criar o ambiente Python.' }
    }
    & $projectPython -m pip install -r requirements-lock.txt
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao instalar o backend.' }
    & $PackageManagerPath install --frozen-lockfile
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao instalar a interface.' }
}
if (-not (Test-Path -LiteralPath $projectPython)) { throw 'Execute este script com -Install na primeira vez.' }
if (-not (Test-Path -LiteralPath '.env')) { Copy-Item -LiteralPath '.env.example' -Destination '.env' }
if ($Index) {
    & $projectPython -m backend.vector
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao indexar. Confirme que o Ollama e o modelo de embeddings estão disponíveis.' }
}
# API em loopback. O serviço permanece nesta janela; Ctrl+C encerra o processo.
$webProcess = Start-Process -FilePath $env:ComSpec -ArgumentList @('/c', "`"$PackageManagerPath`" run dev --host 127.0.0.1 --port 3000") -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru
Write-Host 'Interface: http://127.0.0.1:3000 | API e contratos: http://127.0.0.1:8000/docs'
Write-Host "Interface iniciada no processo $($webProcess.Id). Ctrl+C encerra a API; a interface pode ser encerrada pelo processo informado."
& $projectPython -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
