param([string]$PackageManagerPath = 'pnpm')
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
& $PackageManagerPath exec tsc --noEmit
if ($LASTEXITCODE -ne 0) { throw 'TypeScript falhou.' }
& $PackageManagerPath run lint
if ($LASTEXITCODE -ne 0) { throw 'Lint falhou.' }
& $PackageManagerPath run build
if ($LASTEXITCODE -ne 0) { throw 'Build falhou.' }
& '.\.venv\Scripts\python.exe' -m pytest tests -q
if ($LASTEXITCODE -ne 0) { throw 'Testes do backend falharam.' }
& '.\.venv\Scripts\python.exe' -m evaluation.retrieval
if ($LASTEXITCODE -ne 0) { throw 'Avaliação da recuperação falhou.' }
