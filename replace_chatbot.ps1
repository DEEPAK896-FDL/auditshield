$file    = 'd:\Projects\AUDITSHIELD\audits\templates\audits\landing.html'
$jsFile  = 'd:\Projects\AUDITSHIELD\new_chatbot.js'
$lines   = Get-Content $file -Encoding UTF8

# ── Find the chatbot <script> block (second script block, after line 1800) ──
$cbStart = -1
$cbEnd   = -1

for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($cbStart -eq -1 -and $lines[$i].Trim() -eq '<script>' -and $i -gt 1800) {
        $cbStart = $i
    }
    if ($cbStart -ne -1 -and $cbEnd -eq -1 -and $i -gt $cbStart -and $lines[$i].Trim() -eq '</script>') {
        $cbEnd = $i
        break
    }
}

Write-Host "Chatbot script block: line $($cbStart+1) to line $($cbEnd+1)"

# ── Read the pure JS (no <script> tags) and wrap it ──
$jsContent = Get-Content $jsFile -Raw -Encoding UTF8

$wrapped  = [System.Collections.Generic.List[string]]::new()
[void]$wrapped.Add('<script>')
foreach ($l in $jsContent.Split("`n")) { [void]$wrapped.Add($l.TrimEnd("`r")) }
[void]$wrapped.Add('</script>')

# ── Build final file: before + wrapped JS + after ──
$before = $lines[0..($cbStart - 1)]
$after  = $lines[($cbEnd + 1)..($lines.Count - 1)]

$newLines = [System.Collections.Generic.List[string]]::new()
foreach ($l in $before)   { [void]$newLines.Add($l) }
foreach ($l in $wrapped)  { [void]$newLines.Add($l) }
foreach ($l in $after)    { [void]$newLines.Add($l) }

Set-Content -Path $file -Value $newLines -Encoding UTF8
Write-Host "Done. File now has $($newLines.Count) lines."

# ── Sanity checks ──
$opens  = ($newLines | Where-Object { $_.Trim() -eq '<script>'  }).Count
$closes = ($newLines | Where-Object { $_.Trim() -eq '</script>' }).Count
Write-Host "Script tags -- open: $opens   close: $closes   (expected: 2 each)"

$last3 = $newLines[($newLines.Count - 3)..($newLines.Count - 1)]
Write-Host "Last 3 lines:"
$last3 | ForEach-Object { Write-Host "  [$_]" }
