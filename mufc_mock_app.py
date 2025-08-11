
import os, re, requests, datetime
import feedparser, streamlit as st
from dateutil import parser as dtp

st.set_page_config(page_title="Man United – 5 temaer (Demo/Live)", layout="wide")
st.title("Manchester United · 5 temaer")

API = os.getenv("FOOTBALL_DATA_API_KEY")
HEAD = {"X-Auth-Token": API} if API else {}

def _short(t, n=180): return (t[:n] + "…") if t and len(t)>n else t
def google_news_rss(q, lang="da"):
    from urllib.parse import quote_plus
    return f"https://news.google.com/rss/search?q={quote_plus(q)}&hl={lang}&gl=DK&ceid=DK:{lang.upper()}"

def fetch_rss(url, limit=8):
    try:
        d = feedparser.parse(url)
    except Exception as e:
        return [{"error": f"RSS-fejl: {e}"}]
    out=[]
    for e in d.entries[:60]:
        title=e.get("title","")
        sumr=re.sub("<.*?>","",e.get("summary","") or "")
        when=(e.get("published") or e.get("updated") or "")
        try: when=dtp.parse(when).strftime("%Y-%m-%d %H:%M")
        except Exception: when=None
        out.append({"title":title,"summary":_short(sumr,220),"link":e.get("link",""),"when":when})
        if len(out)>=limit: break
    return out

def mock_kampprogram():
    base = datetime.datetime.now() + datetime.timedelta(days=2)
    return [
        {"Dato/tid": (base + datetime.timedelta(days=i*3)).strftime("%Y-%m-%d %H:%M"),
         "Turnering": "Premier League" if i%2==0 else "UEFA Europa League",
         "Kamp": f"Manchester United vs Modstander {i+1}"}
        for i in range(8)
    ]

def mock_resultater():
    base = datetime.datetime.now() - datetime.timedelta(days=2)
    return [
        {"Dato": (base - datetime.timedelta(days=i*4)).strftime("%Y-%m-%d"),
         "Turnering": "Premier League" if i%2==0 else "FA Cup",
         "Resultat": f"Manchester United {2+i}-{1+i%2} Modstander {i+1}"}
        for i in range(8)
    ]

def mock_stilling():
    rows = []
    for pos, team, pts in [(1,"Arsenal",86),(2,"Manchester City",84),(3,"Liverpool",80),(4,"Aston Villa",68),
                           (5,"Manchester United",66),(6,"Tottenham",64),(7,"Newcastle",60),(8,"Chelsea",58)]:
        rows.append({"Pos": pos, "Hold": team, "K": 38 if pos<5 else 37, "MF": 60+pos, "MM": 30+pos, "P": pts})
    return rows

@st.cache_data(ttl=900)
def nyheder(): return fetch_rss(google_news_rss("Manchester United","da"),limit=8)

@st.cache_data(ttl=900)
def rygter():  return fetch_rss(google_news_rss("Manchester United transfer OR rygter","da"),limit=8)

@st.cache_data(ttl=900)
def kampprogram(team_id=66, days_ahead=30, limit=10):
    url=f"https://api.football-data.org/v4/teams/{team_id}/matches?status=SCHEDULED&dateTo={(datetime.date.today()+datetime.timedelta(days=days_ahead)).isoformat()}"
    r=requests.get(url,headers=HEAD,timeout=15); r.raise_for_status()
    data=r.json(); out=[]
    for m in data.get("matches",[])[:limit]:
        out.append({"Dato/tid": dtp.parse(m["utcDate"]).strftime("%Y-%m-%d %H:%M"),
                    "Turnering": m["competition"]["name"],
                    "Kamp": f'{m["homeTeam"]["name"]} vs {m["awayTeam"]["name"]}'})
    return out

@st.cache_data(ttl=900)
def resultater(team_id=66, days_back=30, limit=10):
    url=f"https://api.football-data.org/v4/teams/{team_id}/matches?status=FINISHED&dateFrom={(datetime.date.today()-datetime.timedelta(days=days_back)).isoformat()}"
    r=requests.get(url,headers=HEAD,timeout=15); r.raise_for_status()
    data=r.json(); out=[]
    for m in data.get("matches",[])[:limit]:
        ft=m.get("score",{}).get("fullTime",{})
        out.append({"Dato": dtp.parse(m["utcDate"]).strftime("%Y-%m-%d"),
                    "Turnering": m["competition"]["name"],
                    "Resultat": f'{m["homeTeam"]["name"]} {ft.get("home","?")}-{ft.get("away","?")} {m["awayTeam"]["name"]}'})
    return out

@st.cache_data(ttl=900)
def stilling_pl(competition_id=2021, limit=20):
    url=f"https://api.football-data.org/v4/competitions/{competition_id}/standings"
    r=requests.get(url,headers=HEAD,timeout=15); r.raise_for_status()
    data=r.json(); rows=[]
    table=(data.get("standings") or [{}])[0].get("table",[])
    for row in table[:limit]:
        rows.append({"Pos": row["position"], "Hold": row["team"]["name"],
                     "K": row["playedGames"], "MF": row["goalsFor"],
                     "MM": row["goalsAgainst"], "P": row["points"]})
    return rows

# --- Sidebar toggles ---
st.sidebar.header("Indstillinger")
demo_default = not bool(API)
use_demo = st.sidebar.toggle("Demo mode (mock data)", value=demo_default,
                             help="Slå til, hvis du ikke har API-nøgle. Nyheder/rygter virker altid via RSS.")
lang = st.sidebar.selectbox("Sprog for nyheder/rygter", ["da","en","de","es"], index=0)

@st.cache_data(ttl=900)
def nyheder_lang(lang): 
    return fetch_rss(google_news_rss("Manchester United",lang),limit=8)
@st.cache_data(ttl=900)
def rygter_lang(lang):  
    return fetch_rss(google_news_rss("Manchester United transfer OR rumors OR rygter",lang),limit=8)

tabs = st.tabs(["🗞️ Nyheder","🕵️‍♂️ Rygter","📅 Kampprogram","✅ Seneste resultater","📊 PL-stilling"])

with tabs[0]:
    items = nyheder_lang(lang)
    if not items:
        st.info("Ingen nyheder lige nu.")
    for it in items:
        st.markdown(f"""**{it.get("title","(ingen titel)")}**  
{it.get("summary","")}  
[Link]({it.get("link","#")}) · {it.get("when","")}""")
        st.divider()

with tabs[1]:
    items = rygter_lang(lang)
    if not items:
        st.info("Ingen rygter lige nu.")
    for it in items:
        st.markdown(f"""**{it.get("title","(ingen titel)")}**  
{it.get("summary","")}  
[Link]({it.get("link","#")}) · {it.get("when","")}""")
        st.divider()

with tabs[2]:
    if use_demo:
        st.caption("Viser demo-kampprogram (mock). Sæt FOOTBALL_DATA_API_KEY for live data.")
        st.table(mock_kampprogram())
    else:
        try:
            st.table(kampprogram())
        except Exception as e:
            st.error(f"Kunne ikke hente kampprogram: {e}")
            st.caption("Tip: slå Demo mode til i venstre side.")

with tabs[3]:
    if use_demo:
        st.caption("Viser demo-resultater (mock).")
        st.table(mock_resultater())
    else:
        try:
            st.table(resultater())
        except Exception as e:
            st.error(f"Kunne ikke hente resultater: {e}")
            st.caption("Tip: slå Demo mode til i venstre side.")

with tabs[4]:
    if use_demo:
        st.caption("Viser demo-PL-stilling (mock).")
        st.table(mock_stilling())
    else:
        try:
            st.table(stilling_pl())
        except Exception as e:
            st.error(f"Kunne ikke hente PL-stilling: {e}")
            st.caption("Tip: slå Demo mode til i venstre side.")
