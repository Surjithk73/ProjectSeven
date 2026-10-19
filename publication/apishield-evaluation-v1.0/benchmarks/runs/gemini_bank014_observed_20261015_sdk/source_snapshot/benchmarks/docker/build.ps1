$ErrorActionPreference = 'Stop'
Set-Location 'C:/Users/surji/ProjectSeven'
docker pull python:3.13.3-slim-bookworm
if ($LASTEXITCODE -ne 0) { throw 'Base image pull failed' }
$baseImage = (docker image inspect python:3.13.3-slim-bookworm --format '{{index .RepoDigests 0}}').Trim()
if ($baseImage -notmatch '@sha256:[a-f0-9]{64}$') { throw 'No resolved base digest' }
docker build --build-arg "PYTHON_BASE=$baseImage" -f benchmarks/docker/Dockerfile -t apishield-eval:2026-10-15 .
if ($LASTEXITCODE -ne 0) { throw 'Image build failed' }
$builtImage = (docker image inspect apishield-eval:2026-10-15 --format '{{.Id}}').Trim()
@{ base_image=$baseImage; image_id=$builtImage; tag='apishield-eval:2026-10-15'; captured_at=(Get-Date).ToUniversalTime().ToString('o') } | ConvertTo-Json | Set-Content -Encoding utf8 benchmarks/provenance/container_image.json
Write-Output $builtImage
