# Install ttmens-skills — default: Core + debate + All platforms (37 core skills)
param(
    [string[]]$Target = @("All"),
    [string[]]$Profile = @("debate"),
    [string]$Project = "",
    [string]$Platform = "",
    [string]$Scenario = "",
    [string]$Stage = "",
    [switch]$Lite,
    [switch]$NativeOnly,
    [switch]$BorrowedOnly,
    [switch]$DryRun,
    [switch]$Core
)

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command python3 -ErrorAction SilentlyContinue }
if (-not $py) { throw "Python not found" }

$argsList = @("$Root\scripts\install_skills.py", "--core")

$normalized = $Target | ForEach-Object { $_.ToLower() }
if ($normalized -contains "all") { $argsList += "--all" }
else {
    if ($normalized -contains "cursor") { $argsList += "--cursor" }
    if ($normalized -contains "hermes") { $argsList += "--hermes" }
    if ($normalized -contains "opencode") { $argsList += "--opencode" }
}
foreach ($p in $Profile) { if ($p) { $argsList += "--profile"; $argsList += $p } }
if ($Platform) { $argsList += "--platform"; $argsList += $Platform }
if ($Scenario) { $argsList += "--scenario"; $argsList += $Scenario }
if ($Lite) {
    $argsList += "--lite"
    if ($Stage) { $argsList += "--stage"; $argsList += $Stage }
}
if ($NativeOnly) { $argsList += "--native-only" }
if ($BorrowedOnly) { $argsList += "--borrowed-only" }
if ($DryRun) { $argsList += "--dry-run" }
if ($Project) { $argsList += "--project"; $argsList += $Project }

& $py.Source @argsList
if ($LASTEXITCODE -eq 0 -and -not $DryRun) {
    Write-Host ""
    Write-Host "Post-install: run detect + validate:"
    & $py.Source "$Root\scripts\detect_agent_env.py" --json
    & $py.Source "$Root\scripts\validate_skills.py"
}
