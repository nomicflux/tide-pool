"""The sea's weathers: the relationships each one gives words, and the words that bind them."""

WEATHER = {
    "calm": ("dreams of", "shelters", "remembers", "becomes", "waits beneath"),
    "storm": ("shatters", "crashes into", "tears through", "calls out for"),
    "fog": ("almost remembers", "loses sight of", "haunts", "mistakes itself for"),
    "ice": ("freezes beside", "holds", "keeps still beside", "glazes over"),
}
BRIDGE_WORDS = {word for bridges in WEATHER.values() for bridge in bridges
                for word in bridge.split()} | {"and", "listens"}


def choices():
    names = list(WEATHER)
    return f"{', '.join(names[:-1])}, or {names[-1]}"
