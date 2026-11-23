# Instala en este PC todo lo rescatado de Emerge FM para que lo usen TODAS las sesiones de Claude Code.
# Uso: descomprime el zip, entra a la carpeta y haz clic derecho en este archivo -> "Ejecutar con PowerShell".
#
# Que hace:
#  1. Copia logos, dossier, Viaje sin Rumbo y el rescate de "claude code" a  %USERPROFILE%\.claude\emerge-fm\
#  2. Instala la skill nota-estilo-bbcl en  %USERPROFILE%\.claude\skills\  (disponible en todas las sesiones)
#  3. Agrega el contexto de Emerge FM a  %USERPROFILE%\.claude\CLAUDE.md  (lo leen todas las sesiones)
#  4. Agrega a la memoria del proyecto "claude code" SOLO las notas que falten (nunca reemplaza las que ya existen)
# Antes de cambiar algo que ya existe, deja un respaldo al lado.

$ErrorActionPreference = "Stop"
$paquete = Join-Path $PSScriptRoot "paquete"
$claude  = Join-Path $env:USERPROFILE ".claude"
$fecha   = Get-Date -Format yyyyMMdd-HHmmss
New-Item -ItemType Directory -Force -Path $claude | Out-Null

# 1. Archivos de Emerge FM
$destEmerge = Join-Path $claude "emerge-fm"
if (Test-Path $destEmerge) { Rename-Item $destEmerge "emerge-fm.respaldo-$fecha" }
Copy-Item -Recurse (Join-Path $paquete "emerge-fm") $destEmerge
Write-Host "1/4  Archivos copiados a $destEmerge"

# 2. Skill
$skills = Join-Path $claude "skills"
New-Item -ItemType Directory -Force -Path $skills | Out-Null
$destSkill = Join-Path $skills "nota-estilo-bbcl"
if (Test-Path $destSkill) { Rename-Item $destSkill "nota-estilo-bbcl.respaldo-$fecha" }
Copy-Item -Recurse (Join-Path $paquete "skills\nota-estilo-bbcl") $destSkill
Write-Host "2/4  Skill instalada en $destSkill"

# 3. CLAUDE.md personal
$destMd = Join-Path $claude "CLAUDE.md"
$marca  = "# Contexto: Farid y Radio Emerge FM 105.5"
$nuevo  = Get-Content -Raw -Encoding UTF8 (Join-Path $paquete "CLAUDE.md")
if (Test-Path $destMd) {
    $actual = Get-Content -Raw -Encoding UTF8 $destMd
    Copy-Item $destMd "$destMd.respaldo-$fecha"
    if ($actual -like "*$marca*") {
        $previo = $actual.Substring(0, $actual.IndexOf($marca)).TrimEnd()
        $texto = if ($previo) { "$previo`r`n`r`n$nuevo" } else { $nuevo }
        Set-Content -Encoding UTF8 -Path $destMd -Value $texto
        Write-Host "3/4  Contexto de Emerge FM actualizado en $destMd"
    } else {
        Add-Content -Encoding UTF8 -Path $destMd -Value "`r`n`r`n$nuevo"
        Write-Host "3/4  Contexto agregado al final de $destMd"
    }
} else {
    Set-Content -Encoding UTF8 -Path $destMd -Value $nuevo
    Write-Host "3/4  Contexto instalado en $destMd"
}

# 4. Memoria del proyecto "claude code": solo agrega las que falten
$mem = Join-Path $claude "projects\C--Users-farid-Desktop-claude-code\memory"
New-Item -ItemType Directory -Force -Path $mem | Out-Null
$agregadas = 0
Get-ChildItem (Join-Path $paquete "emerge-fm\rescate-claude-code\memoria") -Filter *.md | Where-Object { $_.Name -ne "MEMORY.md" } | ForEach-Object {
    $d = Join-Path $mem $_.Name
    if (-not (Test-Path $d)) { Copy-Item $_.FullName $d; $agregadas++ }
}
Write-Host "4/4  Memoria: $agregadas notas agregadas (las existentes no se tocaron)"
Write-Host ""
Write-Host "Listo. Las sesiones NUEVAS de Claude Code en este PC ya tienen el contexto, los logos y la skill."
Read-Host "Presiona Enter para cerrar"
