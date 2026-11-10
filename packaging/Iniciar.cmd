@echo off
setlocal DisableDelayedExpansion
set "AUTO_RACE_LAUNCHER_APP=%~dp0app"
set AUTO_RACE_LAUNCHER_ARGS=%*
powershell.exe -NoProfile -Command "$ErrorActionPreference='Stop'; try { $app=(Resolve-Path -LiteralPath $env:AUTO_RACE_LAUNCHER_APP -ErrorAction Stop).ProviderPath; $files=@(Get-ChildItem -LiteralPath $app -Filter '*.exe' -File -ErrorAction Stop); if ($files.Count -ne 1) { throw 'A pasta app deve conter exatamente um executavel.' }; if ($files[0].DirectoryName -ne $app) { throw 'Caminho do executavel invalido.' }; $name=[guid]::NewGuid().ToString('N')+'.exe'; $target=Join-Path -Path $app -ChildPath $name; Rename-Item -LiteralPath $files[0].FullName -NewName $name -ErrorAction Stop; $info=New-Object System.Diagnostics.ProcessStartInfo; $info.FileName=$target; $info.Arguments=$env:AUTO_RACE_LAUNCHER_ARGS; $info.WorkingDirectory=$app; $info.UseShellExecute=$false; $process=[System.Diagnostics.Process]::Start($info); $process.WaitForExit(); exit $process.ExitCode } catch { [Console]::Error.WriteLine('Nao foi possivel iniciar. Feche a instancia atual se o arquivo estiver em uso. '+$_.Exception.Message); exit 2 }"
exit /b %errorlevel%
