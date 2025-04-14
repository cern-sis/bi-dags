CLOSED_ACCESS = (
    r"not+540__a:'CC+BY'+not+540__a:'CC-BY'+" + r"not+540__f:Bronze+not+540__3:preprint"
)
BRONZE_ACCESS = r"540__f:'Bronze'"
GREEN_ACCESS = r""
GOLD_ACCESS = r""

CERN_READ_AND_PUBLISH = r"540__f:'CERN-RP"
CERN_INDIVIDUAL_APCS = r"540__f:'CERN-APC'"
SCOAP3 = r"540__f:'SCOAP3'"
OTHER = r"540__f:'Other'"
OTHER_COLLECTIVE_MODELS = r"540__f:'Collective'"

GOLD_OPEN_ACCESS_QUERY = "(affiliation:CERN or 595:'For annual report') and year:{year} not 980:ConferencePaper not 980:BookChapter not 595:'Not for annual report' and 540__f:'*' not 540__f:Bronze"
GREEN_OPEN_ACCESS_QUERY = "(affiliation:CERN or 595:'For annual report') and year:{year} not 980:ConferencePaper not 980:BookChapter not 595:'Not for annual report' not 540__f:'*' AND (8564_y:preprint OR 8564_y:”Accepted manuscript” OR 540__3:preprint)"
BRONZE_OPEN_ACCESS_QUERY = "(affiliation:CERN or 595:'For annual report') and year:{year} not 980:ConferencePaper not 980:BookChapter not 595:'Not for annual report' and 540__f:Bronze"
CLOSED_OPEN_ACCESS_QUERY = "(affiliation:CERN or 595:'For annual report') and year:{year} not 980:ConferencePaper not 980:BookChapter not 595:'Not for annual report' not 540__f:'*' NOT (8564_y:preprint OR 8564_y:”Accepted manuscript” OR 540__3:preprint)"
