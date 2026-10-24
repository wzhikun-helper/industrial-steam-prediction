$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    # Generated local cache, never committed. Preserve exact font files without
    # hardcoding the author's machine path in the manuscript.
    $paperFontDir = if ($env:STEAM_PAPER_FONT_DIR) { $env:STEAM_PAPER_FONT_DIR } elseif ($env:WINDIR) { Join-Path $env:WINDIR 'Fonts' } else { throw 'Set STEAM_PAPER_FONT_DIR to installed SimSun/Times font files.' }
    foreach ($fontFile in @('simsun.ttc','times.ttf','timesbd.ttf','timesi.ttf','timesbi.ttf')) {
        if (-not (Test-Path -LiteralPath (Join-Path $paperFontDir $fontFile))) { throw ('Missing font: '+$fontFile) }
    }
    $paperFontDir = (Resolve-Path -LiteralPath $paperFontDir).Path.Replace('\','/').TrimEnd('/')+'/'
    ('\newcommand{\systemfontdir}{'+$paperFontDir+'}') | Set-Content -LiteralPath 'local_font_paths.tex' -Encoding utf8
    $steps = @(
        @{ tool='xelatex'; args=@('--disable-installer','-interaction=nonstopmode','-halt-on-error','main.tex'); log='build_1_xelatex.txt' },
        @{ tool='bibtex'; args=@('--disable-installer','main'); log='build_2_bibtex.txt' },
        @{ tool='xelatex'; args=@('--disable-installer','-interaction=nonstopmode','-halt-on-error','main.tex'); log='build_3_xelatex.txt' },
        @{ tool='xelatex'; args=@('--disable-installer','-interaction=nonstopmode','-halt-on-error','main.tex'); log='build_4_xelatex.txt' }
    )
    $records = @()
    foreach ($step in $steps) {
        & $step.tool @($step.args) *> $step.log
        $code = $LASTEXITCODE
        $records += @{ command=($step.tool+' '+($step.args -join ' ')); exit_code=$code; log=$step.log }
        $records | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath 'build_status.json' -Encoding utf8
        if ($code -ne 0) { throw ('Build failed: '+$step.log) }
    }
    Write-Output 'Complete XeLaTeX/BibTeX build: four zero exit codes.'
} finally { Pop-Location }
