"""Weekly price history figure for the README: median and 10th-90th percentile band per fuel."""
import sys, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
src = sys.argv[1] if len(sys.argv) > 1 else "data/coruna.csv"
out = sys.argv[2] if len(sys.argv) > 2 else "docs/figures/price_history.png"
df = pd.read_csv(src, sep="|", usecols=["date","station_id","price_goa","price_g95e5","price_glp"], parse_dates=["date"])
print("rows", len(df), "stations", df.station_id.nunique(), "range", df.date.min().date(), df.date.max().date())
fuels = [("price_goa","Diesel (gasóleo A)","#1f5f99"),("price_g95e5","Gasoline 95 E5","#c2571a"),("price_glp","LPG (GLP)","#3a7d44")]
g = df.set_index("date").groupby(pd.Grouper(freq="W"))
fig, ax = plt.subplots(figsize=(11,4.2), dpi=150)
for col,label,c in fuels:
    q = g[col].quantile([.1,.5,.9]).unstack().dropna()
    ax.fill_between(q.index, q[0.1], q[0.9], color=c, alpha=.15, lw=0)
    ax.plot(q.index, q[0.5], color=c, lw=1.6, label=label)
for s in ("top","right"): ax.spines[s].set_visible(False)
ax.set_ylabel("EUR / litre"); ax.grid(axis="y", alpha=.3)
ax.set_title(f"Weekly fuel prices across {df.station_id.nunique()} stations in A Coruña province (median, 10th–90th percentile band)", loc="left", fontsize=11)
ax.legend(frameon=False, loc="upper left", ncol=3)
fig.tight_layout(); fig.savefig(out, facecolor="white")
