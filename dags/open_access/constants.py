CLOSED_ACCESS = (
    r"not+540__a:'CC+BY'+not+540__a:'CC-BY'+" + r"not+540__f:Bronze+not+540__3:preprint"
)
BRONZE_ACCESS = r"540__f:'Bronze'"
GREEN_ACCESS = (
    r"not+540__a:'CC+BY'+not+540__a:'CC-BY'+not+540__a:"
    + r"'arXiv+nonexclusive-distrib'+not+540__f:'Bronze'"
)
GOLD_ACCESS = r"540__3:'publication'+and+" + r"(540__a:'CC-BY'+OR++540__a:'CC+BY')"

CERN_READ_AND_PUBLISH = r"540__f:'CERN-RP"
CERN_INDIVIDUAL_APCS = r"540__f:'CERN-APC'"
SCOAP3 = r"540__f:'SCOAP3'"
OTHER = r"540__f:'Other'"
OTHER_COLLECTIVE_MODELS = r"540__f:'Collective'"
