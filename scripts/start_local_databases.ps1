param(
    [ValidateSet('Start', 'Status')]
    [string]$Action = 'Start'
)

$ErrorActionPreference = 'Stop'
$localRoot = Join-Path $env:LOCALAPPDATA 'DCDS'
$mysqlExe = Join-Path $localRoot 'servers\mysql-8.4.9-winx64\bin\mysqld.exe'
$mysqlConfig = Join-Path $localRoot 'my.ini'
$mongoExe = Join-Path $localRoot 'servers\mongodb-win32-x86_64-windows-7.0.28\bin\mongod.exe'
$mongoConfig = Join-Path $localRoot 'mongod.cfg'

function Test-LocalPort([int]$Port) {
    $client = [System.Net.Sockets.TcpClient]::new()
    try {
        $task = $client.ConnectAsync('127.0.0.1', $Port)
        return $task.Wait(1000) -and $client.Connected
    } catch {
        return $false
    } finally {
        $client.Dispose()
    }
}

function Wait-LocalPort([int]$Port) {
    for ($attempt = 0; $attempt -lt 40; $attempt++) {
        if (Test-LocalPort $Port) { return $true }
        Start-Sleep -Milliseconds 250
    }
    return $false
}

if ($Action -eq 'Start') {
    if (-not (Test-LocalPort 3306)) {
        if (-not (Test-Path -LiteralPath $mysqlExe) -or -not (Test-Path -LiteralPath $mysqlConfig)) {
            throw "MySQL local installation is missing under $localRoot"
        }
        Start-Process -FilePath $mysqlExe -ArgumentList @("--defaults-file=`"$mysqlConfig`"") -WindowStyle Hidden | Out-Null
    }
    if (-not (Test-LocalPort 27017)) {
        if (-not (Test-Path -LiteralPath $mongoExe) -or -not (Test-Path -LiteralPath $mongoConfig)) {
            throw "MongoDB local installation is missing under $localRoot"
        }
        Start-Process -FilePath $mongoExe -ArgumentList @('--config', "`"$mongoConfig`"") -WindowStyle Hidden | Out-Null
    }
}

if (-not (Wait-LocalPort 3306)) {
    throw "MySQL is not accepting local connections on port 3306. Check $localRoot\logs\mysql.log"
}
if (-not (Wait-LocalPort 27017)) {
    throw "MongoDB is not accepting local connections on port 27017. Check $localRoot\logs\mongo.log"
}

Write-Output 'MySQL: 127.0.0.1:3306 ready'
Write-Output 'MongoDB: 127.0.0.1:27017 ready'
