"""
Contrast points from existing logistic_predicted_probabilities_*.csv,
CIs bootstrapped from raw per-trial files using the SAME model.
"""
import numpy as np, pandas as pd
import statsmodels.formula.api as smf

PRED_CSV = {  # your existing files
    "coupled": "logistic_predicted_probabilities_original.csv",
    "tol0.2":  "logistic_predicted_probabilities_tol0.2.csv",
    "tol0.3":  "logistic_predicted_probabilities_tol0.3.csv",
}
RAW = {
    "coupled": {"maze1":"rrt_results_maze1_postfix.csv","maze2":"rrt_results_maze2_postfix.csv","maze3":"rrt_results_maze3_postfix.csv"},
    "tol0.2":  {"maze1":"rrt_results_maze1_tol0.2.csv","maze2":"rrt_results_maze2_tol0.2.csv","maze3":"rrt_results_maze3_tol0.2.csv"},
    "tol0.3":  {"maze1":"rrt_results_maze1_tol0.3.csv","maze2":"rrt_results_maze2_tol0.3.csv","maze3":"rrt_results_maze3_tol0.3.csv"},
}
DROP_RR_1=True; STEPS=[0.4,0.5,0.6]; MAZES=["maze1","maze2","maze3"]
TOL=1e-9; B=2000; SEED=0
FORMULA="success ~ C(maze)*C(step_size) + C(maze)*C(random_rate)"

def point_from_csv(path):
    d=pd.read_csv(path)  # cols: maze, step_size, pred_success
    out={}
    for mz in MAZES:
        g=d[d.maze==mz].set_index("step_size")["pred_success"]
        pick=lambda s: g[[k for k in g.index if abs(k-s)<TOL][0]]
        out[mz]=100*(pick(0.5)-0.5*(pick(0.4)+pick(0.6)))
    return out

def load_raw(ds):
    parts=[]
    for mz,p in RAW[ds].items():
        d=pd.read_csv(p); d["success"]=d["path_found"].astype(bool).astype(int); d["maze"]=mz
        parts.append(d[["maze","random_rate","step_size","success"]])
    data=pd.concat(parts,ignore_index=True)
    if DROP_RR_1: data=data[data.random_rate<1.0-TOL].copy()
    return data

def contrast(model,d,mz):
    rates=d[["random_rate"]].drop_duplicates()
    def pc(s):
        g=rates.copy(); g["maze"]=mz; g["step_size"]=s
        return model.predict(g).mean()
    return 100*(pc(0.5)-0.5*(pc(0.4)+pc(0.6)))

rows=[]
for ds in ["coupled","tol0.2","tol0.3"]:
    pts=point_from_csv(PRED_CSV[ds])
    d=load_raw(ds)
    full=smf.logit(FORMULA,data=d).fit(disp=False)
    for mz in MAZES:
        boot_pt=contrast(full,d,mz)
        rng=np.random.default_rng(SEED); boot=[]
        for _ in range(B):
            s=d.sample(len(d),replace=True,random_state=int(rng.integers(1e9)))
            try: boot.append(contrast(smf.logit(FORMULA,data=s).fit(disp=False),s,mz))
            except Exception: pass
        lo,hi=np.percentile(boot,[2.5,97.5])
        rows.append({"dataset":ds,"maze":mz,
            "contrast_from_csv":round(pts[mz],2),
            "contrast_from_fit":round(boot_pt,2),
            "ci_low":round(lo,2),"ci_high":round(hi,2),
            "excludes_zero":bool(lo>0 or hi<0)})
        print(f"{ds:8s} {mz}: csv={pts[mz]:+.1f} fit={boot_pt:+.1f} [{lo:+.1f},{hi:+.1f}]")

pd.DataFrame(rows).to_csv("contrast_results.csv",index=False)
print("\n-> contrast_results.csv (csv vs fit columns should match)")