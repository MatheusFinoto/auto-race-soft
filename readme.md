# Auto Race

Para gerar o build no PowerShell, a partir da raiz do projeto:

```powershell
rtk proxy .\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-build.txt
rtk proxy .\.venv\Scripts\python.exe build.py
```

O build inclui as imagens, o modelo de OCR local e o Tesseract usado no modo
`templates`. Na máquina que gera o build, o Tesseract deve estar instalado em
`C:\Program Files\Tesseract-OCR`;
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

## Ler somas com OCR local

O modo padrão, `local`, reconhece a expressão inteira, como `26+40`, usando um
modelo já treinado do [ddddocr](https://github.com/sml2h3/ddddocr). A inferência
roda na CPU do computador. Após instalar as dependências, o reconhecimento
funciona offline, mantém as imagens no computador e não tem cobrança por leitura.
O modelo acompanha o pacote Python e também é incluído no executável gerado.

Instale as dependências:

```powershell
rtk proxy .\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Para testar arquivos sem clicar ou digitar no jogo:

```powershell
rtk proxy .\.venv\Scripts\python.exe -m src.read_equation .\soma.png
rtk proxy .\.venv\Scripts\python.exe -m src.read_equation .\soma1.png .\soma2.png
rtk proxy .\.venv\Scripts\python.exe -m src.read_equation .\captura.png --crop 100 200 100 40
```

O recorte do comando usa `esquerda topo largura altura`, em pixels. Sem `--crop`,
o comando lê a imagem inteira. A saída tem o formato `soma.png: 26 + 40 = 66`.
O leitor reconhece os dois operandos, e o Python calcula a soma. Leituras
incompletas ou ambíguas são rejeitadas. Se uma imagem não puder ser lida, o
comando informa a falha e termina com código diferente de zero.

Para usar o modelo local na automação:

```powershell
$env:AUTO_RACE_READER = 'local'
$env:AUTO_RACE_EQUATION_REGION = '-174,-19,100,40'
rtk proxy .\.venv\Scripts\python.exe -m src.main
```

`AUTO_RACE_EQUATION_REGION` define `deslocamento_x,deslocamento_y,largura,altura`
em relação ao ponto de clique do diálogo usado pelo passo 3. O padrão é
`-174,-19,100,40`; ajuste essa região na tela real para conter a expressão inteira.
Uma leitura incompleta ou uma falha do modelo impede o envio da resposta.

O modo anterior permanece disponível como `templates`: ele lê os dois recortes
de números de 40×40 com as imagens de referência e usa Tesseract como fallback.
Para selecioná-lo, defina `$env:AUTO_RACE_READER = 'templates'` antes de executar.

Os testes automatizados verificam a validação das expressões e o fluxo de
execução. Casos sintéticos ajudam a verificar o leitor, mas não demonstram
precisão nas imagens originais enviadas na conversa: esses arquivos ainda
precisam ser testados. O posicionamento do recorte também exige verificação
na tela real do jogo.
