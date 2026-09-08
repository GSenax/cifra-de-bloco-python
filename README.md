# 🔐 Cifra de Bloco em Python

Implementação educacional de uma cifra de bloco desenvolvida em Python, com o objetivo de estudar conceitos fundamentais de criptografia e compreender, na prática, como diferentes etapas de transformação podem ser combinadas para realizar a encriptação e decriptação de dados.

> ⚠️ **Aviso:** este projeto possui finalidade exclusivamente acadêmica e educacional. A cifra implementada não deve ser utilizada para proteger informações sensíveis ou substituir algoritmos criptográficos padronizados e auditados.

## 📌 Sobre o projeto

O projeto implementa uma cifra de bloco que processa os dados em blocos de **32 bits (4 bytes)**.

O algoritmo utiliza múltiplas rodadas de transformação, combinando operações de substituição, permutação, rotações de bits e operações XOR.

A chave fornecida pelo usuário é convertida em um valor de 32 bits e utilizada para derivar uma subchave diferente para cada rodada.

## ⚙️ Funcionamento

O processo de encriptação de cada bloco é dividido em quatro rodadas.

Em cada rodada são realizadas duas etapas principais:

1. **Substituição**
2. **Permutação**

A saída de uma etapa é utilizada como entrada da próxima rodada, aumentando a mistura dos bits do bloco.

O processo de decriptação realiza as transformações de forma inversa e na ordem reversa das rodadas.

## 🔑 Geração das chaves

A chave fornecida como texto é convertida para um valor de 32 bits utilizando uma implementação do **FNV-1a**, seguida de operações adicionais de mistura dos bits.

A partir dessa chave são derivadas quatro subchaves, uma para cada rodada do algoritmo.

### Fluxo da chave

**Chave em texto → Conversão para 32 bits → Derivação das subchaves → 4 subchaves**

## 🔄 Estrutura das rodadas

Cada rodada realiza uma sequência de transformações sobre o bloco:

**Bloco de 32 bits → XOR com a subchave → Substituição pela S-Box → Permutação pela P-Box → Rotação de bits → XOR com subchave rotacionada → Próxima rodada**

O algoritmo possui **4 rodadas** de transformação.

## 🧩 Principais componentes

### S-Box

A S-Box realiza a substituição de cada **nibble (4 bits)** por outro valor.

Como o bloco possui 32 bits, cada bloco é dividido em 8 nibbles durante essa etapa.

A substituição altera os valores dos bits de forma não linear.

### P-Box

A P-Box realiza a permutação dos bits do bloco de 32 bits.

Essa operação redistribui os bits dentro do bloco, fazendo com que informações originalmente próximas sejam espalhadas por diferentes posições.

### Rotações de bits

O algoritmo utiliza rotações circulares para a esquerda e para a direita.

Essas operações são utilizadas durante a derivação das subchaves e nas transformações aplicadas aos blocos.

### XOR

A operação XOR é utilizada para combinar o bloco com as subchaves e também para realizar parte das transformações internas do algoritmo.

## 📁 Encriptação de arquivos

Além de processar blocos individualmente, o programa permite encriptar arquivos.

O arquivo é lido em modo binário e dividido em blocos de 4 bytes.

Caso o tamanho do arquivo não seja múltiplo de 4 bytes, é aplicado um padding para completar o último bloco.

**Arquivo original → Leitura dos bytes → Divisão em blocos de 4 bytes → Padding → Encriptação → Arquivo encriptado**

Na decriptação, o processo é realizado de forma inversa e o padding é removido ao final.

## 🖥️ Modos de utilização

O programa possui três modos principais:

### Encriptar um arquivo

    python cifra_blocos.py encriptar <entrada> <saida> <chave>

### Decriptar um arquivo

    python cifra_blocos.py decriptar <entrada> <saida> <chave>

### Demonstrar as rodadas

    python cifra_blocos.py demo <hex_bloco> <chave>

### Modo de demonstração

O modo `demo` permite observar o resultado intermediário de cada rodada.

Ele apresenta:

- Plaintext inicial;
- chave utilizada;
- subchaves derivadas;
- resultado após a substituição;
- resultado após a permutação;
- ciphertext final.

Esse modo foi desenvolvido para facilitar a análise do funcionamento interno da cifra e observar como o bloco é transformado a cada rodada.

## 🛠️ Tecnologias utilizadas

- **Python**
- `struct`
- Operações bit a bit
- Manipulação de arquivos binários

## 🧠 Conceitos praticados

- Criptografia por cifra de bloco
- Substituição e permutação
- S-Box e P-Box
- XOR
- Rotações de bits
- Derivação de subchaves
- Manipulação de dados binários
- Padding
- Leitura e escrita de arquivos
- Argumentos de linha de comando
- Estruturação de algoritmos criptográficos

## 🎓 Objetivo acadêmico

O objetivo principal do projeto foi compreender, de maneira prática, conceitos fundamentais utilizados em algoritmos de criptografia por blocos.

A implementação permite visualizar como diferentes operações sobre bits podem ser combinadas em várias rodadas para transformar a representação de um bloco de dados.

O projeto também possibilitou explorar operações de baixo nível sobre bits, manipulação de bytes e processamento de arquivos binários.

## 👤 Autor

**Gabriel Sena**

Estudante de Engenharia da Computação, com interesse em desenvolvimento de software, tecnologia e segurança da informação.
