import random
import svgwrite


def render(data, theme, width=600, height=200):
    """
    Render Matrix-style digital rain visualization for contributions.

    Args:
        data (dict): Contribution data.
        theme (dict): Theme colors.
        width (int): SVG width.
        height (int): SVG height.

    Returns:
        str: SVG string.
    """

    dwg = svgwrite.Drawing(size=(width, height))

    # Background
    dwg.add(
        dwg.rect(
            insert=(0, 0),
            size=(width, height),
            fill=theme.get("bg_color", "#000000")
        )
    )

    contributions = data.get("contributions", [])

    cols = min(len(contributions), 60)
    col_width = width / cols if cols else 10

    for i, contrib in enumerate(contributions[:cols]):

        count = contrib.get("count", 0)

        if count <= 0:
            continue

        x = i * col_width + col_width / 2

        char = random.choice(["0", "1"])

        intensity = min(1, count / 10)

        text = dwg.text(
            char,
            insert=(x, 0),
            fill=theme.get("icon_color", "#00ff41"),
            font_size=12 + intensity * 6,
            font_family="monospace",
            text_anchor="middle",
            opacity=0.9
        )

        # random fall duration
        dur = f"{random.uniform(3,7)}s"

        text.add(
            dwg.animate(
                attributeName="y",
                from_="-10",
                to=str(height + 10),
                dur=dur,
                repeatCount="indefinite"
            )
        )

        dwg.add(text)

    return dwg.tostring()