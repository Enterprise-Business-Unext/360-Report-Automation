import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import textwrap


SHORT_LABELS = {}

def create_module_chart(
    title,
    questions,
    participant,
    manager,
    peer,
    reportee
):

    # -----------------------------
    # Figure Creation
    # -----------------------------

    x = np.arange(len(questions))
    width = 0.2

    plt.figure(figsize=(14,8))

    # -----------------------------
    # Draw Bars
    # -----------------------------
    bars1 = plt.bar(
        x - 1.5 * width,
        participant,
        width,
        label="Participant",
        color="#4F81BD"
    )

    bars2 = plt.bar(
        x - 0.5 * width,
        manager,
        width,
        label="Manager",
        color="#F79646"
    )

    bars3 = plt.bar(
        x + 0.5 * width,
        peer,
        width,
        label="Peer",
        color="#A5A5A5"
    )

    bars4 = plt.bar(
        x + 1.5 * width,
        reportee,
        width,
        label="Direct Reportee",
        color="#FFC000"
    )

    plt.ylim(0, 5.0)


    wrapped_questions = [
        SHORT_LABELS.get(q, "\n".join(textwrap.wrap(q, width=20)))
        for q in questions
    ]


    plt.xticks(
        x,
        wrapped_questions,
        fontsize=17,
        fontweight="bold"
    )

    plt.grid(axis="y", linestyle="--", alpha=0.3)

    plt.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.35),
        ncol=4,
        frameon=False,
        fontsize=22,
        handlelength=2,
        handletextpad=0.5
    )
    
    # -----------------------------
    # Value Labels
    # -----------------------------
    for bars in [bars1, bars2, bars3, bars4]:

        for bar in bars:

            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.08,
                f"{bar.get_height():.2f}",
                ha="center",
                fontsize=17,
                fontweight="bold",
                rotation=90
            )

    # -----------------------------
    # Layout
    # -----------------------------
    
    plt.subplots_adjust(left=0.05,
    right=0.98,
    top=0.93,
    bottom=0.34)

    # -----------------------------
    # Save
    # -----------------------------
    os.makedirs("output/module_charts", exist_ok=True)
    plt.savefig(
        f"output/module_charts/{title.replace(' ', '_')}.png",
        dpi=150,
        bbox_inches="tight",
        pad_inches=0.05
    )

    plt.close()

    