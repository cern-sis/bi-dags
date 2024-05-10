def get_url(key, year):
    url = {
        "publications_total_count": r"http://cdsweb.cern.ch/search?wl=0&ln=en&cc=Published+"
        + r"Articles&sc=1&p=%28affiliation%3ACERN+or+595%3A%27For+annual+report%27%29+and+"
        + rf"year%3A{year}+not+980%3AConferencePaper+not+980%3ABookChapter+not+595%3A%27Not+"
        + r"for+annual+report%27&f=&action_search=Search&of=xm",
        "conference_proceedings_count": r"http://cdsweb.cern.ch/search?wl=0&ln=en&cc=Published+"
        + r"Articles&p=980%3AARTICLE+and+%28affiliation%3ACERN+or+595%3A%27For+annual+report%27%29+"
        + rf"and+year%3A{year}+and+980%3AConferencePaper+not+595%3A%27Not+for+annual+"
        + r"report%27&f=&action_search=Search&c=Published+Articles&c=&sf=author&so=a&rm=&rg=10&sc=1&of=xm",
        "non_journal_proceedings_count": r"https://cds.cern.ch/search?ln=en&p=affiliation%3ACERN+or+"
        + rf"260%3ACERN+and+260%3A{year}+and+%28980%3ABOOK+or+980%3APROCEEDINGS+or+690%3A%27YELLOW+REPORT%27+"
        + r"or+980%3ABookChapter+or+980%3AREPORT%29+not+595%3A%27Not+for+annual+report%27&action_search="
        + r"Search&op1=a&m1=a&p1=&f1=&c=CERN+Document+Server&sf=&so=d&rm=&rg=10&sc=1&of=xm",
    }
    return url[key]
