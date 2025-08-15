import streamlit as st
import pandas as pd
import os
import json

# ================== Sidebar (define ONCE) ==================
st.sidebar.subheader("🔐 LLM Settings (Gemini)")
gemini_key_input = st.sidebar.text_input(
    "Gemini API Key", type="password", help="Paste your Google AI Studio key", key="gemini_api_key_txt"
)
if gemini_key_input:
    os.environ["GOOGLE_API_KEY"] = gemini_key_input

# Let the model be configurable; default to a widely-available Gemini model.
# If you have access to a newer one (e.g., "gemini-2.0-flash" or "gemini-2.5-pro"), put it here.
model_name = st.sidebar.text_input(
    "Gemini model ID",
    value="gemini-2.0-flash",
    help="Examples: gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash",
    key="gemini_model_id_txt",
)

use_ai_explanations = st.sidebar.checkbox(
    "Use AI explanations", value=True, key="use_ai_explanations_cb"
)

st.sidebar.subheader("📋 Draft Strategy")
default_strategy = (
    "Prioritize elite RB/WR early; delay QB until value; fill starters first; "
    "use FLEX for best RB/WR/TE; break ties with higher projected points, then better rank."
)
user_strategy = st.sidebar.text_area(
    "Strategy the AI should follow", value=default_strategy, height=100, key="draft_strategy_txt"
)

# ================== Page config & Styles ==================
st.set_page_config(page_title="Fantasy Football AI Demo", layout="wide")
st.markdown("""
<style>
    .main { padding: 1rem; background-color: #0B162A; color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .header { text-align: center; background: #A71930; color: white; padding: 2rem; border-radius: 15px; margin-bottom: 2rem; border: 2px solid #FFD100; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; }
    .header h1 { font-size: 2.8rem; margin-bottom: 0.5rem; }
    .draft-status { background: #021C35; color: #FFD100; padding: 1rem; border-radius: 10px; text-align: center; margin-bottom: 1rem; border: 1px solid #A71930; font-weight: 600; }
    .player-suggestion { background: #001F47; color: white; border-radius: 12px; padding: 1rem; margin-bottom: 1rem; border-left: 5px solid #A71930; border: 1px solid #444; font-weight: 600; box-shadow: 0 2px 6px rgba(167, 25, 48, 0.5); }
    .stat-box { background: #021C35; color: #FFD100; padding: 0.5rem; border-radius: 6px; text-align: center; margin: 0.2rem; border: 1px solid #A71930; font-weight: 700; }
    .stat-box div:nth-child(2) { color: white !important; font-weight: 600; font-size: 0.8em; }
    .roster-slot { background: #021C35; padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid #444; display: flex; justify-content: space-between; align-items: center; border: 1px solid #444; color: #FFD100; font-weight: 700; }
    .roster-slot.filled { border-left-color: #A71930; background: #001F47; border: 1px solid #A71930; color: white; }
    .roster-slot span[style*="color: #000000"] { color: #FFD100 !important; }
    .confidence-bar { height: 6px; background: #444; border-radius: 3px; margin-top: 8px; overflow: hidden; box-shadow: inset 0 1px 3px rgba(255,255,255,0.3); }
    .confidence-fill { height: 100%; background: #A71930; border-radius: 3px; box-shadow: 0 0 8px #A71930; }
    div[data-testid="stDataFrame"] > div > div > div > div { scrollbar-width: thin; scrollbar-color: #A71930 #021C35; }
    div[data-testid="stDataFrame"] > div > div > div > div::-webkit-scrollbar { width: 8px; height: 8px; }
    div[data-testid="stDataFrame"] > div > div > div > div::-webkit-scrollbar-track { background: #021C35; }
    div[data-testid="stDataFrame"] > div > div > div > div::-webkit-scrollbar-thumb { background-color: #A71930; border-radius: 10px; border: 2px solid #021C35; }
</style>
""", unsafe_allow_html=True)

# ================== Draft Helpers ==================
def serialize_roster(roster_dict):
    """Compact, LLM‑friendly roster summary + counts."""
    slots = []
    for slot, p in roster_dict.items():
        slots.append({
            "slot": slot,
            "filled": p is not None,
            "name": (p or {}).get("name") if p else None,
            "position": (p or {}).get("position") if p else None,
            "team": (p or {}).get("team") if p else None,
        })
    # counts
    pos_counts = {"QB":0,"RB":0,"WR":0,"TE":0,"DST":0,"K":0}
    for p in roster_dict.values():
        if not p: 
            continue
        pos = p.get("position","")
        if pos in pos_counts: pos_counts[pos] += 1
        if pos in ["D/ST","DST"]: 
            pos_counts["DST"] += 1
    summary = {
        "slots": slots,
        "counts": pos_counts,
        "open_slots": [s["slot"] for s in slots if not s["filled"]],
        "flex_rules": "FLEX accepts RB/WR/TE only; max one QB, TE, DST, and K.",
        "caps": {"QB":1,"RB":2,"WR":2,"TE":1,"FLEX":1,"DST":1,"K":1}
    }
    return summary

def filter_draftable(df, roster_dict, limit=25):
    """Only keep players that can be placed in main or FLEX right now."""
    draftable_rows = []
    for _, r in df.iterrows():
        status = can_draft_player(r, roster_dict)
        if status in ("main","flex"):
            draftable_rows.append(r)
        if len(draftable_rows) >= limit:
            break
    return pd.DataFrame(draftable_rows) if draftable_rows else df.head(0)

def compact_available(df, limit=15):
    cols = ["name","position","team","projected_points","rank"]
    if not all(c in df.columns for c in cols): 
        return []
    small = df[cols].head(limit).copy()
    small["projected_points"] = small["projected_points"].astype(float)
    small["rank"] = small["rank"].astype(int)
    return small.to_dict("records")
def can_draft_player(player, roster):
    pos = player['position']
    if pos == 'QB':
        return 'main' if roster['QB'] is None else 'full'
    elif pos == 'RB':
        if roster['RB1'] is None or roster['RB2'] is None: return 'main'
        return 'flex' if roster['FLEX'] is None else 'full'
    elif pos == 'WR':
        if roster['WR1'] is None or roster['WR2'] is None: return 'main'
        return 'flex' if roster['FLEX'] is None else 'full'
    elif pos == 'TE':
        if roster['TE'] is None: return 'main'
        return 'flex' if roster['FLEX'] is None else 'full'
    elif pos in ['D/ST', 'DST']:
        return 'main' if roster['D/ST'] is None else 'full'
    elif pos == 'K':
        return 'main' if roster['K'] is None else 'full'
    return 'main'

def build_roster(drafted_players):
    roster = {'QB': None, 'RB1': None, 'RB2': None, 'WR1': None, 'WR2': None, 'TE': None, 'FLEX': None, 'D/ST': None, 'K': None}
    flex_pool = []
    if not drafted_players: return roster
    for player in drafted_players:
        if not isinstance(player, dict): continue
        pos = player.get('position', '')
        if pos == 'QB' and not roster['QB']: roster['QB'] = player
        elif pos == 'RB':
            if not roster['RB1']: roster['RB1'] = player
            elif not roster['RB2']: roster['RB2'] = player
            else: flex_pool.append(player)
        elif pos == 'WR':
            if not roster['WR1']: roster['WR1'] = player
            elif not roster['WR2']: roster['WR2'] = player
            else: flex_pool.append(player)
        elif pos == 'TE' and not roster['TE']: roster['TE'] = player
        elif pos in ['D/ST', 'DST'] and not roster['D/ST']: roster['D/ST'] = player
        elif pos == 'K' and not roster['K']: roster['K'] = player
        else:
            if pos in ['RB','WR','TE']: flex_pool.append(player)
    if not roster['FLEX'] and flex_pool:
        for p in flex_pool:
            if p.get('position','') in ['RB','WR','TE']:
                roster['FLEX'] = p
                break
    return roster

# ================== Session ==================
if 'current_pick' not in st.session_state: st.session_state.current_pick = 27
if 'drafted_players' not in st.session_state: st.session_state.drafted_players = []

# ================== Data ==================
@st.cache_data
def load_player_rankings():
    try:
        df = pd.read_csv('fantasy_2025_predictions_updated.csv')
        df = df.rename(columns={
            'Player':'name','Team':'team','Pos':'position',
            'Predicted_FPTS/G':'projected_points','Rank':'rank'
        }).sort_values(by='rank')
        return df
    except Exception as e:
        st.error(f"Error loading fantasy_2025_predictions_updated.csv: {e}")
        return None

player_rankings = load_player_rankings()
if player_rankings is None: st.stop()

drafted_names = [p['name'] for p in st.session_state.drafted_players if isinstance(p, dict) and 'name' in p]
available_players = player_rankings[~player_rankings['name'].isin(drafted_names)]

# ================== Gemini helpers ==================
@st.cache_data(show_spinner=False)
def gemini_reason(player_dict, roster_snapshot, pick_number, model_id, api_key):
    """
    1–2 sentence why FOR THIS PLAYER, aware of user's roster.
    """
    if not api_key:
        return "Top ranked player based on 2025 projections."
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_id)

        roster_summary = serialize_roster(roster_snapshot)
        prompt = f"""
You are a concise fantasy draft assistant.
Explain—in 1–2 sentences—why this player is a good fit NOW, given the user's current roster, caps, and FLEX rules.
Avoid fluff. Mention roster fit if relevant.

Current pick: {pick_number}

My roster (JSON):
{json.dumps(roster_summary, ensure_ascii=False)}

Candidate player (JSON):
{json.dumps(player_dict, ensure_ascii=False)}

Return only the explanation sentence(s).
"""
        resp = model.generate_content(prompt)
        return (resp.text or "").strip() or "Top ranked player based on 2025 projections."
    except Exception:
        return "Top ranked player based on 2025 projections."


@st.cache_data(show_spinner=False)
def gemini_pick_and_why(available_small, roster_snapshot, pick_number, strategy, model_id, api_key):
    """
    Choose ONE draftable player from available_small based on full roster context + strategy.
    Returns dict {name, position, team, reason}.
    """
    if not api_key or not available_small:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_id)

        roster_summary = serialize_roster(roster_snapshot)
        prompt = f"""
You are a fantasy football draft assistant.
Choose ONE player to draft NEXT from the provided list.
HARD rules:
- Respect roster caps: 1 QB, 2 RB, 2 WR, 1 TE, 1 FLEX (RB/WR/TE), 1 DST, 1 K.
- Only suggest players that can be placed in an open main slot or FLEX right now.
- Prioritize filling open starters before bench.
- Follow the user's draft strategy after roster needs.

Current pick: {pick_number}
User strategy: {strategy}

My roster (JSON):
{json.dumps(roster_summary, ensure_ascii=False)}

Available (JSON array of players):
{json.dumps(available_small, ensure_ascii=False)}

Return STRICT JSON with keys: name, position, team, reason.
No extra text.
"""
        resp = model.generate_content(prompt)
        text = (resp.text or "").strip()
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start:end+1])
    except Exception:
        pass
    return None

def roster_needs_summary(roster_dict):
    order = ["QB","RB1","RB2","WR1","WR2","TE","FLEX","D/ST","K"]
    return [slot for slot in order if roster_dict.get(slot) is None]

def compact_available(df, limit=15):
    cols = ["name","position","team","projected_points","rank"]
    if not all(c in df.columns for c in cols): return []
    small = df[cols].head(limit).copy()
    small["projected_points"] = small["projected_points"].astype(float)
    small["rank"] = small["rank"].astype(int)
    return small.to_dict("records")

# ================== Header ==================
st.markdown("""
<div class="header">
    <h1>Fantasy Football Player Prediction Aid</h1>
    <p>AI-Powered Draft Assistant & Season Manager</p>
</div>
""", unsafe_allow_html=True)

# ================== Layout ==================
col1, col2, col3 = st.columns([1,2,1])

# ---------- Left: Draft controls ----------
with col1:
    st.subheader("Draft Settings")
    current_pick = st.session_state.current_pick
    draft_position = ((current_pick - 1) % 5) + 1
    current_round = ((current_pick - 1) // 5) + 1

    st.markdown(f"""
    <div class="stat-box" style="margin-bottom: 1rem;">
        <div style="font-weight: bold; font-size: 1.5rem;">{current_round}</div>
        <div style="font-size: 1rem;">Current Round</div>
    </div>
    <div class="stat-box" style="margin-bottom: 1rem;">
        <div style="font-weight: bold; font-size: 1.5rem;">{draft_position}</div>
        <div style="font-size: 1rem;">Draft Position</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="draft-status">
        <strong>LIVE DRAFT</strong><br>
        Pick #{current_pick}
    </div>
    """, unsafe_allow_html=True)

    positions = ['All'] + sorted(player_rankings['position'].unique().tolist())
    selected_position = st.selectbox("Filter Available Players by Position", positions, key="pos_filter")

    filtered_available = (
        available_players[available_players['position'] == selected_position]
        if selected_position != 'All' else available_players
    )
    suggestions = filtered_available.head(3).to_dict('records')

    st.subheader("Available Players")
    df_to_display = filtered_available[['name','position','team','projected_points','rank']].head(20).copy()
    df_to_display.index = df_to_display.index + 1
    st.dataframe(df_to_display, use_container_width=True)

# ---------- Center: AI recommendations ----------
with col2:
    st.subheader("Recommendations")

    roster = build_roster(st.session_state.drafted_players)
    needs = roster_needs_summary(roster)

    # Only show/ask AI about players you can draft right now
    filtered_available_draftable = filter_draftable(filtered_available, roster, limit=50)

    # keep your suggestions list if you like, but better base it on draftable too
    suggestions = filtered_available_draftable.head(3).to_dict('records')

    available_small = compact_available(filtered_available_draftable, limit=15)

    # Loop through AI suggested players (per-card "Why")
    for i, player in enumerate(suggestions, 1):
        team = player.get('team','N/A')
        rank_display = player.get('rank','N/A')

        if use_ai_explanations:
            with st.spinner("Thinking..."):
                why_text = gemini_reason(
                    {
                        "name": player["name"],
                        "position": player["position"],
                        "team": team,
                        "projected_points": float(player.get("projected_points", 0) or 0),
                        "rank": int(player.get("rank", 9999) or 9999),
                    },
                    roster_snapshot=roster,
                    pick_number=st.session_state.current_pick,
                    model_id=model_name,
                    api_key=os.getenv("GOOGLE_API_KEY"),
                )
        else:
            why_text = "Top ranked player based on 2025 projections."

        st.markdown(f"""
<div class="player-suggestion">
    <h4>#{i} {player['name']} ({player['position']})</h4>
    <div style="display: flex; gap: 1rem; margin: 1rem 0;">
        <div class="stat-box">
            <div style="font-weight: bold; font-size: 1.1em;">{player['projected_points']:.1f}</div>
            <div style="font-size: 0.8em; color: white;">Proj Pts</div>
        </div>
        <div class="stat-box">
            <div style="font-weight: bold; font-size: 1.1em;">{team}</div>
            <div style="font-size: 0.8em; color: white;">Team</div>
        </div>
        <div class="stat-box">
            <div style="font-weight: bold; font-size: 1.1em;">{rank_display}</div>
            <div style="font-size: 0.8em; color: white;">Rank</div>
        </div>
    </div>
    <div style="background: white; padding: 0.8rem; border-radius: 6px; font-style: italic; color: black;">
        <strong>Why:</strong> {why_text}
    </div>
</div>
""", unsafe_allow_html=True)

    # Global AI pick button
    st.markdown("#### 🤖 Ask AI: Who should I pick next?")
    if st.button("Ask AI based on needs & availability", key="ask_ai_btn"):
        with st.spinner("Analyzing board + needs..."):
            ai_pick = gemini_pick_and_why(
                available_small=available_small,
                roster_snapshot=roster,
                needs=needs,
                pick_number=st.session_state.current_pick,
                strategy=user_strategy,
                model_id=model_name,
                api_key=os.getenv("GOOGLE_API_KEY"),
            )
        if ai_pick:
            st.success(f"AI suggests: **{ai_pick['name']} ({ai_pick['position']}, {ai_pick['team']})**")
            st.markdown(f"*Why:* {ai_pick['reason']}")
            if st.button(f"Draft {ai_pick['name']} now", key="ai_draft_now"):
                st.session_state.drafted_players.append({
                    "name": ai_pick["name"], "position": ai_pick["position"], "team": ai_pick["team"]
                })
                st.session_state.current_pick += 1
                st.success(f"Drafted {ai_pick['name']}!")
                st.rerun()
        else:
            st.info("Couldn’t get an AI pick. Check your Gemini API key or try again.")

    st.markdown("---")
    st.markdown("### Draft Players Directly")

    col_a, col_b, col_c, col_d, col_e, col_f = st.columns([1,1,1,1,1,1])
    col_a.markdown(" ")
    col_b.markdown("**Proj Pts**")
    col_c.markdown("**Rank**")
    col_d.markdown("**Team**")
    col_e.markdown("**Pos**")
    col_f.markdown("")

# ---------- Manual list with draft buttons ----------
for idx, player in filtered_available.head(20).iterrows():
    name, pos, team = player['name'], player['position'], player['team']
    proj, rank = player['projected_points'], player['rank']

    col_a, col_b, col_c, col_d, col_e, col_f = st.columns([3,1,1,1,1,2])
    col_a.markdown(f"**{name}**")
    col_b.markdown(f"{proj:.1f}")
    col_c.markdown(f"{rank}")
    col_d.markdown(f"{team}")
    col_e.markdown(f"{pos}")

    col_f1, col_f2 = col_f.columns([1,1])

    if col_f1.button("Draft", key=f"draft_avail_{idx}"):
        roster_now = build_roster(st.session_state.drafted_players)
        draft_status = can_draft_player(player, roster_now)
        if draft_status in ('main','flex'):
            st.session_state.drafted_players.append({'name': name,'position': pos,'team': team})
            st.session_state.current_pick += 1
            st.success(f"Drafted {name} to {pos if draft_status=='main' else 'FLEX'}!")
            st.rerun()
        else:
            st.warning(f"Cannot draft {name}: {pos} is filled.")

    if col_f2.button("Already Drafted", key=f"remove_{idx}"):
        st.session_state.drafted_players.append({'name': name})
        st.session_state.current_pick += 1
        st.info(f"{name} marked as already drafted and removed from available list.")
        st.rerun()

# ---------- Right: Roster ----------
with col3:
    st.subheader("Your Team")
    roster = build_roster(st.session_state.drafted_players)
    position_colors = {'QB':'#013369','RB1':'#D50A0A','RB2':'#D50A0A','WR1':'#FFB612','WR2':'#FFB612','TE':'#013369','FLEX':'#0085CA','D/ST':'#002244','K':'#A5ACAF'}

    for slot, player in roster.items():
        slot_color = position_colors.get(slot, '#000000')
        if player:
            st.markdown(f"""
            <div class="roster-slot filled" style="color: white; background: {slot_color}; border-left-color: {slot_color};">
                <span style="font-weight: 600;">{slot}</span>
                <div style="text-align: right;">
                    <div style="font-weight: 600;">{player['name']}</div>
                    <div style="font-size: 0.8em;">{player['team']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="roster-slot" style="color: {slot_color}; border-left-color: {slot_color};">
                <span style="font-weight: 600;">{slot}</span>
                <span style="font-style: italic;">Empty</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("Reset Team", key="reset_btn"):
        st.session_state.drafted_players = []
        st.session_state.current_pick = 1
        st.success("Team has been reset!")
        st.rerun()

# -------- Bottom --------
st.markdown("---")
col4, col5, col6 = st.columns(3)
with col4:
    st.subheader("Trade & Waiver Insights")
    st.markdown("- **Trade targets:** Look for players with increasing snap shares.\n- **Waiver wire:** Monitor breakout rookies.\n- **Strategy:** Prioritize RB depth early.")
with col5:
    st.subheader("Trading Advice")
    st.markdown("- Trade for positional needs.\n- Avoid selling low on injured stars.\n- Use advanced stats for trade evaluation.")
with col6:
    st.subheader("Watchlist")
    st.markdown("- Rising rookies and under-the-radar veterans.\n- Players returning from injury.\n- Matchup-dependent sleepers.")
st.markdown("---")