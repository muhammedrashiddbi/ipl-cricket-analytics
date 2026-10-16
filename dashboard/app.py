import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px


# ============================================================
# THEME COLOURS  (black / white / red)
# ============================================================

RED = "#d32f2f"
DARK_RED = "#9b1c1c"
LIGHT_RED = "#fdecea"
BLACK = "#000000"
WHITE = "#ffffff"


# ============================================================
# PAGE SETTINGS
# ============================================================

st.set_page_config(
    page_title="IPL Bowlers Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# DATABASE
# ============================================================

DB = r"C:\Documents\ipl-cricket-analytics\data\raw\ipl.db"


@st.cache_data
def run_query(sql, params=()):
    conn = sqlite3.connect(DB)
    try:
        return pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()


# ============================================================
# HELPER: BUILD "column IN (?, ?, ...)" FOR MULTI-SELECT
# ============================================================

def add_in_filter(conditions, params, column, selected_values):
    """
    If nothing is selected -> no filter (means All).
    If one or more selected -> column IN (?, ?, ...)
    """
    if selected_values:
        placeholders = ",".join(["?"] * len(selected_values))
        conditions.append(f"{column} IN ({placeholders})")
        params.extend(selected_values)


# ============================================================
# STYLING (BLACK / WHITE / RED)
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- BASE ---------- */

    .stApp {
        background-color: #ffffff;
        color: #000000;
    }

    body,
    p,
    span,
    label,
    div,
    section {
        color: #000000 !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #000000 !important;
    }

    /* red accent line under headings */
    h1 {
        border-bottom: 4px solid #d32f2f;
        padding-bottom: 6px;
    }

    h2 {
        border-left: 5px solid #d32f2f;
        padding-left: 10px;
    }

    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #000000 !important;
        border-top: 4px solid #d32f2f !important;
        border-radius: 8px !important;
        padding: 15px !important;
    }

    [data-testid="stMetricLabel"] {
        color: #000000 !important;
    }

    [data-testid="stMetricValue"] {
        color: #d32f2f !important;
    }

    hr {
        border-color: #000000 !important;
    }


    /* ---------- FILTER LABELS ---------- */

    .stSelectbox label,
    .stMultiSelect label,
    .stNumberInput label,
    .stRadio label {
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 15px !important;
    }


    /* ---------- SELECT BOX / MULTISELECT (CLOSED STATE) ---------- */

    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] > div > div {
        background-color: #e3f0ff !important;
    }

    div[data-baseweb="select"] > div {
        border: 2px solid #000000 !important;
        border-radius: 8px !important;
        min-height: 44px !important;
    }

    div[data-baseweb="select"] > div:hover {
        border-color: #d32f2f !important;
    }

    div[data-baseweb="select"] span,
    div[data-baseweb="select"] input,
    div[data-baseweb="select"] div {
        color: #000000 !important;
        font-weight: 500 !important;
    }

    div[data-baseweb="select"] input::placeholder {
        color: #555555 !important;
        opacity: 1 !important;
    }

    div[data-baseweb="select"] svg {
        fill: #d32f2f !important;
        color: #d32f2f !important;
    }


    /* ---------- MULTISELECT SELECTED CHIPS ---------- */

    span[data-baseweb="tag"] {
        background-color: #d32f2f !important;
        border-radius: 6px !important;
    }

    span[data-baseweb="tag"] span,
    span[data-baseweb="tag"] div {
        color: #f2f2f2 !important;
        font-weight: 600 !important;
    }

    span[data-baseweb="tag"] svg {
        fill: #ffffff !important;
        color: #ffffff !important;
    }


    /* ---------- DROPDOWN LIST (WHEN CLICKED) ---------- */

    /* whole dropdown panel = very light blue */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] div,
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li,
    div[data-baseweb="menu"],
    ul[role="listbox"] {
        background-color: #f5f9ff !important;
        color: #546475 !important;
    }

    div[data-baseweb="popover"] > div {
        border: 1px solid #000000 !important;
        border-radius: 8px !important;
    }

    li[role="option"] {
        font-weight: 500 !important;
        border-bottom: 1px solid #c9dcf2 !important;
    }

    li[role="option"] *,
    div[data-baseweb="popover"] li,
    div[data-baseweb="popover"] li * {
        color: #000000 !important;
    }

    /* hover */
    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="popover"] li:hover *,
    li[role="option"]:hover,
    li[role="option"]:hover * {
        background-color: #d32f2f !important;
        color: #f2f2f2 !important;
    }

    /* selected / highlighted option */
    li[role="option"][aria-selected="true"],
    li[role="option"][aria-selected="true"] * {
        background-color: #dce9f9 !important;
        color: #000000 !important;
        font-weight: 700 !important;
    }


    /* ---------- NUMBER INPUT ---------- */

    .stNumberInput input {
        color: #000000 !important;
        background-color: #ffffff !important;
        font-weight: 600 !important;
    }

    .stNumberInput div[data-baseweb="input"] {
        border: 2px solid #000000 !important;
        border-radius: 8px !important;
        background-color: #fff2f4 !important;
    }

    .stNumberInput div[data-baseweb="input"]:hover {
        border-color: #d32f2f !important;
    }

    .stNumberInput button {
        background-color: #d32f2f !important;
    }

    .stNumberInput button svg {
        fill: #ffffff !important;
        color: #ffffff !important;
    }


    /* ===== FORCE WHITE-SHADE BLUE DROPDOWNS (overrides dark theme) ===== */

    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div > div,
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div > div {
        background-color: #e3f0ff !important;
    }

    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
        border: 2px solid #000000 !important;
        border-radius: 8px !important;
    }

    [data-testid="stSelectbox"] [data-baseweb="select"] *,
    [data-testid="stMultiSelect"] [data-baseweb="select"] * {
        color: #000000 !important;
    }

    /* open dropdown panel */
    [data-baseweb="popover"],
    [data-baseweb="popover"] * {
        background-color: #f5f9ff !important;
        color: #000000 !important;
    }

    /* selected option */
    [data-baseweb="popover"] li[aria-selected="true"],
    [data-baseweb="popover"] li[aria-selected="true"] * {
        background-color: #dce9f9 !important;
        font-weight: 700 !important;
    }

    /* hover option */
    [data-baseweb="popover"] li:hover,
    [data-baseweb="popover"] li:hover * {
        background-color: #d32f2f !important;
        color: #f2f2f2 !important;
    }
/* closed select / multiselect box */
    [data-testid="stSelectbox"] div,
    [data-testid="stMultiSelect"] div {
        background-color: #d5dce3 !important;    /* closed box colour */
        color: #000914 !important;
    }

    /* keep the labels transparent */
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] * {
        background-color: transparent !important;
    }

    /* open dropdown list + the panel around it */
    [role="listbox"],
    [role="listbox"] *,
    [role="option"],
    [role="option"] *,
    div:has(> [role="listbox"]),
    div:has(> div > [role="listbox"]),
    div:has(> div > div > [role="listbox"]) {
        background-color: #5a6573 !important;    /* <-- dropdown list colour */
        color: #000000 !important;
    }

    /* selected option (darker so it stands out) */
    [role="option"][aria-selected="true"],
    [role="option"][aria-selected="true"] * {
        background-color: #2f5f96 !important;
        color: #ffffff !important;
    }

    /* hover option */
    [role="option"]:hover,
    [role="option"]:hover * {
        background-color: #d32f2f !important;
        color: #ffffff !important;
    }

    /* keep multiselect chips red with white text */
    [data-testid="stMultiSelect"] span[data-baseweb="tag"],
    [data-testid="stMultiSelect"] span[data-baseweb="tag"] * {
        background-color: #d32f2f !important;
        color: #ffffff !important;
    }
    
/* Make Season, Bowling Team and Bowling Style text black */
[data-testid="stMultiSelect"] label,
[data-testid="stSelectbox"] label {
    color: #000000 !important;
}

[data-testid="stMultiSelect"] [data-baseweb="select"] *,
[data-testid="stSelectbox"] [data-baseweb="select"] * {
    color: #000000 !important;
}
    /* ===== TEXT INSIDE CLOSED SELECT BOXES = BLACK ===== */

    /* "All seasons", "All teams", "All" */
    [data-testid="stSelectbox"] *,
    [data-testid="stMultiSelect"] * {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        opacity: 1 !important;
    }

    /* placeholder text (All seasons / All teams) */
    [data-testid="stSelectbox"] input::placeholder,
    [data-testid="stMultiSelect"] input::placeholder {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        opacity: 1 !important;
    }

    /* keep selected chips red with white text */
    [data-testid="stMultiSelect"] span[data-baseweb="tag"],
    [data-testid="stMultiSelect"] span[data-baseweb="tag"] * {
        background-color: #d32f2f !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
        /* ===== ALL DROPDOWN LISTS (Select Bowler, Season, Team, Style) ===== */

    html body div[data-baseweb="popover"],
    html body div[data-baseweb="popover"] *,
    html body [data-testid="stSelectboxVirtualDropdown"],
    html body [data-testid="stSelectboxVirtualDropdown"] *,
    html body ul[role="listbox"],
    html body ul[role="listbox"] *,
    html body li[role="option"],
    html body li[role="option"] * {
        background: #e3f0ff !important;          /* <-- list colour (light) */
        background-color: #e3f0ff !important;    /* <-- same colour here */
        color: #000000 !important;
        opacity: 1 !important;
        filter: none !important;
    }

    /* selected option */
    html body li[role="option"][aria-selected="true"],
    html body li[role="option"][aria-selected="true"] * {
        background: #bcd9f7 !important;
        background-color: #bcd9f7 !important;
        color: #000000 !important;
    }

    /* hover option */
    html body li[role="option"]:hover,
    html body li[role="option"]:hover * {
        background: #d32f2f !important;
        background-color: #d32f2f !important;
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TITLE
# ============================================================

st.title("IPL Bowlers Analytics")
st.caption("IPL bowling performance analysis")


# ============================================================
# NAVIGATION
# ============================================================

page = st.radio(
    "Navigation",
    ["Bowlers Overview", "Individual Bowler"],
    horizontal=True
)

st.divider()


# ============================================================
# BASIC DATABASE DATA
# ============================================================

try:
    season_df = run_query(
        """
        SELECT DISTINCT season_id
        FROM deliveries
        WHERE season_id IS NOT NULL
        ORDER BY season_id
        """
    )
except Exception as e:
    st.error("Database connection failed.")
    st.code(str(e))
    st.stop()

seasons = season_df["season_id"].tolist()


# ============================================================
# TEAMS
# ============================================================

team_df = run_query(
    """
    SELECT DISTINCT bowling_team
    FROM deliveries
    WHERE bowling_team IS NOT NULL
    AND bowling_team <> ''
    ORDER BY bowling_team
    """
)

teams = team_df["bowling_team"].tolist()


# ============================================================
# BOWLERS
# ============================================================

bowler_df = run_query(
    """
    SELECT DISTINCT bowler
    FROM deliveries
    WHERE bowler IS NOT NULL
    AND bowler <> ''
    ORDER BY bowler
    """
)

bowler_list = bowler_df["bowler"].tolist()


# ============================================================
# BOWLING STYLE
# ============================================================

STYLE_CASE = """
CASE

    WHEN LOWER(COALESCE(d.bowler_type, '')) LIKE '%spin%'
        OR LOWER(COALESCE(d.bowler_type, '')) LIKE '%break%'
        OR LOWER(COALESCE(d.bowler_type, '')) LIKE '%googly%'
        OR LOWER(COALESCE(d.bowler_type, '')) LIKE '%orthodox%'
        OR LOWER(COALESCE(d.bowler_type, '')) LIKE '%chinaman%'

    THEN 'Spin'

    WHEN LOWER(COALESCE(d.bowler_type, '')) LIKE '%pace%'
        OR LOWER(COALESCE(d.bowler_type, '')) LIKE '%fast%'
        OR LOWER(COALESCE(d.bowler_type, '')) LIKE '%medium%'
        OR LOWER(COALESCE(d.bowler_type, '')) LIKE '%seam%'

    THEN 'Pace'

    ELSE 'Other'

END
"""


# ============================================================
# ============================================================
# BOWLERS OVERVIEW
# ============================================================
# ============================================================

if page == "Bowlers Overview":

    st.header("Bowlers Overview")

    # ========================================================
    # FILTERS
    # ========================================================

    with st.form("overview_filters"):

        f1, f2, f3, f4 = st.columns(4)

        with f1:
            selected_seasons = st.multiselect(
                "Season",
                seasons,
                placeholder="All seasons"
            )

        with f2:
            selected_teams = st.multiselect(
                "Bowling Team",
                teams,
                placeholder="All teams"
            )

        with f3:
            selected_style = st.selectbox(
                "Bowling Style",
                ["All", "Spin", "Pace"]
            )

        with f4:
            minimum_balls = st.number_input(
                "Minimum Balls",
                min_value=0,
                value=100,
                step=10
            )

        apply_filters = st.form_submit_button("Apply Filters")

    # ========================================================
    # SQL FILTERS
    # ========================================================

    conditions = []
    query_params = []

    add_in_filter(conditions, query_params, "d.season_id", selected_seasons)
    add_in_filter(conditions, query_params, "d.bowling_team", selected_teams)

    if conditions:
        where_sql = "WHERE " + " AND ".join(conditions)
    else:
        where_sql = ""

    # ========================================================
    # MAIN BOWLER QUERY
    # ========================================================

    query = f"""

    SELECT

        d.bowler AS Bowler,

        {STYLE_CASE} AS Style,

        SUM(
            CASE
                WHEN COALESCE(d.is_wide_ball, 0) = 0
                AND COALESCE(d.is_no_ball, 0) = 0
                THEN 1
                ELSE 0
            END
        ) AS Balls,

        SUM(
            COALESCE(d.total_runs, 0)
        ) AS Runs,

        SUM(
            CASE
                WHEN COALESCE(d.is_wicket, 0) = 1
                AND COALESCE(d.wicket_kind, '') NOT IN
                (
                    'run out',
                    'retired hurt',
                    'obstructing the field'
                )
                THEN 1
                ELSE 0
            END
        ) AS Wickets,

        SUM(
            CASE
                WHEN COALESCE(d.total_runs, 0) = 0
                AND COALESCE(d.is_wide_ball, 0) = 0
                AND COALESCE(d.is_no_ball, 0) = 0
                THEN 1
                ELSE 0
            END
        ) AS Dot_Balls

    FROM deliveries d

    {where_sql}

    GROUP BY
        d.bowler,
        Style

    HAVING Balls >= ?

    ORDER BY
        Wickets DESC

    """

    # HAVING Balls >= ? needs this parameter
    query_params.append(minimum_balls)

    # ========================================================
    # EXECUTE QUERY
    # ========================================================

    bowlers = run_query(query, tuple(query_params))

    # ========================================================
    # STYLE FILTER
    # ========================================================

    if selected_style != "All":
        bowlers = bowlers[bowlers["Style"] == selected_style]

    # ========================================================
    # EMPTY DATA CHECK
    # ========================================================

    if bowlers.empty:
        st.warning("No data available for the selected filters.")
        st.stop()

    # ========================================================
    # CALCULATIONS
    # ========================================================

    bowlers["Overs"] = (bowlers["Balls"] / 6).round(1)

    bowlers["Economy"] = (
        bowlers["Runs"] / bowlers["Balls"] * 6
    ).round(2)

    bowlers["Dot_Ball_Percent"] = (
        bowlers["Dot_Balls"] / bowlers["Balls"] * 100
    ).round(2)

    # ========================================================
    # KPI
    # ========================================================

    st.subheader("Key Performance")

    total_bowlers = bowlers["Bowler"].nunique()
    total_balls = int(bowlers["Balls"].sum())
    total_wickets = int(bowlers["Wickets"].sum())
    total_runs = bowlers["Runs"].sum()
    overall_economy = total_runs / total_balls * 6

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric("Bowlers", f"{total_bowlers:,}")

    with k2:
        st.metric("Balls", f"{total_balls:,}")

    with k3:
        st.metric("Wickets", f"{total_wickets:,}")

    with k4:
        st.metric("Economy", f"{overall_economy:.2f}")

    st.divider()

    # ========================================================
    # CHART 1
    # ECONOMY BY BOWLING STYLE
    # ========================================================

    st.header("Economy by Bowling Style")

    style_data = (
        bowlers
        .groupby("Style", as_index=False)
        .agg(Economy=("Economy", "mean"))
    )

    style_data["Economy"] = style_data["Economy"].round(2)

    fig1 = px.bar(
        style_data,
        x="Style",
        y="Economy",
        text="Economy",
        color_discrete_sequence=[RED]
    )

    fig1.update_traces(
        textposition="outside",
        textfont=dict(color=BLACK, size=13),
        marker_line_color=BLACK,
        marker_line_width=1.2,
        hovertemplate="<b>%{x}</b><br>Economy: %{y:.2f}<extra></extra>"
    )

    fig1.update_layout(
        height=430,
        plot_bgcolor=WHITE,
        paper_bgcolor=WHITE,
        font=dict(color=BLACK, size=13),
        xaxis=dict(
            title=dict(text="Bowling Style", font=dict(color=BLACK, size=15)),
            tickfont=dict(color=BLACK, size=13),
            showticklabels=True,
            showgrid=False
        ),
        yaxis=dict(
            title=dict(text="Economy", font=dict(color=BLACK, size=15)),
            tickfont=dict(color=BLACK, size=13),
            showticklabels=True,
            gridcolor="#dddddd"
        ),
        showlegend=False,
        margin=dict(l=70, r=30, t=30, b=80)
    )

    st.plotly_chart(fig1, use_container_width=True)

    # ========================================================
    # CHART 2
    # DOT BALL SHARE
    # ========================================================

    st.header("Dot-ball Share by Bowling Style")

    dot_data = (
        bowlers
        .groupby("Style", as_index=False)
        .agg(Dot_Ball_Share=("Dot_Ball_Percent", "mean"))
    )

    dot_data["Dot_Ball_Share"] = dot_data["Dot_Ball_Share"].round(2)

    fig2 = px.bar(
        dot_data,
        x="Style",
        y="Dot_Ball_Share",
        text="Dot_Ball_Share",
        color_discrete_sequence=[BLACK]
    )

    fig2.update_traces(
        textposition="outside",
        textfont=dict(color=BLACK, size=13),
        hovertemplate="<b>%{x}</b><br>Dot-ball Share: %{y:.2f}%<extra></extra>"
    )

    fig2.update_layout(
        height=430,
        plot_bgcolor=WHITE,
        paper_bgcolor=WHITE,
        font=dict(color=BLACK, size=13),
        xaxis=dict(
            title=dict(text="Bowling Style", font=dict(color=BLACK, size=15)),
            tickfont=dict(color=BLACK, size=13),
            showticklabels=True,
            showgrid=False
        ),
        yaxis=dict(
            title=dict(text="Dot-ball Share (%)", font=dict(color=BLACK, size=15)),
            tickfont=dict(color=BLACK, size=13),
            showticklabels=True,
            gridcolor="#dddddd"
        ),
        showlegend=False,
        margin=dict(l=70, r=30, t=30, b=80)
    )

    st.plotly_chart(fig2, use_container_width=True)

    # ========================================================
    # CHART 3
    # TOP WICKET TAKERS
    # ========================================================

    st.header("Top Bowlers by Wickets")

    top_wickets = (
        bowlers
        .sort_values("Wickets", ascending=False)
        .head(10)
        .copy()
    )

    top_wickets = top_wickets.sort_values("Wickets")

    fig3 = px.bar(
        top_wickets,
        x="Wickets",
        y="Bowler",
        orientation="h",
        text="Wickets",
        color_discrete_sequence=[RED]
    )

    fig3.update_traces(
        textposition="outside",
        textfont=dict(color=BLACK, size=12),
        hovertemplate="<b>%{y}</b><br>Wickets: %{x}<extra></extra>"
    )

    fig3.update_layout(
        height=500,
        plot_bgcolor=WHITE,
        paper_bgcolor=WHITE,
        font=dict(color=BLACK, size=13),
        xaxis=dict(
            title=dict(text="Wickets", font=dict(color=BLACK, size=15)),
            tickfont=dict(color=BLACK, size=13),
            showticklabels=True,
            gridcolor="#dddddd"
        ),
        yaxis=dict(
            title=dict(text="Bowler", font=dict(color=BLACK, size=15)),
            tickfont=dict(color=BLACK, size=12),
            showticklabels=True,
            automargin=True
        ),
        showlegend=False,
        margin=dict(l=180, r=70, t=30, b=70)
    )

    st.plotly_chart(fig3, use_container_width=True)

    # ========================================================
    # CHART 4
    # ECONOMY BY BOWLER
    # ========================================================

    st.header("Economy by Bowler")

    economy_data = (
        bowlers
        .sort_values("Economy", ascending=True)
        .head(15)
        .copy()
    )

    fig4 = px.bar(
        economy_data,
        x="Economy",
        y="Bowler",
        orientation="h",
        text="Economy",
        color_discrete_sequence=[BLACK]
    )

    fig4.update_traces(
        textposition="outside",
        textfont=dict(color=BLACK, size=12),
        hovertemplate="<b>%{y}</b><br>Economy: %{x:.2f}<extra></extra>"
    )

    fig4.update_layout(
        height=650,
        plot_bgcolor=WHITE,
        paper_bgcolor=WHITE,
        font=dict(color=BLACK, size=13),
        xaxis=dict(
            title=dict(text="Economy", font=dict(color=BLACK, size=15)),
            tickfont=dict(color=BLACK, size=13),
            showticklabels=True,
            gridcolor="#dddddd"
        ),
        yaxis=dict(
            title=dict(text="Bowler", font=dict(color=BLACK, size=15)),
            tickfont=dict(color=BLACK, size=12),
            showticklabels=True,
            automargin=True
        ),
        showlegend=False,
        margin=dict(l=180, r=70, t=30, b=70)
    )

    st.plotly_chart(fig4, use_container_width=True)

    # ========================================================
    # FINAL TABLE
    # ========================================================

    st.header("Bowler Performance Table")

    final_table = bowlers[
        [
            "Bowler",
            "Style",
            "Balls",
            "Overs",
            "Runs",
            "Wickets",
            "Economy",
            "Dot_Ball_Percent"
        ]
    ].copy()

    final_table.columns = [
        "Bowler",
        "Style",
        "Balls",
        "Overs",
        "Runs",
        "Wickets",
        "Economy",
        "Dot-ball %"
    ]

    st.dataframe(final_table, use_container_width=True, hide_index=True)


# ============================================================
# ============================================================
# INDIVIDUAL BOWLER
# ============================================================
# ============================================================

else:

    st.header("Individual Bowler")

    # ========================================================
    # BOWLER SELECT
    # ========================================================

    if not bowler_list:
        st.warning("No bowlers found.")
        st.stop()

    selected_bowler = st.selectbox("Select Bowler", bowler_list)

    f1, f2 = st.columns(2)

    with f1:
        individual_seasons = st.multiselect(
            "Season",
            seasons,
            placeholder="All seasons",
            key="individual_season"
        )

    with f2:
        individual_teams = st.multiselect(
            "Bowling Team",
            teams,
            placeholder="All teams",
            key="individual_team"
        ) 

  
    # ========================================================
    # CONDITIONS
    # ========================================================

    conditions = ["d.bowler = ?"]
    params = [selected_bowler]

    add_in_filter(conditions, params, "d.season_id", individual_seasons)
    add_in_filter(conditions, params, "d.bowling_team", individual_teams)

    where_sql = "WHERE " + " AND ".join(conditions)

    # ========================================================
    # INDIVIDUAL DATA
    # ========================================================

    individual = run_query(
        f"""
        SELECT
            d.season_id,
            d.bowler,
            d.batting_team,
            d.bowling_team,
            d.total_runs,
            d.is_wide_ball,
            d.is_no_ball,
            d.is_wicket,
            d.wicket_kind
        FROM deliveries d
        {where_sql}
        """,
        tuple(params)
    )

    if individual.empty:
        st.warning("No data available.")
        st.stop()

    # ========================================================
    # LEGAL BALLS
    # ========================================================

    legal = individual[
        (individual["is_wide_ball"].fillna(0) == 0)
        &
        (individual["is_no_ball"].fillna(0) == 0)
    ].copy()

    balls = len(legal)

    runs = legal["total_runs"].fillna(0).sum()

    wickets = individual[
        (individual["is_wicket"].fillna(0) == 1)
        &
        (
            ~individual["wicket_kind"]
            .fillna("")
            .isin(["run out", "retired hurt", "obstructing the field"])
        )
    ].shape[0]

    if balls > 0:
        economy = runs / balls * 6
    else:
        economy = 0

    dot_balls = legal[legal["total_runs"].fillna(0) == 0].shape[0]

    if balls > 0:
        dot_percentage = dot_balls / balls * 100
    else:
        dot_percentage = 0

    # ========================================================
    # KPI
    # ========================================================

    st.subheader("Performance")

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric("Bowler", selected_bowler)

    with k2:
        st.metric("Balls", f"{balls:,}")

    with k3:
        st.metric("Wickets", f"{wickets:,}")

    with k4:
        st.metric("Economy", f"{economy:.2f}")

    st.divider()

    # ========================================================
    # ECONOMY BY SEASON
    # ========================================================

    st.header("Economy by Season")

    season_rows = []

    for season, group in individual.groupby("season_id"):

        legal_group = group[
            (group["is_wide_ball"].fillna(0) == 0)
            &
            (group["is_no_ball"].fillna(0) == 0)
        ]

        season_balls = len(legal_group)
        season_runs = legal_group["total_runs"].fillna(0).sum()

        if season_balls > 0:
            season_economy = season_runs / season_balls * 6
        else:
            season_economy = 0

        season_rows.append(
            {"Season": season, "Economy": round(season_economy, 2)}
        )

    season_data = pd.DataFrame(season_rows)

    fig5 = px.line(
        season_data,
        x="Season",
        y="Economy",
        markers=True,
        text="Economy",
        color_discrete_sequence=[RED]
    )

    fig5.update_traces(
        textposition="top center",
        textfont=dict(color=BLACK, size=12),
        line=dict(color=RED, width=3),
        marker=dict(color=BLACK, size=9, line=dict(color=RED, width=2)),
        hovertemplate="<b>Season: %{x}</b><br>Economy: %{y:.2f}<extra></extra>"
    )

    fig5.update_layout(
        height=450,
        plot_bgcolor=WHITE,
        paper_bgcolor=WHITE,
        font=dict(color=BLACK, size=13),
        xaxis=dict(
            title=dict(text="Season", font=dict(color=BLACK, size=15)),
            tickfont=dict(color=BLACK, size=13),
            showticklabels=True,
            showgrid=False
        ),
        yaxis=dict(
            title=dict(text="Economy", font=dict(color=BLACK, size=15)),
            tickfont=dict(color=BLACK, size=13),
            showticklabels=True,
            gridcolor="#dddddd"
        ),
        margin=dict(l=70, r=30, t=30, b=80)
    )

    st.plotly_chart(fig5, use_container_width=True)

    # ========================================================
    # ECONOMY BY OPPONENT
    # ========================================================

    st.header("Economy by Opponent")

    opponent_rows = []

    for opponent, group in individual.groupby("batting_team"):

        legal_group = group[
            (group["is_wide_ball"].fillna(0) == 0)
            &
            (group["is_no_ball"].fillna(0) == 0)
        ]

        opponent_balls = len(legal_group)
        opponent_runs = legal_group["total_runs"].fillna(0).sum()

        if opponent_balls > 0:
            opponent_economy = opponent_runs / opponent_balls * 6
        else:
            opponent_economy = 0

        opponent_rows.append(
            {"Opponent": opponent, "Economy": round(opponent_economy, 2)}
        )

    opponent_data = pd.DataFrame(opponent_rows)
    opponent_data = opponent_data.sort_values("Economy")

    fig6 = px.bar(
        opponent_data,
        x="Economy",
        y="Opponent",
        orientation="h",
        text="Economy",
        color_discrete_sequence=[BLACK]
    )

    fig6.update_traces(
        textposition="outside",
        textfont=dict(color=BLACK, size=12),
        hovertemplate="<b>%{y}</b><br>Economy: %{x:.2f}<extra></extra>"
    )

    fig6.update_layout(
        height=550,
        plot_bgcolor=WHITE,
        paper_bgcolor=WHITE,
        font=dict(color=BLACK, size=13),
        xaxis=dict(
            title=dict(text="Economy", font=dict(color=BLACK, size=15)),
            tickfont=dict(color=BLACK, size=13),
            showticklabels=True,
            gridcolor="#dddddd"
        ),
        yaxis=dict(
            title=dict(text="Opponent", font=dict(color=BLACK, size=15)),
            tickfont=dict(color=BLACK, size=12),
            showticklabels=True,
            automargin=True
        ),
        margin=dict(l=160, r=70, t=30, b=70)
    )

    st.plotly_chart(fig6, use_container_width=True)

    # ========================================================
    # DISMISSAL TYPES
    # ========================================================

    st.header("Dismissal Types")

    dismissal = individual[individual["is_wicket"].fillna(0) == 1].copy()

    dismissal = dismissal[
        ~dismissal["wicket_kind"]
        .fillna("")
        .isin(["run out", "retired hurt", "obstructing the field"])
    ]

    if not dismissal.empty:

        dismissal_data = (
            dismissal["wicket_kind"]
            .fillna("Unknown")
            .value_counts()
            .reset_index()
        )

        dismissal_data.columns = ["Dismissal", "Wickets"]

        fig7 = px.bar(
            dismissal_data,
            x="Dismissal",
            y="Wickets",
            text="Wickets",
            color_discrete_sequence=[RED]
        )

        fig7.update_traces(
            textposition="outside",
            textfont=dict(color=BLACK, size=12),
            marker_line_color=BLACK,
            marker_line_width=1.2,
            hovertemplate="<b>%{x}</b><br>Wickets: %{y}<extra></extra>"
        )

        fig7.update_layout(
            height=450,
            plot_bgcolor=WHITE,
            paper_bgcolor=WHITE,
            font=dict(color=BLACK, size=13),
            xaxis=dict(
                title=dict(text="Dismissal Type", font=dict(color=BLACK, size=15)),
                tickfont=dict(color=BLACK, size=12),
                showticklabels=True,
                showgrid=False
            ),
            yaxis=dict(
                title=dict(text="Wickets", font=dict(color=BLACK, size=15)),
                tickfont=dict(color=BLACK, size=13),
                showticklabels=True,
                gridcolor="#dddddd"
            ),
            margin=dict(l=70, r=30, t=30, b=100)
        )

        st.plotly_chart(fig7, use_container_width=True)

    # ========================================================
    # FINAL TABLE
    # ========================================================

    st.header("Season Performance Table")

    st.dataframe(season_data, use_container_width=True, hide_index=True)