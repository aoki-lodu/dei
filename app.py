import streamlit as st
import pandas as pd
import time

# ==========================================
# 0. 設定 & データ定義
# ==========================================
st.set_page_config(page_title="DE&I Management Game", layout="wide", initial_sidebar_state="collapsed")

# --- カスタムCSS ---
st.markdown("""
<style>
    /* ベースフォントとサイズ調整 */
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', 'Hiragino Kaku Gothic ProN', 'ヒラギノ角ゴ ProN W3', sans-serif;
        font-size: 18px; 
    }
    
    /* タイトルのサイズ調整 */
    h1 {
        font-size: 1.8rem !important;
        font-weight: bold;
        margin-bottom: 0.5rem !important;
    }
    
    /* スコアボード */
    .score-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(90px, 1fr));
        gap: 10px;
        background: #ffffff;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 25px;
        text-align: center;
        color: #333333;
    }
    .score-item {
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        margin-bottom: 5px;
    }
    .score-label { 
        font-size: 13px; 
        color: #666666 !important;
        white-space: nowrap; 
        margin-bottom: 2px;
    }
    .score-value { 
        font-size: 20px; 
        font-weight: bold; 
        color: #333333 !important;
        line-height: 1.2;
    }
    
    /* 施策カード */
    .policy-card {
        background: white; 
        border: 1px solid #ddd; 
        padding: 15px;
        border-radius: 8px; margin-bottom: 12px; 
        display: flex; justify-content: space-between; align-items: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        color: #333333;
    }
    .tag {
        font-size: 0.85em;
        padding: 4px 6px; 
        border-radius: 4px; 
        margin-left: 4px;
        white-space: nowrap;
    }
    
    /* メンバーカードのスタイル */
    .member-card {
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px !important; /* 間隔を元に戻しました */
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        color: #333333;
        background-color: white;
    }

    /* データフレーム調整 */
    thead tr th:first-child { display: none }
    tbody th { display: none }
    
    /* タブの強調 */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 定数定義 ---
RISK_MAP_DISPLAY = {
    "1": "🎉 セーフ", "2": "💚 くらし", "3": "📖 キャリア", 
    "4": "🌏 グローバル", "5": "🌈 アイデンティティ", "6": "⚖️ フェア"
}
SORT_ORDER = ['💚', '📖', '🌏', '🌈', '⚖️']

# --- ✅ 初期人財カード (ゲーム開始時専用) ---
INITIAL_CHARACTERS = [
    {"name": "結城 奏太", "icons": ["💚", "🌈"], "base": 2},
    {"name": "柊 凛花", "icons": ["📖", "⚖️"], "base": 2},
    {"name": "神崎 剣也", "icons": ["🌏"], "base": 2},
    {"name": "桜庭 美月", "icons": ["💚", "📖"], "base": 2},
    {"name": "天道 翔", "icons": ["💚", "🌏"], "base": 2},
    {"name": "橘 沙織", "icons": ["📖", "🌈"], "base": 2},
    {"name": "Leon Heartfield", "icons": ["🌏", "⚖️"], "base": 2},
    {"name": "Elena", "icons": ["🌈", "⚖️"], "base": 2}
]

# --- ✅ 人財データ (1個→2個→3個の順にソート済み) ---
CHARACTERS_DB = [
    {"name": "本田 琴音", "icons": ["💚"], "base": 1},
    {"name": "浜田 佑香", "icons": ["💚"], "base": 1},
    {"name": "白石 凛子", "icons": ["💚"], "base": 1},
    {"name": "石田 紅葉", "icons": ["💚"], "base": 1},
    {"name": "山田 隼人", "icons": ["💚"], "base": 1},
    {"name": "佐伯 啓", "icons": ["💚"], "base": 2},
    {"name": "池田 悠真", "icons": ["💚"], "base": 2},
    {"name": "加藤 ひかる", "icons": ["💚"], "base": 2},
    {"name": "大野 未来", "icons": ["💚"], "base": 2},
    {"name": "谷口 実央", "icons": ["💚"], "base": 3},
    {"name": "鈴木 翔太", "icons": ["💚"], "base": 3},
    {"name": "木村 拓海", "icons": ["💚"], "base": 3},
    {"name": "藤田 陽", "icons": ["💚"], "base": 4},
    {"name": "佐々木 真央", "icons": ["💚"], "base": 4},
    {"name": "川瀬 美羽", "icons": ["💚"], "base": 5},
    {"name": "井上 菜々", "icons": ["📖"], "base": 1},
    {"name": "神田 亮", "icons": ["📖"], "base": 1},
    {"name": "橋本 紗季", "icons": ["📖"], "base": 1},
    {"name": "吉田 玲奈", "icons": ["📖"], "base": 1},
    {"name": "池上 直樹", "icons": ["📖"], "base": 1},
    {"name": "原 真子", "icons": ["📖"], "base": 2},
    {"name": "宮本 蒼真", "icons": ["📖"], "base": 2},
    {"name": "中村 さくら", "icons": ["📖"], "base": 2},
    {"name": "竹内 智也", "icons": ["📖"], "base": 2},
    {"name": "杉本 麻衣", "icons": ["📖"], "base": 3},
    {"name": "上田 翔", "icons": ["📖"], "base": 3},
    {"name": "斎藤 陽介", "icons": ["📖"], "base": 3},
    {"name": "中島 慎也", "icons": ["📖"], "base": 4},
    {"name": "島田 こはる", "icons": ["📖"], "base": 4},
    {"name": "村上 拓人", "icons": ["📖"], "base": 5},
    {"name": "An Nguyen", "icons": ["🌏"], "base": 1},
    {"name": "Liam O'Connor", "icons": ["🌏"], "base": 1},
    {"name": "Carlos Souza", "icons": ["🌏"], "base": 1},
    {"name": "Hanna Schmidt", "icons": ["🌏"], "base": 1},
    {"name": "Ava Chen", "icons": ["🌏"], "base": 1},
    {"name": "Mei Tanaka", "icons": ["🌏"], "base": 2},
    {"name": "Alec Tan", "icons": ["🌏"], "base": 2},
    {"name": "Lucas Pereira", "icons": ["🌏"], "base": 2},
    {"name": "Ethan Wang", "icons": ["🌏"], "base": 2},
    {"name": "Minh Tran", "icons": ["🌏"], "base": 3},
    {"name": "Olga Petrov", "icons": ["🌏"], "base": 3},
    {"name": "Priya Singh", "icons": ["🌏"], "base": 3},
    {"name": "Julia Novak", "icons": ["🌏"], "base": 4},
    {"name": "Hyejin Park", "icons": ["🌏"], "base": 4},
    {"name": "Sergey Ivanov", "icons": ["🌏"], "base": 5},
    {"name": "長井 智哉", "icons": ["🌈"], "base": 1},
    {"name": "佐藤 陽菜", "icons": ["🌈"], "base": 1},
    {"name": "田村 結菜", "icons": ["🌈"], "base": 1},
    {"name": "内田 隼", "icons": ["🌈"], "base": 1},
    {"name": "宮下 慧", "icons": ["🌈"], "base": 1},
    {"name": "石井 直人", "icons": ["🌈"], "base": 2},
    {"name": "花田 里緒", "icons": ["🌈"], "base": 2},
    {"name": "岡本 さとみ", "icons": ["🌈"], "base": 2},
    {"name": "田辺 海斗", "icons": ["🌈"], "base": 2},
    {"name": "Sofia García", "icons": ["🌈"], "base": 3},
    {"name": "柴田 悠斗", "icons": ["🌈"], "base": 3},
    {"name": "茅野 すみれ", "icons": ["🌈"], "base": 3},
    {"name": "松本 直哉", "icons": ["🌈"], "base": 4},
    {"name": "森 真由", "icons": ["🌈"], "base": 4},
    {"name": "遠藤 大地", "icons": ["🌈"], "base": 5},
    {"name": "藤川 佑", "icons": ["⚖️"], "base": 1},
    {"name": "伊藤 葵", "icons": ["⚖️"], "base": 1},
    {"name": "磯部 瞳", "icons": ["⚖️"], "base": 1},
    {"name": "工藤 彩花", "icons": ["⚖️"], "base": 1},
    {"name": "渡辺 結衣", "icons": ["⚖️"], "base": 1},
    {"name": "長谷川 凛", "icons": ["⚖️"], "base": 2},
    {"name": "林 佳奈", "icons": ["⚖️"], "base": 2},
    {"name": "新井 美月", "icons": ["⚖️"], "base": 2},
    {"name": "原田 怜", "icons": ["⚖️"], "base": 2},
    {"name": "野村 智", "icons": ["⚖️"], "base": 3},
    {"name": "山根 悠", "icons": ["⚖️"], "base": 3},
    {"name": "平野 健太", "icons": ["⚖️"], "base": 3},
    {"name": "大西 悠", "icons": ["⚖️"], "base": 4},
    {"name": "山崎 優斗", "icons": ["⚖️"], "base": 4},
    {"name": "中原 玲央", "icons": ["⚖️"], "base": 5},
    {"name": "安藤 望", "icons": ["💚", "📖"], "base": 2},
    {"name": "山口 咲良", "icons": ["💚", "🌏"], "base": 4},
    {"name": "近藤 海斗", "icons": ["💚", "🌈"], "base": 5},
    {"name": "阿部 千尋", "icons": ["💚", "⚖️"], "base": 1},
    {"name": "田中 蓮", "icons": ["💚", "⚖️"], "base": 1},
    {"name": "Amira Hassan", "icons": ["📖", "🌏"], "base": 4},
    {"name": "山本 大翔", "icons": ["📖", "🌈"], "base": 5},
    {"name": "高橋 美咲", "icons": ["📖", "⚖️"], "base": 2},
    {"name": "望月 さや", "icons": ["📖", "⚖️"], "base": 3},
    {"name": "三浦 真琴", "icons": ["🌏", "🌈"], "base": 2},
    {"name": "Daniel Kim", "icons": ["🌏", "🌈"], "base": 4},
    {"name": "青木 里奈", "icons": ["🌏", "⚖️"], "base": 3},
    {"name": "杉浦 颯太", "icons": ["🌏", "⚖️"], "base": 5},
    {"name": "片山 駿", "icons": ["🌈", "⚖️"], "base": 1},
    {"name": "金子 拓真", "icons": ["🌈", "⚖️"], "base": 3},
    {"name": "Noor Rahman", "icons": ["💚", "📖", "🌏"], "base": 4},
    {"name": "藤田 陽葵", "icons": ["💚", "📖", "🌈"], "base": 4},
    {"name": "Zoe Müller", "icons": ["💚", "📖", "⚖️"], "base": 2},
    {"name": "町田 柚希", "icons": ["💚", "🌏", "🌈"], "base": 3},
    {"name": "Wang Ava", "icons": ["💚", "🌏", "⚖️"], "base": 1},
    {"name": "加藤 佳奈", "icons": ["💚", "🌈", "⚖️"], "base": 5},
    {"name": "清水 友香", "icons": ["📖", "🌏", "🌈"], "base": 1},
    {"name": "佐藤 紗季", "icons": ["📖", "🌏", "⚖️"], "base": 5},
    {"name": "川口 由衣", "icons": ["📖", "🌈", "⚖️"], "base": 3},
    {"name": "Juan Martínez", "icons": ["🌏", "🌈", "⚖️"], "base": 2}
]

# 全てのキャラクターを統合（初期メンバーがCHARACTERS_DBにいなければ追加するため）
# 重複を避けるために名前で管理するか、初期メンバーもDBに含めて扱うかですが、
# ここでは「初期メンバー」も全て `CHARACTERS_DB` に追加して通し番号(index)で管理しやすくします。
for init_char in INITIAL_CHARACTERS:
    # 既に同じ名前の人がいなければ追加
    if not any(c["name"] == init_char["name"] for c in CHARACTERS_DB):
        CHARACTERS_DB.append(init_char)

# --- ✅ 施策データ ---
POLICIES_DB = [
    {"name": "短時間勤務", "target": ["💚"], "cost": 2, "power": 2, "type": ["recruit", "shield", "power"]},
    {"name": "ケア支援（保育/介護補助）", "target": ["💚"], "cost": 2, "power": 2, "type": ["recruit", "shield", "power"]},
    {"name": "ユニーバーサルデザインサポート", "target": ["💚"], "cost": 2, "power": 2, "type": ["shield", "power"]},
    {"name": "各種申請ガイド＆相談窓口", "target": ["💚"], "cost": 1, "power": 0, "type": ["recruit", "shield"]},
    {"name": "男性育休", "target": ["💚"], "cost": 2, "power": 0, "type": ["recruit", "promote", "shield"]},
    {"name": "転勤支援", "target": ["🌏"], "cost": 1, "power": 0, "type": ["recruit", "shield"]},
    {"name": "就労在留支援", "target": ["🌏"], "cost": 1, "power": 0, "type": ["recruit", "shield"]},
    {"name": "LGBTQ+アライコミュニティ", "target": ["🌈"], "cost": 2, "power": 0, "type": ["recruit", "promote", "shield"]},
    {"name": "指導員制度", "target": ["🌈"], "cost": 2, "power": 2, "type": ["promote", "power"]},
    {"name": "清和会", "target": ["⚖️"], "cost": 1, "power": 0, "type": ["shield"]},
    {"name": "ウェルビーイング表彰", "target": ["💚","🌈"], "cost": 2, "power": 2, "type": ["recruit", "shield", "power"]},      
    {"name": "メンター制度", "target": ["💚", "📖"], "cost": 2, "power": 1, "type": ["promote", "shield","power"]},
    {"name": "リターンシップ(復職支援)", "target": ["💚", "📖"], "cost": 2, "power": 0, "type": ["recruit", "promote"]},
    {"name": "復帰ブリッジ（育休/介護）", "target": ["💚", "📖"], "cost": 1, "power": 1, "type": ["promote", "shield", "power"]},
    {"name": "テレワーク・ワーケーション制度", "target": [ "💚","🌏"], "cost": 1, "power": 1, "type": ["recruit", "shield", "power"]},
    {"name": "多言語対応", "target": ["💚","🌏"], "cost": 2, "power": 2, "type": ["recruit", "power"]},
    {"name": "サテライト/在宅手当", "target": ["💚","🌏"], "cost": 1, "power": 1, "type": ["recruit", "shield", "power"]},
    {"name": "障がい者インクルージョンコミュニティ", "target": ["💚", "🌈"], "cost": 2, "power": 0, "type": ["promote", "shield"]},
    {"name": "通勤交通費支給", "target": ["💚", "⚖️"], "cost": 1, "power": 0, "type": ["recruit"]},
    {"name": "1on1", "target": ["📖", "🌏"], "cost": 2, "power": 3, "type": ["shield", "power"]},
    {"name": "アルムナイ/ブーメラン採用", "target": ["📖", "🌏"], "cost": 1, "power": 0, "type": ["recruit", "shield"]},
    {"name": "グローバルタレントマネジメント", "target": ["🌏"], "cost": 3, "power": 3, "type": ["recruit", "promote", "shield", "power"]},
    {"name": "社内公募・FA制度", "target": ["📖", "🌈"], "cost": 2, "power": 1, "type": ["promote", "shield", "power"]},
    {"name": "アンコンシャス・バイアス研修", "target": ["📖", "🌈"], "cost": 2, "power": 0, "type": ["recruit", "shield"]},
    {"name": "DVO(DNP価値目標制度)制度と評価制度", "target": ["📖", "⚖️"], "cost": 1, "power": 0, "type": ["recruit", "promote"]},
    {"name": "キャリア自律支援金の支給", "target": ["📖", "⚖️"], "cost": 3, "power": 3, "type": ["promote", "power"]},
    {"name": "職群別キャリア・スキルマップの可視化", "target": ["📖", "⚖️"], "cost": 1, "power": 1, "type": ["promote", "power"]},
    {"name": "社内複業制度", "target": ["📖", "⚖️"], "cost": 3, "power": 3, "type": ["recruit", "promote", "power"]},
    {"name": "同性パートナーシップ制度", "target": [ "🌈","⚖️"], "cost": 1, "power": 0, "type": ["recruit", "promote", "shield"]},
    {"name": "スポンサーシッププログラム", "target": ["🌈", "⚖️"], "cost": 1, "power": 0, "type": ["promote"]},
    {"name": "面接官トレーニング", "target": ["🌈", "⚖️"], "cost": 1, "power": 0, "type": ["recruit", "promote"]},
    {"name": "インクルージョンループ", "target": ["🌈", "⚖️"], "cost": 3, "power": 3, "type": ["promote", "shield", "power"]},
    {"name": "キャリアサポート休暇・ライフサポート休暇", "target": ["🌈", "⚖️"], "cost": 2, "power": 1, "type": ["shield", "power"]},
    {"name": "施設（社員食堂、診療所、契約保養施設等）の充実", "target": ["🌈", "⚖️"], "cost": 2, "power": 0, "type": ["recruit", "shield"]},
    {"name": "マネジメントフィードバック（360度評価）", "target": ["🌈", "⚖️"], "cost": 1, "power": 0, "type": ["promote", "shield"]},
    {"name": "ミドル・シニア向けキャリア自律支援", "target": ["💚","📖","⚖️"], "cost": 2, "power": 1, "type": ["recruit", "power"]},
    {"name": "オープン・ドア・ルーム（内部通報制度）", "target": ["📖","🌈","⚖️"], "cost": 1, "power": 0, "type": ["shield"]},
    {"name": "タレントマネジメントシステムの活用", "target": ["📖","🌈","🌏"], "cost": 2, "power": 0, "type": ["recruit"]},
]

# ソート用関数（キャッシュ化して高速化）
@st.cache_data
def get_sorted_data():
    def get_sort_key(char):
        num_icons = len(char['icons'])
        sorted_icons = sorted(char['icons'], key=lambda x: SORT_ORDER.index(x) if x in SORT_ORDER else 99)
        priority_indices = tuple(SORT_ORDER.index(icon) if icon in SORT_ORDER else 99 for icon in sorted_icons)
        return (num_icons, priority_indices, char['base'])
    
    sorted_chars = sorted(CHARACTERS_DB, key=get_sort_key)
    sorted_policies = POLICIES_DB
    
    # 初期メンバーが sorted_chars のどのインデックスにいるかを特定する
    init_char_names = [c["name"] for c in INITIAL_CHARACTERS]
    init_indices = [i for i, c in enumerate(sorted_chars) if c["name"] in init_char_names]
    
    return sorted_chars, sorted_policies, init_indices

sorted_chars, sorted_policies, initial_member_indices = get_sorted_data()

# ==========================================
# 1. 状態管理 & 初期セットアップ
# ==========================================
st.title("🎲 DE&I 組織シミュレーター")

# プレースホルダーの作成（タイトルのすぐ下）
scoreboard_placeholder = st.empty()

# セッション状態の初期化
if "is_startup_completed" not in st.session_state:
    st.session_state.is_startup_completed = False 
    
if "selected_char_rows" not in st.session_state:
    st.session_state.selected_char_rows = []
if "selected_policy_rows" not in st.session_state:
    st.session_state.selected_policy_rows = []

if "active_member_indices" not in st.session_state:
    st.session_state.active_member_indices = []

# ==========================================
# 2. フェーズ分岐処理
# ==========================================
active_chars = []
active_policies = []

def sort_icons(icon_set):
    return sorted(list(icon_set), key=lambda x: SORT_ORDER.index(x) if x in SORT_ORDER else 99)

# --- フェーズA: 初期メンバー選択 (2名限定) ---
if not st.session_state.is_startup_completed:
    st.info("🆕 **Step 1: 初期人財カードから最初のメンバーを2名選んでください**")
    
    # 初期メンバーだけを含むデータフレームを作成
    init_chars_data = [sorted_chars[i] for i in initial_member_indices]
    df_chars_init = pd.DataFrame(init_chars_data)
    
    # アイコンをソートして表示
    df_chars_init["選択用リスト"] = df_chars_init.apply(lambda x: f"{''.join(sort_icons(x['icons']))} {x['name']}", axis=1)
    
    selection_event_init = st.dataframe(
        df_chars_init[["選択用リスト"]], 
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row",
        height=350,
        key="df_init_selection" 
    )
    
    # 選択された行(0〜7)を、全体の sorted_chars のインデックスに変換する
    selected_local_rows = selection_event_init.selection.rows
    selected_global_indices = [initial_member_indices[r] for r in selected_local_rows]
    
    if len(selected_global_indices) == 2:
        if st.button("🚀 この2名でスタート！", use_container_width=True, type="primary"):
            st.session_state.active_member_indices = selected_global_indices
            st.session_state.is_startup_completed = True
            st.rerun()
    elif len(selected_global_indices) > 2:
        st.warning(f"⚠️ 選択できるのは2名までです (現在 {len(selected_global_indices)} 名)")
    else:
        st.caption(f"あと {2 - len(selected_global_indices)} 名選んでください")

    active_chars = [] 

# --- フェーズB: メインゲーム (施策 & 追加採用) ---
else:
    with st.expander("⚙️ 施策実行・追加採用 (ここをタップ)", expanded=True):
        tab1, tab2 = st.tabs(["🃏 ① 施策実行", "👥 ② メンバー管理"])

        with tab1:
            st.caption("👇 実施する施策を選んでください")
            
            df_pols = pd.DataFrame(sorted_policies)
            df_pols["施策リスト"] = df_pols.apply(lambda x: f"{''.join(sort_icons(x['target']))} {x['name']}", axis=1)
            
            selection_event_pols = st.dataframe(
                df_pols[["施策リスト"]],
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="multi-row",
                height=300,
                key="df_pols_selection"
            )
            
            selected_pol_indices = selection_event_pols.selection.rows
            active_policies = [sorted_policies[i] for i in selected_pol_indices]
            
            recruit_enabled_icons = set()
            for pol in active_policies:
                if "recruit" in pol["type"]:
                    for t in pol["target"]:
                        recruit_enabled_icons.add(t)
            
            if recruit_enabled_icons:
                icons_str = "".join(sort_icons(recruit_enabled_icons))
                st.info(f"🔓 追加採用可能な属性: {icons_str}")
            else:
                st.warning("⚠️ 「採用」施策を選ぶと、追加メンバーが選べるようになります")

        with tab2:
            st.caption("👇 **「現在参加中」または「採用条件を満たす」メンバーのみ表示されています**")
            st.caption("※ チェックを外すと離脱、チェックを入れると参加します")
            
            display_indices = []
            
            for i, char in enumerate(sorted_chars):
                is_active = i in st.session_state.active_member_indices
                is_recruitable = set(char["icons"]).issubset(recruit_enabled_icons)
                
                if is_active or is_recruitable:
                    display_indices.append(i)
            
            display_data = []
            for idx in display_indices:
                char = sorted_chars[idx]
                is_active = idx in st.session_state.active_member_indices
                display_data.append({
                    "original_index": idx,
                    "参加": is_active,
                    "名前と属性": f"{''.join(sort_icons(char['icons']))} {char['name']}"
                })
                
            df_display = pd.DataFrame(display_data)
            
            if not df_display.empty:
                edited_df = st.data_editor(
                    df_display[["参加", "名前と属性"]],
                    column_config={
                        "参加": st.column_config.CheckboxColumn(
                            "参加状況",
                            help="チェックを入れるとメンバーに参加します",
                            default=False,
                        ),
                        "名前と属性": st.column_config.TextColumn(
                            "メンバー",
                            disabled=True
                        )
                    },
                    disabled=["名前と属性"],
                    hide_index=True,
                    use_container_width=True,
                    height=400,
                    key="editor_member_manage"
                )
                
                checked_rows = [i for i, x in enumerate(edited_df["参加"]) if x]
                new_active_indices_from_display = [df_display.iloc[i]["original_index"] for i in checked_rows]
                
                if set(new_active_indices_from_display) != set(st.session_state.active_member_indices):
                    st.session_state.active_member_indices = new_active_indices_from_display
                    st.rerun()
            else:
                st.info("表示できるメンバーがいません（採用施策を選んでください）")

            st.caption(f"現在 {len(st.session_state.active_member_indices)} 名が参加中")

    active_chars = [sorted_chars[i] for i in st.session_state.active_member_indices]


# ==========================================
# 3. 計算ロジック & 表示 (フェーズB以降のみ実行)
# ==========================================
if st.session_state.is_startup_completed:
    
    total_power = 0
    active_shields = set()
    active_recruits = set()
    active_promotes = set()

    for pol in active_policies:
        if "shield" in pol["type"]:
            for t in pol["target"]: active_shields.add(t)
        if "recruit" in pol["type"]:
            for t in pol["target"]: active_recruits.add(t)
        if "promote" in pol["type"]:
            for t in pol["target"]: active_promotes.add(t)

    char_results = []
    for char in active_chars:
        current_power = char["base"]
        status_tags = []
        
        for pol in active_policies:
            if set(char["icons"]) & set(pol["target"]):
                current_power += pol["power"]
                
        risks = [icon for icon in char["icons"] if icon not in active_shields]
        is_safe = len(risks) == 0 
        
        total_power += current_power
        char_results.append({
            "data": char, "power": current_power, "tags": status_tags, "risks": risks, "is_safe": is_safe
        })

    president_data = {
        "data": {"name": "社長", "icons": ["👑"]},
        "power": 2, "tags": [], "risks": [], "is_safe": True
    }
    total_power += president_data["power"]
    char_results.insert(0, president_data)


    shield_disp = "".join(sort_icons(active_shields)) if active_shields else "ー"
    recruit_disp = "".join(sort_icons(active_recruits)) if active_recruits else "ー"
    promote_disp = "".join(sort_icons(active_promotes)) if active_promotes else "ー"

    # --- スコアボードの描画（プレースホルダーを使用） ---
    scoreboard_html = f"""
    <div class="score-grid">
        <div class="score-item">
            <div class="score-label">🏆 チーム仕事力</div>
            <div class="score-value" style="color:#d32f2f !important; font-size:26px;">{total_power}</div>
        </div>
        <div class="score-item">
            <div class="score-label">🛡️ 離職防止</div>
            <div class="score-value">{shield_disp}</div>
        </div>
        <div class="score-item">
            <div class="score-label">🔵 採用対象</div>
            <div class="score-value">{recruit_disp}</div>
        </div>
        <div class="score-item">
            <div class="score-label">🟢 昇進対象</div>
            <div class="score-value">{promote_disp}</div>
        </div>
        <div class="score-item">
            <div class="score-label">👥 メンバー</div>
            <div class="score-value">{len(char_results)}<span style="font-size:14px">名</span></div>
        </div>
    </div>
    """
    scoreboard_placeholder.markdown(scoreboard_html, unsafe_allow_html=True)

    with st.expander("🎲 サイコロの出目を見る"):
        cols = st.columns(6)
        for i, (num, desc) in enumerate(RISK_MAP_DISPLAY.items()):
            with cols[i]:
                st.markdown(f"**{num}**<br>{desc.replace(' ', '<br>')}", unsafe_allow_html=True)

    st.subheader("📊 組織メンバー")

    if char_results:
        cols = st.columns(3)
        for i, res in enumerate(char_results):
            with cols[i % 3]:
                if res["is_safe"]:
                    border_color = "#00c853"
                    bg_color = "#f1f8e9"
                    status_icon = "🛡️SAFE"
                    footer_text = "✅ 安泰"
                    footer_color = "#2e7d32"
                else:
                    border_color = "#ff5252"
                    bg_color = "#fffbee"
                    status_icon = "⚠️RISK"
                    risk_icons = " ".join(sort_icons(res['risks']))
                    footer_text = f"サイコロを振って {risk_icons} が出たら離職" 
                    footer_color = "#c62828"

                if res['data']['name'] == "社長":
                    status_icon = "👑 社長"
                    footer_text = "鉄壁"

                tags_str = "".join([f"<span style='font-size:12px; border:1px solid #ccc; border-radius:3px; padding:2px 4px; margin-right:3px; background:white; color:#333;'>{t}</span>" for t in res["tags"]])
                
                char_icons_sorted = sort_icons(res["data"]["icons"])
                
                html_card = (
                    f'<div class="member-card" style="border-left: 6px solid {border_color}; background-color: {bg_color};">'
                    f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">'
                    f'  <div style="font-weight:bold; font-size:1.0em; color:{border_color}">{status_icon}</div>'
                    f'  <div style="font-size:0.95em; font-weight:bold; color:#555">力: {res["power"]}</div>'
                    f'</div>'
                    f'<div style="font-weight:bold; font-size:1.2em; margin-bottom:4px; color:#333; display:flex; align-items:center;">'
                    f'{res["data"]["name"]} <span style="font-size:0.9em; margin-left:6px;">{"".join(char_icons_sorted)}</span>'
                    f'</div>'
                    f'<div style="margin-bottom:8px; min-height:18px;">{tags_str}</div>'
                    f'<div style="border-top:1px dashed {border_color}; padding-top:4px; font-size:0.95em; color:{footer_color}; text-align:right; font-weight:bold;">'
                    f'{footer_text}'
                    f'</div>'
                    f'</div>'
                )
                st.markdown(html_card, unsafe_allow_html=True)

    if active_policies:
        st.divider()
        st.subheader("🛠️ 実行施策リスト")
        
        for pol in active_policies:
            ptags = []
            if pol["power"] > 0: ptags.append(f"力+{pol['power']}")
            
            ptags_html = " ".join([f"<span class='tag' style='background:#e8eaf6; color:#3949ab;'>{t}</span>" for t in ptags])
            
            target_sorted = sort_icons(pol['target'])
            
            st.markdown(
                f"""
                <div class="policy-card">
                    <div>
                        <div style="font-weight:bold; color:#333; font-size:1.1em;">{pol['name']}</div>
                        <div style="font-size:0.9em; color:#777;">対象: {"".join(target_sorted)}</div>
                    </div>
                    <div style="text-align:right;">{ptags_html}</div>
                </div>
                """, unsafe_allow_html=True
            )
else:
    pass
