$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    $steps = @(
        @{ tool='pdflatex'; args=@('--disable-installer','-interaction=nonstopmode','-halt-on-error','main.tex'); log='build_1_pdflatex.txt' },
        @{ tool='bibtex'; args=@('--disable-installer','main'); log='build_2_bibtex.txt' },
        @{ tool='pdflatex'; args=@('--disable-installer','-interaction=nonstopmode','-halt-on-error','main.tex'); log='build_3_pdflatex.txt' },
        @{ tool='pdflatex'; args=@('--disable-installer','-interaction=nonstopmode','-halt-on-error','main.tex'); log='build_4_pdflatex.txt' }
    )
    $records = @()
    foreach ($step in $steps) {
        & $step.tool @($step.args) *> $step.log
        $code = $LASTEXITCODE
        $records += @{command=($step.tool + ' ' + ($step.args -join ' ')); exit_code=$code; log=$step.log}
        $records | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath 'build_status.json' -Encoding utf8
        if ($code -ne 0) { throw ('Build failed: ' + $step.log) }
    }
    Write-Output 'PDF build completed; all four command exit codes are zero.'
} finally {
    Pop-Location
}
