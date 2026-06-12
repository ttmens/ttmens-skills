# Install ttmens-skills — default: Core + All platforms (40 skills)
param(
    [string[]]$Target = @("All"),
    [string[]]$Profile = @(),
    [string]$Project = "",
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
foreach ($p in $Profile) { $argsList += "--profile"; $argsList += $p }
if ($NativeOnly) { $argsList += "--native-only" }
if ($BorrowedOnly) { $argsList += "--borrowed-only" }
if ($DryRun) { $argsList += "--dry-run" }
if ($Project) { $argsList += "--project"; $argsList += $Project }

& $py.Source @argsList
