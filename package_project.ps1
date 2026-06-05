$sourcePath = "E:\portfolio-system"
$destinationPath = "E:\portfolio-system\profolio-ai-v1.0.zip"
$exclude = @(".git", "node_modules", ".next", ".venv", "venv", "__pycache__", ".DS_Store", "dist", "build", "coverage", "profolio-ai-v1.0.zip")

Write-Host "Packaging Profolio AI (excluding heavy directories)..."

$files = Get-ChildItem -Path $sourcePath -Recurse | Where-Object { 
    $path = $_.FullName
    $shouldExclude = $false
    foreach ($pat in $exclude) {
        if ($path -like "*\$pat" -or $path -like "*\$pat\*") {
            $shouldExclude = $true
            break
        }
    }
    -not $shouldExclude
}

if (Test-Path $destinationPath) { Remove-Item $destinationPath }

$files | Compress-Archive -DestinationPath $destinationPath -CompressionLevel Optimal

Write-Host "Successfully created archive at: $destinationPath"
