import os
import glob
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt


def list_csvs(folder):
    if not os.path.isdir(folder):
        return []
    return sorted(glob.glob(os.path.join(folder, "*.csv")))


def load_csv(path):
    try:
        return pd.read_csv(path)
    except Exception as e:
        st.error(f"Failed to load CSV: {e}")
        return None


def guess_columns(df):
    cols = list(df.columns)
    x_guess = None
    brake_guess = None
    for c in cols:
        lc = c.lower()
        if x_guess is None and ("distance" in lc or "time" in lc):
            x_guess = c
        if brake_guess is None and ("brake" in lc or "brake_pressure" in lc or "brake pressure" in lc):
            brake_guess = c
    # fallbacks
    if x_guess is None:
        for c in cols:
            if pd.api.types.is_numeric_dtype(df[c]):
                x_guess = c
                break
    if brake_guess is None:
        for c in reversed(cols):
            if pd.api.types.is_numeric_dtype(df[c]):
                brake_guess = c
                break
    return x_guess, brake_guess


def prepare_df_for_chart(df, x_col, y_col, name):
    d = df[[x_col, y_col]].copy()
    d = d.dropna()
    d.columns = ["x", "y"]
    d["driver"] = name
    return d


def main():
    st.set_page_config(page_title="Braking Telemetry Overlay", layout="wide")
    st.title("🛑 Braking Telemetry Graph Analysis — MVP")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    trainer_dir = os.path.join(base_dir, "Trainer")
    trainee_dir = os.path.join(base_dir, "Trainee")

    st.sidebar.header("Data Selection")
    trainer_files = list_csvs(trainer_dir)
    trainee_files = list_csvs(trainee_dir)

    if not trainer_files:
        st.sidebar.warning(f"No CSVs found in Trainer folder: {trainer_dir}")
    if not trainee_files:
        st.sidebar.warning(f"No CSVs found in Trainee folder: {trainee_dir}")

    trainer_choice = st.sidebar.selectbox("Trainer file (Driver 1)", options=trainer_files, format_func=lambda p: os.path.basename(p))
    trainee_choice = st.sidebar.selectbox("Trainee file (Driver 2)", options=trainee_files, format_func=lambda p: os.path.basename(p))

    colmap_expander = st.sidebar.expander("Column mapping (auto-detected)", expanded=True)

    trainer_df = load_csv(trainer_choice) if trainer_choice else None
    trainee_df = load_csv(trainee_choice) if trainee_choice else None

    if trainer_df is None or trainee_df is None:
        st.info("Please add CSV files into the Trainer and Trainee folders and re-open this app.")
        return

    # Guess columns
    t_x, t_brake = guess_columns(trainer_df)
    r_x, r_brake = guess_columns(trainee_df)

    with colmap_expander:
        st.markdown("**Trainer (Driver 1) columns**")
        trainer_x = st.selectbox("X axis (trainer)", options=list(trainer_df.columns), index=list(trainer_df.columns).index(t_x) if t_x in trainer_df.columns else 0)
        trainer_brake = st.selectbox("Brake channel (trainer)", options=list(trainer_df.columns), index=list(trainer_df.columns).index(t_brake) if t_brake in trainer_df.columns else 0)

        st.markdown("**Trainee (Driver 2) columns**")
        trainee_x = st.selectbox("X axis (trainee)", options=list(trainee_df.columns), index=list(trainee_df.columns).index(r_x) if r_x in trainee_df.columns else 0)
        trainee_brake = st.selectbox("Brake channel (trainee)", options=list(trainee_df.columns), index=list(trainee_df.columns).index(r_brake) if r_brake in trainee_df.columns else 0)

    # Option to choose common X axis
    st.sidebar.header("Plot Options")
    x_axis_choice = st.sidebar.selectbox("Use X axis", options=["Distance", "Time"], index=0)
    # Map to available columns (prefer containing word)
    def choose_column_by_keyword(df, keyword):
        for c in df.columns:
            if keyword.lower() in c.lower():
                return c
        return None

    if x_axis_choice == "Distance":
        trainer_x = choose_column_by_keyword(trainer_df, "distance") or trainer_x
        trainee_x = choose_column_by_keyword(trainee_df, "distance") or trainee_x
    else:
        trainer_x = choose_column_by_keyword(trainer_df, "time") or trainer_x
        trainee_x = choose_column_by_keyword(trainee_df, "time") or trainee_x

    # Build prepared data
    t_p = prepare_df_for_chart(trainer_df, trainer_x, trainer_brake, "Trainer")
    tr_p = prepare_df_for_chart(trainee_df, trainee_x, trainee_brake, "Trainee")

    # Align / optionally smooth
    smooth = st.sidebar.slider("Smoothing (rolling window, points)", 1, 51, 1, step=2)
    if smooth > 1:
        t_p["y"] = t_p["y"].rolling(smooth, min_periods=1, center=True).mean()
        tr_p["y"] = tr_p["y"].rolling(smooth, min_periods=1, center=True).mean()

    combined = pd.concat([t_p, tr_p], ignore_index=True)

    # Plot with Altair (interactive zoom + pan)
    # Create an interval selection bound to scales so users can drag/zoom and axes will update
    zoom = alt.selection_interval(bind='scales')

    chart = alt.Chart(combined).mark_line().encode(
        x=alt.X('x:Q', title=f"{x_axis_choice}"),
        y=alt.Y('y:Q', title='Brake (units)'),
        color=alt.Color('driver:N', scale=alt.Scale(range=['#f1c40f', '#00bcd4'])),
        tooltip=['driver', 'x', 'y']
    ).add_selection(zoom).properties(width=900, height=400)

    st.subheader("Braking overlay")
    st.markdown("Use mouse wheel or drag on the chart to zoom/pan. Double-click to reset the view.")
    st.altair_chart(chart, use_container_width=True)

    # Summary stats
    st.subheader("Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Trainer — max brake", f"{t_p['y'].max():.2f}")
        st.write("Brake > 0 threshold zones (Trainer):")
        t_zones = get_brake_zones(t_p)
        st.write(t_zones)
    with col2:
        st.metric("Trainee — max brake", f"{tr_p['y'].max():.2f}")
        st.write("Brake > 0 threshold zones (Trainee):")
        tr_zones = get_brake_zones(tr_p)
        st.write(tr_zones)


def get_brake_zones(df, threshold=1e-3):
    # Identify continuous regions where brake > threshold
    arr = df['y'].values
    x = df['x'].values
    if len(arr) == 0:
        return []
    mask = arr > threshold
    zones = []
    in_zone = False
    start_x = None
    for i, m in enumerate(mask):
        if m and not in_zone:
            in_zone = True
            start_x = x[i]
        if not m and in_zone:
            in_zone = Fal