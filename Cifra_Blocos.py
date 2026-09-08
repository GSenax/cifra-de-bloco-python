import sys
import struct

NUM_RODADAS = 4

# Constantes usadas pra misturar a chave em cada rodada, cada uma diferente
CONSTANTES_RODADA = [0x9E3779B9, 0x6C62272E, 0xC2B2AE35, 0x27D4EB2F]

# Tabela de substituição: cada nibble (4 bits) vira outro valor
# A ideia é quebrar padrões no bloco pra dificultar análise
SBOX = [0xE, 0x4, 0xD, 0x1, 0x2, 0xF, 0xB, 0x8,
        0x3, 0xA, 0x6, 0xC, 0x5, 0x9, 0x0, 0x7]

# S-Box ao contrário, usada pra desfazer a substituição na decriptação
SBOX_INV = [0] * 16
for _i, _v in enumerate(SBOX):
    SBOX_INV[_v] = _i

# Tabela de permutação: define pra onde cada bit vai dentro do bloco de 32 bits
# Isso faz com que bits de um byte se misturem com bits de outros bytes
PBOX = [
     1, 16,  5, 20,  9, 24, 13, 28,
     2, 17,  6, 21, 10, 25, 14, 29,
     3, 18,  7, 22, 11, 26, 15, 30,
     4, 19,  8, 23, 12, 27,  0, 31
]

# P-Box inversa pra desfazer a permutação na decriptação
PBOX_INV = [0] * 32
for _i, _v in enumerate(PBOX):
    PBOX_INV[_v] = _i


def rotacao_esquerda(valor, qtd, nbits=32):
    # Desloca os bits pra esquerda de forma circular (o que sai pela esquerda volta pela direita)
    qtd %= nbits
    mascara = (1 << nbits) - 1
    return ((valor << qtd) | (valor >> (nbits - qtd))) & mascara


def rotacao_direita(valor, qtd, nbits=32):
    qtd %= nbits
    mascara = (1 << nbits) - 1
    return ((valor >> qtd) | (valor << (nbits - qtd))) & mascara


def chave_string_para_32bits(chave_str):
    # Transforma a string da chave num número de 32 bits usando hash FNV-1a
    # Não usa nenhuma biblioteca, só XOR e multiplicação modular byte a byte
    MASCARA = 0xFFFFFFFF
    h = 0x811C9DC5
    for byte in chave_str.encode('utf-8'):
        h ^= byte
        h = (h * 0x01000193) & MASCARA
    # Mistura final pra distribuir melhor os bits
    h ^= (h >> 16)
    h = (h * 0x45D9F3B) & MASCARA
    h ^= (h >> 16)
    return h & MASCARA


def derivar_subchave(chave32, rodada):
    # Gera uma subchave diferente pra cada rodada a partir da chave principal
    # Se a chave mudar 1 bit, todas as subchaves mudam também
    MASCARA = 0xFFFFFFFF
    k = (chave32 ^ CONSTANTES_RODADA[rodada]) & MASCARA
    k = rotacao_esquerda(k, (rodada * 7 + 3) % 32)
    k = (k * 0x6D2B79F5 + rodada + 1) & MASCARA
    k ^= rotacao_esquerda(chave32, (rodada * 13 + 5) % 32)
    return k & MASCARA


def aplicar_substituicao(bloco32, subchave):
    # Primeiro mistura o bloco com a subchave via XOR pra tornar a substituição dependente da chave
    # Depois troca cada nibble (4 bits) pelo valor correspondente na S-Box
    misturado = bloco32 ^ subchave
    resultado = 0
    for i in range(8):  # 32 bits / 4 = 8 nibbles
        nibble = (misturado >> (i * 4)) & 0xF
        resultado |= (SBOX[nibble] << (i * 4))
    return resultado


def aplicar_substituicao_inversa(bloco32, subchave):
    # Desfaz a substituição: usa a S-Box inversa e depois XOR com a mesma subchave
    resultado = 0
    for i in range(8):
        nibble = (bloco32 >> (i * 4)) & 0xF
        resultado |= (SBOX_INV[nibble] << (i * 4))
    return resultado ^ subchave


def aplicar_permutacao(bloco32, subchave):
    # Passo 1: redistribui os bits do bloco conforme a P-Box
    resultado = 0
    for i in range(32):
        bit = (bloco32 >> PBOX[i]) & 1
        resultado |= (bit << i)
    # Passo 2: rotaciona o resultado por uma quantidade que depende da subchave
    resultado = rotacao_esquerda(resultado, subchave & 0x1F)
    # Passo 3: XOR final com a subchave rotacionada pra mais difusão
    resultado ^= rotacao_direita(subchave, 7)
    return resultado


def aplicar_permutacao_inversa(bloco32, subchave):
    # Desfaz os 3 passos da permutação na ordem inversa
    resultado = bloco32 ^ rotacao_direita(subchave, 7)
    resultado = rotacao_direita(resultado, subchave & 0x1F)
    bloco_orig = 0
    for i in range(32):
        bit = (resultado >> i) & 1
        bloco_orig |= (bit << PBOX[i])
    return bloco_orig


def encriptar_bloco(bloco32, subchaves):
    # Aplica as 4 rodadas de substituição + permutação no bloco
    b = bloco32
    for r in range(NUM_RODADAS):
        b = aplicar_substituicao(b, subchaves[r])
        b = aplicar_permutacao(b, subchaves[r])
    return b


def decriptar_bloco(bloco32, subchaves):
    # Desfaz as rodadas na ordem inversa: da rodada 4 até a 1
    # Em cada rodada, a permutação é desfeita antes da substituição
    b = bloco32
    for r in range(NUM_RODADAS - 1, -1, -1):
        b = aplicar_permutacao_inversa(b, subchaves[r])
        b = aplicar_substituicao_inversa(b, subchaves[r])
    return b


def encriptar_arquivo(caminho_entrada, caminho_saida, chave_str):
    chave32 = chave_string_para_32bits(chave_str)
    subchaves = [derivar_subchave(chave32, r) for r in range(NUM_RODADAS)]

    with open(caminho_entrada, 'rb') as fin:
        dados = fin.read()

    # Padding: completa o último bloco pra ter exatamente 4 bytes
    # O valor adicionado indica quantos bytes foram inseridos (padrão PKCS#7)
    padding = 4 - (len(dados) % 4)
    dados += bytes([padding] * padding)

    with open(caminho_saida, 'wb') as fout:
        for i in range(0, len(dados), 4):
            bloco = struct.unpack('>I', dados[i:i+4])[0]
            fout.write(struct.pack('>I', encriptar_bloco(bloco, subchaves)))


def decriptar_arquivo(caminho_entrada, caminho_saida, chave_str):
    chave32 = chave_string_para_32bits(chave_str)
    subchaves = [derivar_subchave(chave32, r) for r in range(NUM_RODADAS)]

    with open(caminho_entrada, 'rb') as fin:
        dados_cifrados = fin.read()

    blocos_plain = []
    for i in range(0, len(dados_cifrados), 4):
        bloco = struct.unpack('>I', dados_cifrados[i:i+4])[0]
        blocos_plain.append(struct.pack('>I', decriptar_bloco(bloco, subchaves)))

    dados_plain = b''.join(blocos_plain)

    # Remove o padding lendo o último byte, que diz quantos bytes foram adicionados
    padding = dados_plain[-1]
    if 1 <= padding <= 4:
        dados_plain = dados_plain[:-padding]

    with open(caminho_saida, 'wb') as fout:
        fout.write(dados_plain)


def demonstrar_rodadas(plaintext_hex, chave_str):
    # Mostra o resultado parcial após cada rodada, útil pra analisar o efeito avalanche
    bloco = int(plaintext_hex, 16)
    chave32 = chave_string_para_32bits(chave_str)
    subchaves = [derivar_subchave(chave32, r) for r in range(NUM_RODADAS)]

    print(f"Plaintext : {bloco:08X}")
    print(f"Chave     : '{chave_str}' -> {chave32:08X}")
    print(f"Subchaves derivadas:")
    for i, sk in enumerate(subchaves):
        print(f"  Rodada {i+1}: {sk:08X}")
    print()

    b = bloco
    for r in range(NUM_RODADAS):
        apos_sub = aplicar_substituicao(b, subchaves[r])
        apos_per = aplicar_permutacao(apos_sub, subchaves[r])
        print(f"Rodada {r+1}:")
        print(f"  Apos substituicao : {apos_sub:08X}")
        print(f"  Apos permutacao   : {apos_per:08X}")
        b = apos_per

    print(f"\nCiphertext final: {b:08X}")
    return b


def main():
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python cifra_blocos.py encriptar <entrada> <saida> <chave>")
        print("  python cifra_blocos.py decriptar <entrada> <saida> <chave>")
        print("  python cifra_blocos.py demo <hex_bloco> <chave>")
        sys.exit(1)

    modo = sys.argv[1].lower()

    if modo in ('encriptar', 'decriptar'):
        if len(sys.argv) != 5:
            print(f"Uso: python cifra_blocos.py {modo} <entrada> <saida> <chave>")
            sys.exit(1)
        _, _, entrada, saida, chave = sys.argv
        if modo == 'encriptar':
            encriptar_arquivo(entrada, saida, chave)
            print(f"Encriptado: '{entrada}' -> '{saida}'")
        else:
            decriptar_arquivo(entrada, saida, chave)
            print(f"Decriptado: '{entrada}' -> '{saida}'")

    elif modo == 'demo':
        if len(sys.argv) != 4:
            print("Uso: python cifra_blocos.py demo <hex_bloco> <chave>")
            sys.exit(1)
        demonstrar_rodadas(sys.argv[2], sys.argv[3])

    else:
        print(f"Modo desconhecido: '{modo}'")
        sys.exit(1)


if __name__ == '__main__':
    main()