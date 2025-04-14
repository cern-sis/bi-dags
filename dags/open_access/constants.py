GOLD_OPEN_ACCESS_QUERY = "(affiliation:CERN or 595:'For annual report') and year:{year} not 980:ConferencePaper not 980:BookChapter not 595:'Not for annual report' and 540__f:'*' not 540__f:Bronze"
GREEN_OPEN_ACCESS_QUERY = "(affiliation:CERN or 595:'For annual report') and year:{year} not 980:ConferencePaper not 980:BookChapter not 595:'Not for annual report' not 540__f:'*' AND (8564_y:preprint OR 8564_y:”Accepted manuscript” OR 540__3:preprint)"
BRONZE_OPEN_ACCESS_QUERY = "(affiliation:CERN or 595:'For annual report') and year:{year} not 980:ConferencePaper not 980:BookChapter not 595:'Not for annual report' and 540__f:Bronze"
CLOSED_OPEN_ACCESS_QUERY = "(affiliation:CERN or 595:'For annual report') and year:{year} not 980:ConferencePaper not 980:BookChapter not 595:'Not for annual report' not 540__f:'*' NOT (8564_y:preprint OR 8564_y:”Accepted manuscript” OR 540__3:preprint)"


SCOAP3_QUERY = "(affiliation:CERN or 595:'For annual report') and year:{year} not 980:ConferencePaper not 980:BookChapter not 595:'Not for annual report' and 540__f:SCOAP3"
CERN_READ_AND_PUBLISH_QUERY = "(affiliation:CERN or 595:'For annual report') and year:{year} not 980:ConferencePaper not 980:BookChapter not 595:'Not for annual report' and 540__f:'CERN-RP'"
CERN_INDIVIDUAL_APCS_QUERY = "(affiliation:CERN or 595:'For annual report') and year:{year} not 980:ConferencePaper not 980:BookChapter not 595:'Not for annual report' and 540__f:'CERN-APC'"
OTHER_QUERY = "(affiliation:CERN or 595:'For annual report') and year:{year} not 980:ConferencePaper not 980:BookChapter not 595:'Not for annual report' and 540__f:'Other'"
OTHER_COLLECTIVE_MODELS_QUERY = "(affiliation:CERN or 595:'For annual report') and year:{year} not 980:ConferencePaper not 980:BookChapter not 595:'Not for annual report' and 540__f:Collective"

