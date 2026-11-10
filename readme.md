# Auto Race

Para gerar o build no PowerShell, a partir da raiz do projeto:

```powershell
rtk proxy .\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-build.txt
rtk proxy .\.venv\Scripts\python.exe build.py
```

O build inclui as imagens e o Tesseract usado como fallback. Na máquina que gera
o build, o Tesseract deve estar instalado em `C:\Program Files\Tesseract-OCR`;
para outro local, defina a variável de ambiente `TESSERACT_DIR`.

Abra `dist\AutoRusso\Iniciar.cmd` para iniciar. A cada abertura, o lançador
renomeia o executável da pasta `app` para um nome aleatório antes de executá-lo.
Mantenha o lançador e a pasta `app` juntos. Feche a execução anterior antes de
abrir novamente ou gerar outro build. Para distribuir, envie o arquivo
`dist\AutoRusso.zip` e extraia a pasta inteira antes de abrir o lançador.

Para verificar o pacote sem iniciar a automação do jogo:

```powershell
rtk proxy cmd /d /c dist\AutoRusso\Iniciar.cmd --check-build
```

Para executar pelo código-fonte:

```powershell
rtk proxy .\.venv\Scripts\python.exe -m src.main
```
