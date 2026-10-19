import matplotlib.pyplot as plt
import numpy as np
import os


def create_radar_chart(
    participant_scores,
    manager_scores,
    peer_scores,
    reportee_scores,
    cohort_scores
):

    # -----------------------------
    # Labels
    # -----------------------------
    labels = list(participant_scores.keys())
    participant_values = list(participant_scores.values())
    manager_values = list(manager_scores.values())
    peer_values = list(peer_scores.values())
    reportee_values = list(reportee_scores.values())
    cohort_values = list(cohort_scores.values())

    # -----------------------------
    # Angles
    # -----------------------------
    angles = np.linspace(
        0,
        2 * np.pi,
        len(labels),
        endpoint=False
    ).tolist()

    # Close polygons
    participant_values += participant_values[:1]
    manager_values += manager_values[:1]
    peer_values += peer_values[:1]
    reportee_values += reportee_values[:1]
    cohort_values += cohort_values[:1]
    angles += angles[:1]

    # -----------------------------
    # Figure
    # -----------------------------
    fig, ax = plt.subplots(
        figsize=(8, 8),
        subplot_kw=dict(polar=True)
    )

    ax.set_theta_offset(0)
    ax.set_theta_direction(1)

    # -----------------------------
    # Plot lines
    # -----------------------------
    ax.plot(
        angles,
        participant_values,
        linewidth=2,
        color="#1f77b4",
        label="Participant"
    )

    ax.plot(
        angles,
        manager_values,
        linewidth=2,
        color="#f4b400",
        label="Manager"
    )

    ax.plot(
        angles,
        peer_values,
        linewidth=2,
        color="#2ca02c",
        label="Peer"
    )

    ax.plot(
        angles,
        reportee_values,
        linewidth=2,
        color="gray",
        label="Direct Reportee"
    )

    ax.plot(
        angles,
        cohort_values,
        linewidth=2,
        linestyle=":",
        color="#4e79a7",
        label="Cohort Average"
    )

    # -----------------------------
    # Labels
    # -----------------------------
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=8)

    # -----------------------------
    # Scale
    # -----------------------------
    ax.set_ylim(0, 4)

    # Remove circular rings
    ax.yaxis.grid(False)

    # Keep spokes
    ax.xaxis.grid(True, color="lightgray")

    # Remove border
    ax.spines["polar"].set_visible(False)

    # Remove radial labels
    ax.set_yticks([])

    # -----------------------------
    # Scale numbers
    # -----------------------------
    spoke_angle = angles[2]
    offset = np.deg2rad(5)

    for r in [1, 2, 3, 4]:
        ax.text(
            spoke_angle - offset,
            r,
            str(r),
            fontsize=10,
            fontweight="bold",
            color="gray",
            ha="right",
            va="center",
            bbox=dict(
                facecolor="white",
                edgecolor="none",
                pad=0.15,
                alpha=0.9
            )
        )

    # -----------------------------
    # Legend
    # -----------------------------
    plt.legend(
        loc="lower center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=5,
        frameon=False
    )

    plt.tight_layout()

    os.makedirs("output", exist_ok=True)

    plt.savefig(
        "output/radar_chart.png",
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()


#-----------------------------------------------------


def create_self_vs_average_radar(
    participant_scores,
    average_scores
):
    import matplotlib.pyplot as plt
    import numpy as np
    import os

    labels = list(participant_scores.keys())

    participant_values = list(participant_scores.values())
    average_values = list(average_scores.values())

    angles = np.linspace(
        0,
        2 * np.pi,
        len(labels),
        endpoint=False
    ).tolist()

    participant_values += participant_values[:1]
    average_values += average_values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(
        figsize=(8, 8),
        subplot_kw=dict(polar=True)
    )

    ax.set_theta_offset(0)
    ax.set_theta_direction(1)

    ax.plot(
        angles,
        participant_values,
        linewidth=2,
        color="#1f77b4",
        label="Participant"
    )

    ax.plot(
        angles,
        average_values,
        linewidth=2,
        color="#f4b400",
        label="Average of Respondents"
    )

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=8)

    ax.set_ylim(0, 4)

    ax.yaxis.grid(False)
    ax.xaxis.grid(True, color="lightgray")

    ax.spines["polar"].set_visible(False)
    ax.set_yticks([])

    spoke_angle = angles[2]
    offset = np.deg2rad(5)

    for r in [1, 2, 3, 4]:
        ax.text(
            spoke_angle - offset,
            r,
            str(r),
            fontsize=10,
            fontweight="bold",
            color="gray",
            ha="right",
            va="center",
            bbox=dict(
                facecolor="white",
                edgecolor="none",
                pad=0.15,
                alpha=0.9
            )
        )

    plt.legend(
        loc="lower center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=2,
        frameon=False
    )

    plt.tight_layout(pad=1.0)

    os.makedirs("output", exist_ok=True)

    plt.savefig(
        "output/self_vs_average_radar.png",
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()