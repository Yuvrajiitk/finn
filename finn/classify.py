"""Announcement classifier. Rules first (free, deterministic, explainable); an LLM is only worth calling on 'unclassified'.
Priority: 3 = look now, 2 = worth knowing, 1 = routine (collapsed in the UI)."""
import re
# Order matters: routine exclusions first, then specific before general. First match wins.
RULES = [
 ("routine",           1, r"esop|employee stock|certificate under|regulation 74|loss of share certificate|esg|business responsibility|auditor|secretarial compliance|trading window|reg\.? ?39|duplicate share"),
 ("results",           1, r"newspaper (advert|publication)|publication of (financial )?results"),
 ("results",           3, r"financial results|outcome of board meeting.*(result|quarter)|unaudited|audited results|quarter ended"),
 ("management_change", 3, r"resign|appointment of (chief|managing|whole[- ]time|ceo|cfo|director)|cessation|re-?designation|retire|change in (key )?management"),
 ("litigation",        3, r"show cause|penalty|fine imposed|sebi order|insolvency|nclt|court|tribunal|search and seizure|gst demand|tax demand"),
 ("M&A",               3, r"acqui|merger|amalgamation|demerger|joint venture|scheme of arrangement|stake in|subsidiary|divest"),
 ("fund_raise",        2, r"rights issue|qip|qualified institutions|preferential|buy-?back|commercial paper|non-convertible|ncd|fund ?raising"),
 ("credit_rating",     2, r"credit rating|crisil|icra|care ratings|india ratings|reaffirm|upgrade[d]? .*rating|downgrade"),
 ("pledging",          2, r"pledge|invocation|encumbrance"),
 ("insider_trading",   2, r"regulation 7\(2\)|insider|disclosure under sebi \(prohibition of insider"),
 ("dividend",          2, r"dividend|record date"),
 ("bonus_split",       2, r"bonus (issue|share)|sub-?division|stock split"),
 ("capex",             2, r"capex|capital expenditure|new plant|capacity expansion|greenfield|brownfield"),
 ("earnings_call",     1, r"earnings call|conference call|analyst.*meet|transcript|audio recording"),
 ("investor_meetings", 1, r"investor meet|schedule of (analyst|investor)|one-on-one"),
 ("postal_ballot",     1, r"postal ballot"),
 ("agm_egm",           1, r"annual general meeting|extra-?ordinary general meeting|\bagm\b|\begm\b|e-?voting"),
 ("press_release",     2, r"press release|order win|bagged|receives order|launch|partnership|clarification"),
]
def classify(desc, text=""):
    s = f"{desc} {text}".lower()
    for cat, pri, pat in RULES:
        if re.search(pat, s):
            return cat, pri
    return "unclassified", 1
