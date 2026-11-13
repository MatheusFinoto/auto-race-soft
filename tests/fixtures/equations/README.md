Estas 40 imagens são amostras sintéticas, não os anexos originais do usuário.

Elas representam as expressões `26+40`, `62+2`, `23+46`, `78+43` e `29+31`, em
Times New Roman regular/negrito/itálico e Georgia, com versões limpas e ruidosas.
Foram renderizadas pelo Pillow em 90 × 36 pixels, tamanho de fonte 28, fundo 238
e texto 22 em escala de cinza. As versões com ruído receberam 110 pontos, duas
linhas de um pixel e uma moldura. Os nomes dos arquivos contêm os operandos
esperados.

O teste executa o modelo ONNX real na CPU, exige as cinco leituras em negrito com
ruído e pelo menos 29 leituras corretas no conjunto completo. Leituras incertas
podem retornar `None`; qualquer soma incorreta falha o teste. Esses resultados
não medem a precisão no jogo nem nas imagens originais.
