"""The PastForward mark, the one source for every icon: Then (gold) hops to Today (teal),
then the same gap again to an open Next ring. Used by build.py (SVG favicons) and og.py (PNG icons).
"""
DARK = {"bg": "#0F0D22", "t": "#E6B866", "n": "#74D6C8", "x": "#C9B6FF"}
LIGHT = {"bg": "#F7F5FB", "t": "#D4972B", "n": "#14A08F", "x": "#7A5CE6"}


def _css(p):
    return (f".bg{{fill:{p['bg']}}}.t{{fill:{p['t']}}}.n{{fill:{p['n']}}}.x{{stroke:{p['x']}}}"
            f".st{{stop-color:{p['t']}}}.sn{{stop-color:{p['n']}}}.sx{{stop-color:{p['x']}}}")


def svg(theme="dark", rx=14, k=1.0):
    """theme: 'dark', 'light', or 'auto' (follows the device's light or dark setting).
    rx rounds the corners (0 for platforms that mask the icon themselves); k scales the mark inside its safe zone."""
    if theme == "auto":
        style = _css(DARK) + "@media (prefers-color-scheme:light){" + _css(LIGHT) + "}"
    else:
        style = _css(LIGHT if theme == "light" else DARK)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        f"<style>{style}</style>"
        '<defs><linearGradient id="a" x1="12" x2="32" y1="0" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" class="st"/><stop offset="1" class="sn"/></linearGradient>'
        '<linearGradient id="b" x1="32" x2="52" y1="0" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" class="sn"/><stop offset="1" class="sx"/></linearGradient></defs>'
        f'<rect class="bg" width="64" height="64" rx="{rx}"/>'
        f'<g transform="translate(32 32) scale({k}) translate(-32 -32)">'
        '<path d="M12 35 Q22 13 32 35" fill="none" stroke="url(#a)" stroke-width="3.6" stroke-linecap="round"/>'
        '<path d="M32 35 Q42 13 52 35" fill="none" stroke="url(#b)" stroke-width="3.6" stroke-linecap="round"/>'
        '<circle class="t" cx="12" cy="37" r="6.2"/><circle class="n" cx="32" cy="37" r="6.2"/>'
        '<circle class="bg x" cx="52" cy="37" r="5.8" stroke-width="3.2"/>'
        "</g></svg>\n"
    )
