"""
EDA (Exploratory Data Analysis) Module
Lightweight EDA that prints summary statistics without mutating the data.
"""

import os
import logging
from typing import Dict, Optional

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from .config import LOCAL_OUTPUT_DIR

log = logging.getLogger("alumni_pipeline")


class EDASummary:
    """
    Lightweight EDA that prints summary statistics without mutating the data.
    Generates one multi-panel figure saved to LOCAL_OUTPUT_DIR.
    """

    def run(self, raw: Dict[str, pd.DataFrame]) -> None:
        log.info("=== EDA SUMMARY ===")
        self._print_dataset_overview(raw)
        self._analyze_alumni_people(raw.get("alumni_people"))
        self._analyze_work_locations(raw.get("work_locations"))
        self._analyze_student_scores(raw.get("student_scores"))
        self._plot_eda(raw)

    # ── individual analyses ───────────────────────────────────────────────────
    @staticmethod
    def _print_dataset_overview(raw: Dict[str, pd.DataFrame]) -> None:
        print("\n" + "─" * 60)
        print("  DATASET INVENTORY")
        print("─" * 60)
        for name, df in raw.items():
            missing_pct = df.isnull().mean().mean() * 100
            print(f"  {name:<25}  {len(df):>5} rows  {df.shape[1]:>3} cols  "
                  f"missing={missing_pct:.1f}%")

    @staticmethod
    def _analyze_alumni_people(df: Optional[pd.DataFrame]) -> None:
        if df is None:
            return
        print("\n── alumni_people ──")
        print(f"  Total alumni recorded : {len(df)}")
        if "cinsiyet" in df.columns:
            gender_counts = df["cinsiyet"].value_counts()
            print(f"  Gender distribution  : {gender_counts.to_dict()}")
        if "title" in df.columns:
            top_titles = df["title"].value_counts().head(5)
            print("  Top 5 job titles:")
            for title, cnt in top_titles.items():
                print(f"    {cnt:>3}  {title}")
        if "company" in df.columns:
            n_missing = df["company"].isnull().sum()
            print(f"  Companies with missing data: {n_missing} ({n_missing/len(df):.0%})")

    @staticmethod
    def _analyze_work_locations(df: Optional[pd.DataFrame]) -> None:
        if df is None:
            return
        print("\n── work_locations ──")
        if "kişi" in df.columns and "kurum" in df.columns:
            top = df.nlargest(5, "kişi")[["kurum", "kişi"]]
            print("  Top 5 employers by alumni count:")
            for _, row in top.iterrows():
                print(f"    {row['kişi']:>3}  {row['kurum']}")

    @staticmethod
    def _analyze_student_scores(df: Optional[pd.DataFrame]) -> None:
        if df is None:
            return
        print("\n── student_scores ──")
        if "ORTALAMA" in df.columns:
            s = df["ORTALAMA"]
            print(f"  GPA — mean={s.mean():.2f}  median={s.median():.2f}  "
                  f"std={s.std():.2f}  min={s.min():.2f}  max={s.max():.2f}")
        if "SINIF" in df.columns:
            print(f"  Class distribution: {df['SINIF'].value_counts().to_dict()}")

    @staticmethod
    def _plot_eda(raw: Dict[str, pd.DataFrame]) -> None:
        fig = plt.figure(figsize=(18, 10))
        fig.suptitle("EDA Summary — Alumni Dataset", fontsize=15, fontweight="bold", y=1.01)
        gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

        # Panel 1: dataset sizes
        ax1 = fig.add_subplot(gs[0, 0])
        names = list(raw.keys())
        sizes = [len(raw[n]) for n in names]
        colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(names)))
        ax1.barh(names, sizes, color=colors)
        ax1.set_xlabel("Row count")
        ax1.set_title("Dataset Sizes")
        ax1.tick_params(axis="y", labelsize=7)

        # Panel 2: alumni job title distribution
        alumni = raw.get("alumni_people")
        ax2 = fig.add_subplot(gs[0, 1])
        if alumni is not None and "title" in alumni.columns:
            top_t = alumni["title"].value_counts().head(8)
            ax2.barh(top_t.index[::-1], top_t.values[::-1],
                     color=plt.cm.plasma(np.linspace(0.2, 0.8, len(top_t))))
            ax2.set_title("Top Job Titles")
            ax2.tick_params(axis="y", labelsize=7)
        else:
            ax2.text(0.5, 0.5, "No data", ha="center", va="center")
            ax2.set_title("Top Job Titles")

        # Panel 3: employer distribution
        wl = raw.get("work_locations")
        ax3 = fig.add_subplot(gs[0, 2])
        if wl is not None and "kişi" in wl.columns and "kurum" in wl.columns:
            top_w = wl.nlargest(8, "kişi")
            ax3.barh(top_w["kurum"].values[::-1], top_w["kişi"].values[::-1],
                     color=plt.cm.coolwarm(np.linspace(0.2, 0.8, len(top_w))))
            ax3.set_title("Top Employers (alumni count)")
            ax3.tick_params(axis="y", labelsize=7)
        else:
            ax3.text(0.5, 0.5, "No data", ha="center", va="center")
            ax3.set_title("Top Employers")

        # Panel 4: GPA distribution
        ss = raw.get("student_scores")
        ax4 = fig.add_subplot(gs[1, 0])
        if ss is not None and "ORTALAMA" in ss.columns:
            ax4.hist(ss["ORTALAMA"].dropna(), bins=25, color="#4C72B0",
                     edgecolor="white", linewidth=0.5)
            ax4.axvline(ss["ORTALAMA"].mean(), color="tomato", ls="--", label="Mean")
            ax4.set_xlabel("GPA (ORTALAMA)")
            ax4.set_title("GPA Distribution")
            ax4.legend(fontsize=8)
        else:
            ax4.text(0.5, 0.5, "No data", ha="center", va="center")
            ax4.set_title("GPA Distribution")

        # Panel 5: gender by year (genders table)
        gdf = raw.get("genders")
        ax5 = fig.add_subplot(gs[1, 1])
        if gdf is not None and "Unnamed: 0" in gdf.columns:
            year_cols = [c for c in gdf.columns if c.isdigit()]
            if year_cols:
                row = gdf[gdf["Unnamed: 0"].str.lower().str.contains("kiz-pc", na=False)]
                if not row.empty:
                    vals = row[year_cols].iloc[0].values
                    ax5.plot(year_cols, vals, marker="o", color="orchid", label="Female")
                row2 = gdf[gdf["Unnamed: 0"].str.lower().str.contains("erkek-pc", na=False)]
                if not row2.empty:
                    vals2 = row2[year_cols].iloc[0].values
                    ax5.plot(year_cols, vals2, marker="s", color="steelblue", label="Male")
                ax5.set_title("Gender Enrollment by Year")
                ax5.legend(fontsize=8)
        else:
            ax5.text(0.5, 0.5, "No data", ha="center", va="center")
            ax5.set_title("Gender Enrollment by Year")

        # Panel 6: missing value heatmap
        ax6 = fig.add_subplot(gs[1, 2])
        miss_pct = {n: df.isnull().mean().mean() * 100 for n, df in raw.items()}
        miss_df = pd.DataFrame(miss_pct, index=["missing_%"]).T.sort_values("missing_%")
        ax6.barh(miss_df.index, miss_df["missing_%"],
                 color=["#d73027" if v > 20 else "#fee090" if v > 5 else "#91cf60"
                        for v in miss_df["missing_%"]])
        ax6.set_xlabel("Missing %")
        ax6.set_title("Missing Data by Dataset")
        ax6.tick_params(axis="y", labelsize=7)

        out_path = os.path.join(LOCAL_OUTPUT_DIR, "01_eda_summary.png")
        plt.savefig(out_path, dpi=150, bbox_inches="tight")
        plt.close()
        log.info("  EDA figure saved → %s", out_path)
