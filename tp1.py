"""
TP1 - Algoritmo genético: genótipo e função de fitness
Restrição estilística: cantiga infantil / canção de ninar
  - melodia monofônica, pentatônica de Dó maior (Dó Ré Mi Sol Lá)
  - compasso 4/4, grade de semínimas
  - forma fixa AABA (repetida REPETICOES vezes)

GENÓTIPO: lista de 32 inteiros
  genes 0..15  -> frase A (4 compassos x 4 semínimas)
  genes 16..31 -> frase B (4 compassos x 4 semínimas)
  valor 0..9 -> grau da pentatônica (2 oitavas, 0 = Dó4, 5 = Dó5)
  valor -1   -> S: sustenta a nota anterior (cria notas longas)

FENÓTIPO: A A B A (x REPETICOES) -> 16 compassos por repetição
"""

import random

PENTA = [0, 2, 4, 7, 9]      # Dó Ré Mi Sol Lá (semitons acima de Dó)
N_GRAUS = 10                 # graus 0..9
S = -1                       # sustenta
TAM_FRASE = 16               # 4 compassos x 4 semínimas
TAM_GENOMA = 2 * TAM_FRASE
FORMA = "AABA"
REPETICOES = 2               # 2 x AABA = 32 compassos (~96 s a 80 bpm)
PROB_S = 0.25                # chance de um gene aleatório ser S

TAXA_MUTACAO = 0.05


# ============================ GENÓTIPO ============================
def gene_aleatorio():
    return S if random.random() < PROB_S else random.randrange(N_GRAUS)


def gerar_genotipo():
    g = [gene_aleatorio() for _ in range(TAM_GENOMA)]
    g[0] = random.randrange(N_GRAUS)          # música não pode começar com S
    g[TAM_FRASE] = random.randrange(N_GRAUS)  # frase B também não
    return g


def frases(gen):
    return {"A": gen[:TAM_FRASE], "B": gen[TAM_FRASE:]}


# ========================== DECODIFICAÇÃO ==========================
def grau_para_midi(grau):
    return 60 + 12 * (grau // 5) + PENTA[grau % 5]


def notas_da_frase(frase):
    """Frase (16 genes) -> lista de (grau, duração em semínimas)."""
    notas = []
    for g in frase:
        if g == S and notas:
            grau, dur = notas[-1]
            notas[-1] = (grau, dur + 1)
        elif g != S:
            notas.append((g, 1))
    return notas


def decodificar(gen):
    """Genótipo -> lista de eventos (midi, início, duração), em semínimas.
    Use esta lista para exportar o .mid (ex.: com pretty_midi)."""
    f = frases(gen)
    eventos, t = [], 0
    for _ in range(REPETICOES):
        for letra in FORMA:
            for grau, dur in notas_da_frase(f[letra]):
                eventos.append((grau_para_midi(grau), t, dur))
                t += dur
    return eventos


# ============================ FITNESS =============================
def _alvo(x, alvo, tol):
    """1.0 se x == alvo, caindo linearmente até 0 a uma distância tol."""
    return max(0.0, 1.0 - abs(x - alvo) / tol)


def c_movimento(notas):
    """Cantigas andam por graus vizinhos. Passo (1-2 graus) = 1 ponto,
    nota repetida = 0.5, salto de 3 graus = 0.25, salto maior = 0."""
    graus = [g for g, _ in notas]
    if len(graus) < 2:
        return 0.0
    pontos = {0: 0.5, 1: 1.0, 2: 1.0, 3: 0.25}
    ints = [abs(b - a) for a, b in zip(graus, graus[1:])]
    return sum(pontos.get(i, 0.0) for i in ints) / len(ints)


def c_cadencia(fA, fB):
    """Pergunta e resposta: B termina 'em suspenso' (Sol ou Ré),
    A termina 'resolvida' em Dó, com nota longa (>= 2 semínimas)."""
    grauA, durA = notas_da_frase(fA)[-1]
    grauB, _ = notas_da_frase(fB)[-1]
    fimA = 1.0 if grauA % 5 == 0 else 0.0
    longa = 1.0 if durA >= 2 else 0.0
    fimB = 1.0 if grauB % 5 in (1, 3) else 0.0
    inicioA = 1.0 if fA[0] % 5 == 0 else 0.0     # começa em Dó
    return 0.35 * fimA + 0.25 * longa + 0.25 * fimB + 0.15 * inicioA


def c_ritmo(frase):
    """Cerca de 25% de notas sustentadas e o 1º tempo de cada compasso
    sempre com ataque de nota (tempo forte marcado)."""
    frac_s = sum(1 for g in frase if g == S) / len(frase)
    tempo_forte = sum(1 for c in range(4) if frase[4 * c] != S) / 4
    return 0.5 * _alvo(frac_s, 0.25, 0.25) + 0.5 * tempo_forte


def c_variedade(frase):
    """Usar pelo menos 4 das 5 notas da escala, sem ficar batendo sempre na mesma."""
    graus = [g for g in frase if g != S]
    distintas = len({g % 5 for g in graus})
    mais_comum = max(graus.count(x) for x in set(graus)) / len(graus)
    return 0.6 * min(distintas / 4, 1.0) + 0.4 * _alvo(mais_comum, 0.25, 0.5)


def c_contraste(fA, fB):
    """A frase B fica, em média, cerca de 2 graus mais aguda que A (contraste da forma AABA)."""
    mA = sum(g for g in fA if g != S) / max(1, sum(1 for g in fA if g != S))
    mB = sum(g for g in fB if g != S) / max(1, sum(1 for g in fB if g != S))
    return _alvo(mB - mA, 2.0, 2.0)


PESOS = {"movimento": 0.30, "cadencia": 0.20, "ritmo": 0.20,
         "variedade": 0.15, "contraste": 0.15}


def fitness(gen, pesos=PESOS, detalhado=False):
    f = frases(gen)
    fA, fB = f["A"], f["B"]
    partes = {
        "movimento": (c_movimento(notas_da_frase(fA)) + c_movimento(notas_da_frase(fB))) / 2,
        "cadencia": c_cadencia(fA, fB),
        "ritmo": (c_ritmo(fA) + c_ritmo(fB)) / 2,
        "variedade": (c_variedade(fA) + c_variedade(fB)) / 2,
        "contraste": c_contraste(fA, fB),
    }
    total = sum(pesos[k] * partes[k] for k in pesos)
    return (total, partes) if detalhado else total

def gerar_populacao(n):
    populacao = []
    fit = []

    for _ in range(n):
        g = gerar_genotipo()
        populacao.append(g)
        #fit.append(fitness(g))   # só o número; detalhado=True não é necessário aqui

    return populacao

def roleta(populacao, _fitness):
    """Gira a roleta uma vez: cada indivíduo tem fatia proporcional à fitness."""
    total = sum(_fitness)
    r = random.uniform(0, total)          # ponto onde a "bolinha" para
    acumulado = 0
    for individuo, f in zip(populacao, _fitness):
        acumulado += f
        if acumulado >= r:
            return individuo
    return populacao[-1]                  # segurança contra arredondamento


def selecao(populacao, n_elite=3):
    _fitness = [fitness(ind) for ind in populacao]

    # elitismo: os n_elite melhores, copiados
    ordem = sorted(range(len(populacao)), key=lambda i: _fitness[i], reverse=True)
    elite = [populacao[i][:] for i in ordem[:n_elite]]

    # roleta: sorteia os pais que vão gerar o resto da população
    n_pais = len(populacao) - n_elite
    pool = [roleta(populacao, _fitness)[:] for _ in range(n_pais)]

    return elite, pool

def cruzamento(pool, n):
    nova_populacao = []
    i = 0

    while len(nova_populacao) < n:
        pai1 = pool[i % len(pool)]
        pai2 = pool[(i + 1) % len(pool)]
        corte = random.randrange(4, len(pai1), 4)      # um corte novo por par

        filho1 = pai1[:corte] + pai2[corte:]
        filho2 = pai2[:corte] + pai1[corte:]
        i += 2

        nova_populacao.append(filho1)
        if len(nova_populacao) < n:
            nova_populacao.append(filho2)

    return nova_populacao

def mutar_gene(gene, pos):
    """Muda um gene. 70% das vezes: sobe ou desce 1 grau (mudança suave).
    30% das vezes (ou se o gene for S): troca por um gene aleatório."""
    if random.random() < 0.7 and gene != S:
        novo = gene + random.choice([-1, 1])
        return max(0, min(N_GRAUS - 1, novo))      # não sai da faixa 0..9
    if pos in (0, TAM_FRASE):                      # início de frase nunca vira S
        return random.randrange(N_GRAUS)
    return gene_aleatorio()                        # pode virar nota ou S


def mutacao(populacao, taxa=TAXA_MUTACAO):
    nova = []
    for individuo in populacao:
        filho = individuo[:]                       # cópia: não altera o original
        for pos in range(len(filho)):
            if random.random() < taxa:
                filho[pos] = mutar_gene(filho[pos], pos)
        nova.append(filho)
    return nova

def genetico(populacao, epocas, n_elite=3, taxa_mut=TAXA_MUTACAO):
    historico = []                                   # (melhor, média) por geração
    for e in range(epocas):
        elite, pool = selecao(populacao, n_elite=n_elite)
        filhos = cruzamento(pool, len(populacao) - len(elite))
        filhos = mutacao(filhos, taxa_mut)
        populacao = elite + filhos

        fit = [fitness(g) for g in populacao]
        historico.append((max(fit), sum(fit) / len(fit)))

    melhor = max(populacao, key=fitness)
    return melhor, historico

if __name__ == "__main__":
    import argparse, os
    from saida import exportar_midi, plotar_historico

    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--pop", type=int, default=20)
    parser.add_argument("--epocas", type=int, default=200)
    parser.add_argument("--taxa", type=float, default=TAXA_MUTACAO)
    parser.add_argument("--bpm", type=int, default=80)
    parser.add_argument("--saida", default="resultados")
    args = parser.parse_args()

    seed = args.seed if args.seed is not None else random.randrange(1_000_000)
    random.seed(seed)            # UMA vez, antes de tudo
    print(f"Semente: {seed}")

    populacao_inicial = gerar_populacao(args.pop)
    melhor, historico = genetico(populacao_inicial, args.epocas, taxa_mut=args.taxa)
    total, partes = fitness(melhor, detalhado=True)
    print(f"Melhor final: {total:.3f}", {k: round(v, 2) for k, v in partes.items()})
    print("Frase A:", melhor[:TAM_FRASE])
    print("Frase B:", melhor[TAM_FRASE:])

    os.makedirs(args.saida, exist_ok=True)
    nome = f"cantiga_seed{seed}_taxa{args.taxa}"
    dur = exportar_midi(decodificar(melhor), os.path.join(args.saida, nome + ".mid"), bpm=args.bpm)
    plotar_historico(historico, os.path.join(args.saida, nome + "_fitness.png"),
                     titulo=f"Evolução da fitness (semente {seed}, mutação {args.taxa})")
    print(f"Salvo em {args.saida}/{nome}.mid ({dur:.0f} s) e {nome}_fitness.png")