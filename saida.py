"""Funções auxiliares de saída: exportar .mid e plotar a evolução da fitness."""

import pretty_midi
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def exportar_midi(eventos, caminho, bpm=80, programa=0, velocidade=90):
    """eventos: lista de (nota_midi, início, duração), em semínimas
    (formato devolvido por decodificar). programa 0 = piano."""
    seg = 60.0 / bpm                                   # duração de 1 semínima em segundos
    pm = pretty_midi.PrettyMIDI(initial_tempo=bpm)
    inst = pretty_midi.Instrument(program=programa)
    for nota, inicio, dur in eventos:
        inst.notes.append(pretty_midi.Note(
            velocity=velocidade, pitch=nota,
            start=inicio * seg, end=(inicio + dur) * seg - 0.02))  # pequeno respiro entre notas
    pm.instruments.append(inst)
    pm.write(caminho)
    return pm.get_end_time()


def plotar_historico(historico, caminho, titulo="Evolução da fitness"):
    """historico: lista de (melhor, média) por geração."""
    melhor = [h[0] for h in historico]
    media = [h[1] for h in historico]
    geracoes = range(1, len(historico) + 1)

    fig, ax = plt.subplots(figsize=(6, 3.4), dpi=200)
    ax.plot(geracoes, melhor, color="#2a78d6", linewidth=2, label="Melhor")
    ax.plot(geracoes, media, color="#eb6834", linewidth=2, label="Média da população")

    # rótulos diretos no fim de cada linha
    ax.annotate(f"{melhor[-1]:.3f}", (len(melhor), melhor[-1]), xytext=(4, 0),
                textcoords="offset points", va="center", fontsize=8, color="#333333")
    ax.annotate(f"{media[-1]:.3f}", (len(media), media[-1]), xytext=(4, 0),
                textcoords="offset points", va="center", fontsize=8, color="#333333")

    ax.set_xlabel("Geração")
    ax.set_ylabel("Fitness")
    ax.set_ylim(0, 1)
    ax.set_title(titulo, fontsize=10, loc="left")
    ax.grid(axis="y", color="#e5e5e5", linewidth=0.8)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color("#999999")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(caminho)
    plt.close(fig)
