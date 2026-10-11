param()

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$localRoot = Join-Path $env:USERPROFILE 'AppData\Local\DCDS'
$mysqlVersion = '8.4.9'
$mongoVersion = '7.0.28'
$mysqlFolder = "mysql-$mysqlVersion-winx64"
$mongoFolder = "mongodb-win32-x86_64-windows-$mongoVersion"
$downloadRoot = Join-Path $localRoot 'downloads'
$mysqlArchive = Join-Path $downloadRoot "$mysqlFolder.zip"
$mongoArchive = Join-Path $downloadRoot "$mongoFolder.zip"
$mysqlInstall = Join-Path (Join-Path $localRoot 'servers') $mysqlFolder
$mongoInstall = Join-Path (Join-Path $localRoot 'servers') $mongoFolder
$mysqlExe = Join-Path $mysqlInstall 'bin\mysqld.exe'
$mongoExe = Join-Path $mongoInstall 'bin\mongod.exe'
$mysqlData = Join-Path $localRoot 'data\mysql'
$mongoData = Join-Path $localRoot 'data\mongo'
$envFile = Join-Path $projectRoot '.env'

if (Test-Path -LiteralPath $localRoot) {
    foreach ($dataPath in @($mysqlData, $mongoData)) {
        $dataEntries = Get-ChildItem -LiteralPath $dataPath -Force -ErrorAction SilentlyContinue
        if ($dataEntries) {
            throw "Refusing to initialize or replace non-empty database data under $dataPath. Back it up and inspect it first."
        }
    }
}
if (-not (Test-Path -LiteralPath $envFile)) {
    throw "Project .env is missing: $envFile"
}

$settings = @{}
foreach ($line in Get-Content -LiteralPath $envFile) {
    if ($line -match '^\s*([A-Z0-9_]+)=(.*)\s*$') { $settings[$Matches[1]] = $Matches[2] }
}
foreach ($name in @('MYSQL_ROOT_PASSWORD', 'MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DATABASE')) {
    if (-not $settings.ContainsKey($name) -or [string]::IsNullOrWhiteSpace($settings[$name])) {
        throw "Required setting $name is missing from project .env"
    }
}

New-Item -ItemType Directory -Path $localRoot -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $localRoot 'servers') -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $localRoot 'data\mysql') -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $localRoot 'data\mongo') -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $localRoot 'logs') -Force | Out-Null
New-Item -ItemType Directory -Path $downloadRoot -Force | Out-Null

$curl = Get-Command curl.exe -ErrorAction SilentlyContinue
if (-not $curl) { throw 'curl.exe is required to download the official database archives.' }
$mysqlUrl = "https://cdn.mysql.com/Downloads/MySQL-8.4/$mysqlFolder.zip"
$mongoUrl = "https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-$mongoVersion.zip"
if (-not (Test-Path -LiteralPath $mysqlExe)) {
    & $curl.Source --fail --location --retry 3 --output $mysqlArchive $mysqlUrl
    if ($LASTEXITCODE -ne 0) { throw 'MySQL archive download failed.' }
    Expand-Archive -LiteralPath $mysqlArchive -DestinationPath (Join-Path $localRoot 'servers')
    Remove-Item -LiteralPath $mysqlArchive -Force
}
if (-not (Test-Path -LiteralPath $mongoExe)) {
    & $curl.Source --fail --location --retry 3 --output $mongoArchive $mongoUrl
    if ($LASTEXITCODE -ne 0) { throw 'MongoDB archive download failed.' }
    Expand-Archive -LiteralPath $mongoArchive -DestinationPath (Join-Path $localRoot 'servers')
    Remove-Item -LiteralPath $mongoArchive -Force
}
Remove-Item -LiteralPath $downloadRoot -Force -ErrorAction SilentlyContinue
if (-not (Test-Path -LiteralPath $mysqlExe) -or -not (Test-Path -LiteralPath $mongoExe)) {
    throw 'The downloaded archives did not contain the expected server executables.'
}

$mysqlIni = @"
[mysqld]
basedir=$($mysqlInstall.Replace('\','/'))
datadir=$((Join-Path $localRoot 'data/mysql').Replace('\','/'))
port=3306
bind-address=127.0.0.1
mysqlx=0
log-error=$((Join-Path $localRoot 'logs/mysql.log').Replace('\','/'))
"@
Set-Content -LiteralPath (Join-Path $localRoot 'my.ini') -Value $mysqlIni -Encoding ascii

$mongoCfg = @"
storage:
  dbPath: "$((Join-Path $localRoot 'data/mongo').Replace('\','/'))"
systemLog:
  destination: file
  path: "$((Join-Path $localRoot 'logs/mongo.log').Replace('\','/'))"
  logAppend: true
net:
  bindIp: 127.0.0.1
  port: 27017
"@
Set-Content -LiteralPath (Join-Path $localRoot 'mongod.cfg') -Value $mongoCfg -Encoding ascii

# Initialize only the newly created, empty data directory. Set local credentials
# through a short-lived init file instead of placing passwords in process args.
$initializeLog = Join-Path $localRoot 'logs\mysql-initialize.log'
$initializeErrorLog = Join-Path $localRoot 'logs\mysql-initialize-stderr.log'
$initializeProcess = Start-Process -FilePath $mysqlExe -ArgumentList @(
    "--basedir=$mysqlInstall",
    "--datadir=$mysqlData",
    '--initialize-insecure',
    '--console'
) -NoNewWindow -Wait -PassThru -RedirectStandardOutput $initializeLog -RedirectStandardError $initializeErrorLog
if ($initializeProcess.ExitCode -ne 0) { throw 'MySQL data-directory initialization failed; see logs\mysql-initialize*.log.' }

$escapeSql = { param([string]$value) $value.Replace('\', '\\').Replace("'", "''") }
$rootPassword = & $escapeSql $settings['MYSQL_ROOT_PASSWORD']
$appUser = & $escapeSql $settings['MYSQL_USER']
$appPassword = & $escapeSql $settings['MYSQL_PASSWORD']
$database = & $escapeSql $settings['MYSQL_DATABASE']
$initSql = @"
ALTER USER 'root'@'localhost' IDENTIFIED BY '$rootPassword';
CREATE DATABASE IF NOT EXISTS ``$database``;
CREATE USER IF NOT EXISTS '$appUser'@'127.0.0.1' IDENTIFIED BY '$appPassword';
ALTER USER '$appUser'@'127.0.0.1' IDENTIFIED BY '$appPassword';
GRANT ALL PRIVILEGES ON ``$database``.* TO '$appUser'@'127.0.0.1';
"@
$initFile = Join-Path $localRoot 'mysql-first-start.sql'
[System.IO.File]::WriteAllText($initFile, $initSql, [System.Text.UTF8Encoding]::new($false))

$mysqlProcess = Start-Process -FilePath $mysqlExe -ArgumentList @(
    "--defaults-file=`"$(Join-Path $localRoot 'my.ini')`"",
    "--init-file=`"$initFile`""
) -WindowStyle Hidden -PassThru
$mongoProcess = Start-Process -FilePath $mongoExe -ArgumentList @(
    '--config', "`"$(Join-Path $localRoot 'mongod.cfg')`""
) -WindowStyle Hidden -PassThru

try {
    $mysqlReady = $false
    $mongoReady = $false
    for ($i = 0; $i -lt 80; $i++) {
        if (-not $mysqlReady) {
            $c = [System.Net.Sockets.TcpClient]::new()
            try { $t = $c.ConnectAsync('127.0.0.1', 3306); $mysqlReady = $t.Wait(500) -and $c.Connected } catch {} finally { $c.Dispose() }
        }
        if (-not $mongoReady) {
            $c = [System.Net.Sockets.TcpClient]::new()
            try { $t = $c.ConnectAsync('127.0.0.1', 27017); $mongoReady = $t.Wait(500) -and $c.Connected } catch {} finally { $c.Dispose() }
        }
        if ($mysqlReady -and $mongoReady) { break }
        Start-Sleep -Milliseconds 500
    }
    if (-not $mysqlReady -or -not $mongoReady) {
        throw 'Database startup timed out. Inspect the logs under the DCDS local data folder.'
    }
    Start-Sleep -Seconds 2
    Remove-Item -LiteralPath $initFile -Force -ErrorAction SilentlyContinue
    Write-Output "Portable MySQL $mysqlVersion and MongoDB $mongoVersion installed and started under $localRoot."
    Write-Output 'Both services are configured to listen on loopback only.'
} catch {
    Remove-Item -LiteralPath $initFile -Force -ErrorAction SilentlyContinue
    throw
}
