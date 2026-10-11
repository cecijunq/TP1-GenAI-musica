# TP1 — Geração de canções de ninar com algoritmo genético

Cecília Junqueira Vieira Machado Pereira - matrícula: 2022094888

Este projeto gera melodias no estilo de canções de ninar usando um algoritmo genético. As melodias usam a escala pentatônica de Dó maior, compasso 4/4 e a forma AABA, repetida duas vezes (32 compassos). A melhor melodia de cada execução é exportada em MIDI, junto com um gráfico da evolução da *fitness*.

## Estrutura

```
.
├── tp1.py        # genótipo, fitness e algoritmo genético (ponto de entrada)
├── saida.py      # exportação do MIDI e geração do gráfico
├── README.md
├── requirements.txt
└── resultados/   # criada automaticamente com as saídas
```

## Instalação

Requisitos: Python 3.8 ou superior.

```bash
# (opcional) criar um ambiente virtual
python -m venv venv
source venv/bin/activate

# instalar as dependências
pip install requirements.txt
```

## Execução

Para executar com os parâmetros padrão:

```bash
python tp1.py
```

### Parâmetros

| Parâmetro  | Descrição                                        | Padrão                |
|------------|--------------------------------------------------|-----------------------|
| `--seed`   | Semente aleatória (garante reprodutibilidade)    | sorteada              |
| `--pop`    | Tamanho da população                             | 20                    |
| `--epocas` | Número de gerações                               | 200                   |
| `--taxa`   | Taxa de mutação por gene                         | 0.05                  |
| `--bpm`    | Andamento do MIDI exportado                      | 80                    |
| `--saida`  | Pasta onde os resultados são salvos              | `resultados`          |

Exemplo:

```bash
python tp1.py --seed 4 --taxa 0.03 --epocas 200 --pop 20
```

Se `--seed` não for informada, uma semente é sorteada e mostrada no terminal. Anote esse valor para conseguir repetir a execução.

### Saídas

Cada execução mostra no terminal:
- a semente utilizada;
- a *fitness* final do melhor indivíduo e o valor de cada critério (movimento, cadência, ritmo, variedade e contraste);
- os genes das frases A e B.

Além disso, salva dois arquivos na pasta de saída:
- `cantiga_seed<S>_taxa<T>.mid`: a melodia gerada (cerca de 96 s a 80 bpm);
- `cantiga_seed<S>_taxa<T>_fitness.png`: o gráfico da melhor *fitness* e da *fitness* média por geração.

## Reprodução dos resultados

Os experimentos do relatório usam população 20, 200 gerações e 80 bpm, que são os valores padrão. Para reproduzi-los:

```bash
python tp1.py --seed 4 --taxa 0.03
python tp1.py --seed 9 --taxa 0.05
python tp1.py --seed 7 --taxa 0.05
python tp1.py --seed 9 --taxa 0.1
python tp1.py --seed 4 --taxa 0.15
python tp1.py --seed 8 --taxa 0.2
```

Resultados esperados (*fitness* do melhor indivíduo na última geração):

| Semente | Mutação | Melhor | Média da população |
|---------|---------|--------|--------------------|
| 4       | 0.03    | 0.973  | 0.928              |
| 4       | 0.15    | 0.927  | 0.733              |
| 7       | 0.05    | 0.945  | 0.850              |
| 8       | 0.20    | 0.944  | 0.753              |
| 9       | 0.05    | 0.958  | 0.888              |
| 9       | 0.10    | 0.911  | 0.783              |

A semente é definida uma única vez, antes da criação da população inicial. Por isso, cada comando gera sempre a mesma melodia. Os resultados podem variar se o código, a ordem das chamadas aleatórias ou a versão do Python forem alterados.

## Como ouvir os arquivos MIDI

Os arquivos `.mid` podem ser abertos em qualquer reprodutor ou editor de partituras. No desenvolvimento do projeto, utilizei o programa GarageBand, que já vem instalado nos dispositivos Apple.