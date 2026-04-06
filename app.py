from __future__ import annotations

from pathlib import Path
import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Explorador de Enlace Químico",
    page_icon="🧪",
    layout="wide",
)


BASE_DIR = Path(__file__).parent

possible_paths = [
    BASE_DIR / "data" / "master_elements_118.csv",
    BASE_DIR / "master_elements_118.csv",
]

DATA_PATH = None
for p in possible_paths:
    if p.exists():
        DATA_PATH = p
        break

if DATA_PATH is None:
    raise FileNotFoundError(
        "No se encontró master_elements_118.csv ni en la raíz ni en la carpeta data/."
    )


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["group"] = df["group"].astype("Int64")
    df["period"] = df["period"].astype("Int64")
    return df.sort_values("atomic_number").reset_index(drop=True)


DF = load_data()
NAME_MAP = dict(zip(DF["symbol"], DF["name"]))
SYMBOLS = DF["symbol"].tolist()


DEFAULT_A = "Na"
DEFAULT_B = "Cl"

defaults = {
    "element_a": DEFAULT_A,
    "element_b": DEFAULT_B,
    "tab_element_a": DEFAULT_A,
    "tab_element_b": DEFAULT_B,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def get_row(symbol: str) -> pd.Series:
    return DF.loc[DF["symbol"] == symbol].iloc[0]


METAL_CATEGORIES = {
    "Alkali metal",
    "Alkaline earth metal",
    "Transition metal",
    "Post-transition metal",
    "Lanthanide",
    "Actinide",
}
NONMETAL_CATEGORIES = {"Nonmetal", "Halogen", "Noble gas"}


EXAMPLES = {
    "Na + Cl": ("Na", "Cl"),
    "H + Cl": ("H", "Cl"),
    "C + O": ("C", "O"),
    "Cu + Cu": ("Cu", "Cu"),
    "Si + O": ("Si", "O"),
}


def sync_from_sidebar() -> None:
    st.session_state["tab_element_a"] = st.session_state["element_a"]
    st.session_state["tab_element_b"] = st.session_state["element_b"]


def sync_from_tab() -> None:
    st.session_state["element_a"] = st.session_state["tab_element_a"]
    st.session_state["element_b"] = st.session_state["tab_element_b"]


def set_example(a: str, b: str) -> None:
    st.session_state["element_a"] = a
    st.session_state["element_b"] = b
    st.session_state["tab_element_a"] = a
    st.session_state["tab_element_b"] = b


for label, (a, b) in EXAMPLES.items():
    if st.sidebar.button(label, use_container_width=True):
        set_example(a, b)


row_a = get_row(st.session_state["element_a"])
row_b = get_row(st.session_state["element_b"])


st.markdown(
    """
    <style>
    .card {
        border: 1px solid rgba(49, 51, 63, 0.2);
        border-radius: 16px;
        padding: 1rem 1rem 0.8rem 1rem;
        margin-bottom: 0.8rem;
        background: rgba(250, 250, 250, 0.02);
    }
    .result-box {
        border-radius: 16px;
        padding: 1rem;
        margin: 0.5rem 0 1rem 0;
        border-left: 7px solid #4f46e5;
        background: rgba(79, 70, 229, 0.08);
    }
    .small-note {
        color: #6b7280;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.sidebar.title("⚙️ Control de análisis")
st.sidebar.caption("Selecciona dos elementos o usa uno de los ejemplos rápidos.")
st.sidebar.selectbox(
    "Elemento A",
    options=SYMBOLS,
    key="element_a",
    format_func=lambda s: f"{s} — {NAME_MAP[s]}",
    on_change=sync_from_sidebar,
)
st.sidebar.selectbox(
    "Elemento B",
    options=SYMBOLS,
    key="element_b",
    format_func=lambda s: f"{s} — {NAME_MAP[s]}",
    on_change=sync_from_sidebar,
)

# Refresh rows after possible sidebar selection
row_a = get_row(st.session_state["element_a"])
row_b = get_row(st.session_state["element_b"])


def is_metal(category: str) -> bool:
    return category in METAL_CATEGORIES



def is_nonmetal(category: str) -> bool:
    return category in NONMETAL_CATEGORIES



def is_metalloid(category: str) -> bool:
    return category == "Metalloid"



def fmt(value: object, decimals: int = 3, unit: str = "") -> str:
    if pd.isna(value):
        return "No disponible"
    if isinstance(value, (int, np.integer)):
        return f"{int(value)}{unit}"
    if isinstance(value, (float, np.floating)):
        return f"{value:.{decimals}f}{unit}"
    return str(value)



def coverage_badge(coverage: str) -> tuple[str, str]:
    mapping = {
        "full": ("🟢", "Análisis completo"),
        "pauling_only": ("🟡", "Solo Pauling"),
        "limited_atomic_data": ("🔴", "Solo ficha atómica"),
    }
    return mapping.get(coverage, ("🟡", "Cobertura parcial"))



def pauling_delta(a: pd.Series, b: pd.Series) -> float | None:
    if pd.isna(a["pauling_en"]) or pd.isna(b["pauling_en"]):
        return None
    return abs(float(a["pauling_en"]) - float(b["pauling_en"]))



def classify_pauling(a: pd.Series, b: pd.Series) -> tuple[str, str]:
    if a["symbol"] == b["symbol"]:
        if is_metal(a["category"]):
            return "Enlace metálico", "Ambos átomos son del mismo metal; domina la deslocalización electrónica típica del enlace metálico."
        return "Enlace covalente no polar", "Se trata del mismo elemento, por lo que la compartición electrónica es esencialmente simétrica."

    if is_metal(a["category"]) and is_metal(b["category"]):
        return "Enlace metálico", "Ambos elementos son metales; predomina el carácter metálico con electrones relativamente deslocalizados."

    delta = pauling_delta(a, b)
    if delta is None:
        if (is_metal(a["category"]) and is_nonmetal(b["category"])) or (
            is_metal(b["category"]) and is_nonmetal(a["category"])
        ):
            return "Probable interacción iónica o polar", "La pareja metal–no metal sugiere transferencia parcial o alta polarización, pero falta electronegatividad de Pauling para clasificar con rigor."
        if is_metalloid(a["category"]) or is_metalloid(b["category"]):
            return "Interacción intermedia", "Hay al menos un metaloide y no hay suficiente información de Pauling para concluir con firmeza."
        return "Datos insuficientes", "No hay valores de Pauling suficientes para esta pareja."

    if (is_metal(a["category"]) and is_nonmetal(b["category"])) or (
        is_metal(b["category"]) and is_nonmetal(a["category"])
    ):
        if delta >= 1.7:
            return "Enlace iónico", "La combinación metal–no metal y la alta diferencia de electronegatividad favorecen transferencia electrónica."
        return "Enlace covalente polar con carácter iónico", "Es una pareja metal–no metal, pero la diferencia de electronegatividad no es tan extrema; se espera polarización importante."

    if delta < 0.4:
        return "Enlace covalente no polar", "La diferencia de electronegatividad es muy pequeña y favorece una compartición electrónica aproximadamente simétrica."
    if delta < 1.7:
        return "Enlace covalente polar", "La diferencia de electronegatividad indica compartición desigual de densidad electrónica."
    return "Enlace iónico", "La diferencia de electronegatividad es alta y sugiere fuerte separación de carga."



def classify_mulliken(a: pd.Series, b: pd.Series) -> tuple[str, str]:
    ma = a["mulliken_en_ev"]
    mb = b["mulliken_en_ev"]
    if pd.isna(ma) or pd.isna(mb):
        return (
            "No evaluable con Mulliken",
            "Este método requiere energía de ionización y afinidad electrónica utilizables para ambos elementos.",
        )

    delta = abs(float(ma) - float(mb))
    if delta < 1.0:
        level = "Polarización baja"
        desc = "La asimetría electrónica calculada por Mulliken es reducida; la atracción de electrones entre ambos átomos es relativamente parecida."
    elif delta < 3.0:
        level = "Polarización intermedia"
        desc = "La diferencia de Mulliken sugiere desigualdad apreciable en la atracción electrónica."
    else:
        level = "Polarización alta"
        desc = "La diferencia de Mulliken respalda una fuerte tendencia a la polarización o transferencia de densidad electrónica."

    if is_metal(a["category"]) and is_metal(b["category"]):
        level = "Tendencia metálica / baja polarización"
        desc = "Ambos elementos son metales; incluso con Mulliken, la interpretación dominante sigue siendo de carácter metálico."

    return level, desc



def arkel_data(a: pd.Series, b: pd.Series) -> dict | None:
    dchi = pauling_delta(a, b)
    if dchi is None:
        return None
    avg = (float(a["pauling_en"]) + float(b["pauling_en"])) / 2.0

    ionic = min(max(dchi / 4.0, 0.0), 1.0)
    covalent = min(max((avg / 4.0) * (1.0 - ionic), 0.0), 1.0)
    metallic = min(max(((4.0 - avg) / 4.0) * (1.0 - ionic), 0.0), 1.0)

    if is_metal(a["category"]) and is_metal(b["category"]):
        metallic += 0.30
    elif is_nonmetal(a["category"]) and is_nonmetal(b["category"]):
        covalent += 0.20
    elif (is_metal(a["category"]) and is_nonmetal(b["category"])) or (
        is_metal(b["category"]) and is_nonmetal(a["category"])
    ):
        ionic += 0.20
    elif is_metalloid(a["category"]) or is_metalloid(b["category"]):
        covalent += 0.08
        metallic += 0.08

    total = ionic + covalent + metallic
    ionic /= total
    covalent /= total
    metallic /= total

    vertices = {
        "metálico": np.array([0.0, 0.0]),
        "covalente": np.array([1.0, 0.0]),
        "iónico": np.array([0.5, math.sqrt(3) / 2]),
    }

    point = metallic * vertices["metálico"] + covalent * vertices["covalente"] + ionic * vertices["iónico"]
    dominant = max(
        [("metálico", metallic), ("covalente", covalent), ("iónico", ionic)],
        key=lambda item: item[1],
    )[0]

    return {
        "delta": dchi,
        "average": avg,
        "metallic": metallic,
        "covalent": covalent,
        "ionic": ionic,
        "point": point,
        "dominant": dominant,
    }



def plot_arkel_triangle(data: dict) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6.6, 5.6))
    h = math.sqrt(3) / 2
    triangle = np.array([[0, 0], [1, 0], [0.5, h], [0, 0]])
    ax.plot(triangle[:, 0], triangle[:, 1], linewidth=2)

    ax.fill([0, 1, 0.5], [0, 0, h], alpha=0.08)
    ax.scatter(data["point"][0], data["point"][1], s=180, zorder=5)
    ax.annotate(
        "Pareja seleccionada",
        xy=(data["point"][0], data["point"][1]),
        xytext=(8, 10),
        textcoords="offset points",
        fontsize=10,
    )

    ax.text(-0.03, -0.05, "Metálico", fontsize=12, ha="left", va="top")
    ax.text(1.03, -0.05, "Covalente", fontsize=12, ha="right", va="top")
    ax.text(0.5, h + 0.04, "Iónico", fontsize=12, ha="center", va="bottom")

    ax.text(0.50, -0.11, "↑ electronegatividad promedio", fontsize=10, ha="center")
    ax.text(0.86, 0.42, "↑ Δχ", fontsize=10, rotation=60)

    ax.set_xlim(-0.08, 1.08)
    ax.set_ylim(-0.14, h + 0.12)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    return fig



def expected_properties(primary_label: str) -> list[str]:
    if "iónico" in primary_label.lower():
        return [
            "Alta separación de carga y fuerte interacción electrostática.",
            "Tendencia a formar sólidos cristalinos con altos puntos de fusión.",
            "Conductividad eléctrica principalmente en estado fundido o en disolución.",
            "Frecuente solubilidad en disolventes polares.",
        ]
    if "metálico" in primary_label.lower():
        return [
            "Electrones relativamente deslocalizados en la red cristalina.",
            "Buena conductividad térmica y eléctrica.",
            "Maleabilidad, ductilidad y brillo metálico característicos.",
            "Ausencia de una molécula discreta en el sentido covalente clásico.",
        ]
    if "polar" in primary_label.lower():
        return [
            "Compartición desigual de densidad electrónica.",
            "Presencia de dipolos de enlace y posible reactividad polar.",
            "Propiedades muy sensibles a la geometría molecular global.",
            "Conductividad generalmente baja en fase sólida o líquida pura.",
        ]
    return [
        "Compartición electrónica aproximadamente simétrica.",
        "Baja polarización intrínseca del enlace.",
        "Frecuente formación de moléculas discretas o redes covalentes.",
        "Conductividad usualmente baja, salvo excepciones estructurales.",
    ]



def build_conclusion(a: pd.Series, b: pd.Series) -> str:
    primary, why = classify_pauling(a, b)
    mull_label, mull_desc = classify_mulliken(a, b)
    arkel = arkel_data(a, b)

    pieces = [
        f"La interpretación predominante para {a['symbol']}–{b['symbol']} es **{primary.lower()}**.",
        why,
        f"Desde Mulliken, el resultado se resume como **{mull_label.lower()}**, lo que {mull_desc[0].lower() + mull_desc[1:]}",
    ]

    if arkel is not None:
        pieces.append(
            f"En el diagrama conceptual inspirado en Arkel–Ketelaar, la pareja cae hacia la región **{arkel['dominant']}**, con Δχ = {arkel['delta']:.3f} y χ̄ = {arkel['average']:.3f}."
        )
    else:
        pieces.append(
            "No es posible ubicar la pareja en el diagrama de Arkel–Ketelaar porque falta al menos un valor de electronegatividad de Pauling."
        )

    return " ".join(pieces)


st.title("🧪 Explorador interactivo de enlace químico")
st.caption(
    "Analiza cualquier pareja de elementos de la tabla periódica mediante electronegatividad (Pauling y Mulliken) y un diagrama conceptual inspirado en Arkel–Ketelaar."
)

summary_col1, summary_col2, summary_col3 = st.columns(3)
summary_col1.metric("Elemento A", f"{row_a['symbol']} — {row_a['name']}")
summary_col2.metric("Elemento B", f"{row_b['symbol']} — {row_b['name']}")
summary_col3.metric("Cobertura disponible", f"{row_a['app_method_coverage']} / {row_b['app_method_coverage']}")


tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "1. Introducción",
        "2. Selección de elementos",
        "3. Resultado por electronegatividad",
        "4. Arkel–Ketelaar",
        "5. Conclusión científica",
    ]
)

with tab1:
    st.subheader("¿Qué hace esta aplicación?")
    st.write(
        "Esta app permite seleccionar **cualquier pareja de elementos** de la tabla periódica y estudiar su interacción desde dos enfoques de electronegatividad y una visualización conceptual del carácter de enlace."
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            """
            <div class="card">
            <h4>Métodos usados</h4>
            <ul>
              <li><b>Pauling:</b> comparación directa de electronegatividades para estimar polaridad y tipo de enlace.</li>
              <li><b>Mulliken:</b> respaldo teórico basado en energía de ionización y afinidad electrónica.</li>
              <li><b>Arkel–Ketelaar:</b> representación didáctica del balance entre carácter iónico, covalente y metálico.</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="card">
            <h4>Qué información muestra</h4>
            <ul>
              <li>Ficha atómica de cada elemento.</li>
              <li>Electronegatividades y diferencias.</li>
              <li>Clasificación principal del enlace.</li>
              <li>Interpretación visual del carácter químico.</li>
              <li>Conclusión científica con propiedades esperadas.</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.info(
        "La app distingue entre **análisis completo**, **análisis parcial** y **ficha atómica sin datos suficientes**. Así evita inventar valores cuando una fuente no reporta cierta propiedad."
    )

    st.markdown("### Leyenda de cobertura")
    st.write("🟢 Análisis completo: hay datos suficientes para Pauling, Mulliken y la visualización conceptual.")
    st.write("🟡 Cobertura parcial: puede faltar afinidad electrónica o parte de la información analítica.")
    st.write("🔴 Ficha atómica: el elemento aparece en la tabla, pero no hay suficientes datos para todos los métodos.")

with tab2:
    st.subheader("Selección y ficha comparativa")
    left, right = st.columns(2)

    with left:
        st.selectbox(
            "Elemento A",
            options=SYMBOLS,
            key="tab_element_a",
            format_func=lambda s: f"{s} — {NAME_MAP[s]}",
            on_change=sync_from_tab,
        )
    with right:
        st.selectbox(
            "Elemento B",
            options=SYMBOLS,
            key="tab_element_b",
            format_func=lambda s: f"{s} — {NAME_MAP[s]}",
            on_change=sync_from_tab,
        )

    row_a = get_row(st.session_state["element_a"])
    row_b = get_row(st.session_state["element_b"])

    def element_card(row: pd.Series) -> None:
        emoji, text = coverage_badge(row["app_method_coverage"])
        st.markdown(f"### {row['symbol']} — {row['name']}")
        st.markdown(f"**Cobertura analítica:** {emoji} {text}")
        st.markdown(
            f"""
            <div class="card">
            <b>Número atómico:</b> {row['atomic_number']}<br>
            <b>Grupo:</b> {fmt(row['group'], decimals=0)}<br>
            <b>Período:</b> {fmt(row['period'], decimals=0)}<br>
            <b>Bloque:</b> {row['block']}<br>
            <b>Categoría:</b> {row['category']}<br>
            <b>Configuración electrónica:</b> {row['electron_configuration']}<br>
            <b>Estado estándar:</b> {row['standard_state'] if not pd.isna(row['standard_state']) else 'No disponible'}<br>
            <b>Masa atómica:</b> {fmt(row['atomic_mass_u'], 4, ' u')}<br>
            <b>Radio atómico:</b> {fmt(row['atomic_radius_pm'], 1, ' pm')}<br>
            <b>Electronegatividad de Pauling:</b> {fmt(row['pauling_en'], 3)}<br>
            <b>Primera energía de ionización:</b> {fmt(row['first_ionization_energy_ev'], 3, ' eV')}<br>
            <b>Afinidad electrónica:</b> {fmt(row['electron_affinity_ev'], 3, ' eV')}<br>
            <b>Electronegatividad de Mulliken:</b> {fmt(row['mulliken_en_ev'], 3, ' eV')}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if isinstance(row["notes"], str) and row["notes"].strip():
            st.caption(f"Nota de datos: {row['notes']}")

    card_left, card_right = st.columns(2)
    with card_left:
        element_card(row_a)
    with card_right:
        element_card(row_b)

with tab3:
    row_a = get_row(st.session_state["element_a"])
    row_b = get_row(st.session_state["element_b"])
    st.subheader("Escalas de electronegatividad")

    st.markdown("### A. Escala de Pauling")
    delta_p = pauling_delta(row_a, row_b)
    p_label, p_desc = classify_pauling(row_a, row_b)

    c1, c2, c3 = st.columns(3)
    c1.metric(f"χₚ ({row_a['symbol']})", fmt(row_a["pauling_en"], 3))
    c2.metric(f"χₚ ({row_b['symbol']})", fmt(row_b["pauling_en"], 3))
    c3.metric("Δχ (Pauling)", fmt(delta_p, 3) if delta_p is not None else "No disponible")

    if delta_p is not None:
        pauling_chart = pd.DataFrame(
            {
                "Electronegatividad de Pauling": [float(row_a["pauling_en"]), float(row_b["pauling_en"])]
            },
            index=[row_a["symbol"], row_b["symbol"]],
        )
        st.bar_chart(pauling_chart)
    else:
        st.warning("No hay valores de Pauling suficientes para ambos elementos.")

    st.markdown(
        f"""
        <div class="result-box">
        <b>Clasificación principal:</b> {p_label}<br>
        {p_desc}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Rangos didácticos usados con Pauling: Δχ < 0.4 → covalente no polar; 0.4 ≤ Δχ < 1.7 → covalente polar; Δχ ≥ 1.7 → iónico. El caso metal–metal se interpreta como enlace metálico.")

    st.markdown("### B. Escala de Mulliken")
    st.latex(r"\chi_M = \frac{IE + EA}{2}")

    m_label, m_desc = classify_mulliken(row_a, row_b)
    delta_m = None
    if not pd.isna(row_a["mulliken_en_ev"]) and not pd.isna(row_b["mulliken_en_ev"]):
        delta_m = abs(float(row_a["mulliken_en_ev"]) - float(row_b["mulliken_en_ev"]))

    m1, m2, m3 = st.columns(3)
    m1.metric(f"χₘ ({row_a['symbol']})", fmt(row_a["mulliken_en_ev"], 3, " eV"))
    m2.metric(f"χₘ ({row_b['symbol']})", fmt(row_b["mulliken_en_ev"], 3, " eV"))
    m3.metric("Δχ (Mulliken)", fmt(delta_m, 3, " eV") if delta_m is not None else "No disponible")

    with st.expander("Ver desglose de IE y EA"):
        table = pd.DataFrame(
            {
                "Símbolo": [row_a["symbol"], row_b["symbol"]],
                "IE (eV)": [row_a["first_ionization_energy_ev"], row_b["first_ionization_energy_ev"]],
                "EA (eV)": [row_a["electron_affinity_ev"], row_b["electron_affinity_ev"]],
                "χ_M (eV)": [row_a["mulliken_en_ev"], row_b["mulliken_en_ev"]],
            }
        )
        st.dataframe(table, use_container_width=True, hide_index=True)

    st.markdown(
        f"""
        <div class="result-box">
        <b>Lectura de Mulliken:</b> {m_label}<br>
        {m_desc}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info(
        "En esta app, Mulliken se usa como **respaldo teórico** para describir la tendencia a atraer electrones. La clasificación principal del tipo de enlace se basa en Pauling y en la naturaleza de los elementos seleccionados."
    )

with tab4:
    row_a = get_row(st.session_state["element_a"])
    row_b = get_row(st.session_state["element_b"])
    st.subheader("Diagrama conceptual inspirado en Arkel–Ketelaar")
    st.caption("Esta visualización es didáctica: usa Δχ de Pauling y electronegatividad promedio para mostrar si la pareja se acerca más al carácter iónico, covalente o metálico.")

    arkel = arkel_data(row_a, row_b)
    if arkel is None:
        st.warning("No se puede ubicar esta pareja en el diagrama porque falta al menos un valor de electronegatividad de Pauling.")
    else:
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Δχ", f"{arkel['delta']:.3f}")
        p2.metric("χ̄", f"{arkel['average']:.3f}")
        p3.metric("Dominio", arkel["dominant"].capitalize())
        p4.metric("Pareja", f"{row_a['symbol']}–{row_b['symbol']}")

        c1, c2 = st.columns([1.2, 1])
        with c1:
            st.pyplot(plot_arkel_triangle(arkel), use_container_width=True)
        with c2:
            st.markdown(
                f"""
                <div class="card">
                <b>Pesos relativos</b><br><br>
                Carácter iónico: {arkel['ionic']*100:.1f}%<br>
                Carácter covalente: {arkel['covalent']*100:.1f}%<br>
                Carácter metálico: {arkel['metallic']*100:.1f}%
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(float(arkel["ionic"]), text=f"Iónico {arkel['ionic']*100:.1f}%")
            st.progress(float(arkel["covalent"]), text=f"Covalente {arkel['covalent']*100:.1f}%")
            st.progress(float(arkel["metallic"]), text=f"Metálico {arkel['metallic']*100:.1f}%")

        st.write(
            f"Para la pareja **{row_a['symbol']}–{row_b['symbol']}**, el punto cae hacia la región **{arkel['dominant']}**, lo que sugiere que ese carácter domina en la interacción analizada."
        )

with tab5:
    row_a = get_row(st.session_state["element_a"])
    row_b = get_row(st.session_state["element_b"])
    st.subheader("Síntesis científica")
    primary_label, _ = classify_pauling(row_a, row_b)

    st.markdown(
        f"""
        <div class="result-box">
        {build_conclusion(row_a, row_b)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Propiedades que cabría esperar")
    for prop in expected_properties(primary_label):
        st.write(f"• {prop}")

    st.markdown("### Observación sobre calidad de datos")
    st.write(
        "La app siempre muestra la ficha de los 118 elementos, pero solo ejecuta cada método cuando las propiedades necesarias están disponibles en el conjunto de datos."
    )

    with st.expander("Ver fuentes incluidas en el CSV"):
        src_table = pd.DataFrame(
            {
                "Elemento": [row_a["symbol"], row_b["symbol"]],
                "Fuente base": [row_a["source_core_url"], row_b["source_core_url"]],
                "Fuente analítica": [row_a["source_analytics_url"], row_b["source_analytics_url"]],
                "Validación": [row_a["source_validation_url"], row_b["source_validation_url"]],
            }
        )
        st.dataframe(src_table, use_container_width=True, hide_index=True)
