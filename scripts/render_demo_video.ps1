$ErrorActionPreference = 'Stop'

# Keep the credential in process memory only. Prefer the current shell's value,
# then fall back to the current Windows user's environment setting.
if (-not $env:ELEVENLABS_API_KEY) {
    $env:ELEVENLABS_API_KEY = [Environment]::GetEnvironmentVariable('ELEVENLABS_API_KEY', 'User')
}
if (-not $env:ELEVENLABS_API_KEY) {
    throw 'ELEVENLABS_API_KEY is unavailable to this PowerShell process. Set it in this session or the User environment, then rerun.'
}

python scripts/render_demo_video.py
exit $LASTEXITCODE
