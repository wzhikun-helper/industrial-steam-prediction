"""Byte-preserving export of explicit frozen CSV sources to a new run."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pandas as pd
from src.runtime import create_run_dir, validate_output_dir, project_path, open_new_output
from src.frozen import load_registry, protected_path

SOURCES={
 "Fig1":["results/paper_fig1_target_distribution.csv"],
 "Fig2":["results/paper_fig2_model_performance.csv"],
 "Fig3":["results/paper_fig3_feature_method_comparison.csv","results/paper_fig3_ridge_alpha_sensitivity.csv"],
 "Fig4":["results/paper_fig4_fusion_comparison.csv"],
 "Fig5":["results/paper_fig5_shap_importance.csv"],
 "Fig6":["results/paper_fig6_prediction_diagnostics.csv"],
 "ZH_Table1":["results/paper_fig2_model_performance.csv"],
 "ZH_Table2":["results/paper_fig3_feature_method_comparison.csv"],
 "ZH_Table3":["results/tuning_comparison.csv"],
 "ZH_Table4":["results/paper_fig4_fusion_comparison.csv"],
 "EN_Table1":["results/paper_fig2_model_performance.csv"],
 "EN_Table2":["results/paper_fig3_feature_method_comparison.csv"],
 "EN_Table3":["results/paper_fig4_fusion_comparison.csv"],
}


def export(root,output,*,dry_run=False,sources=None):
    sources=SOURCES if sources is None else sources
    validate_output_dir(root,output)
    registry=load_registry(root)
    payloads={}
    for relative in sorted({p for paths in sources.values() for p in paths}):
        if Path(relative).parts[0]!="results" or Path(relative).suffix!=".csv":
            raise ValueError("Only explicit results CSV sources allowed")
        if relative not in registry:
            raise ValueError(f"Unregistered frozen source: {relative}")
        path=protected_path(root,relative)
        payloads[relative]=path.read_bytes()
        if hashlib.sha256(payloads[relative]).hexdigest()!=registry[relative]:
            raise ValueError(f"Frozen source SHA256 mismatch: {relative}")
    names=[Path(p).name for p in payloads]
    if len(names)!=len(set(names)):
        raise ValueError("Duplicate export basenames")
    if dry_run:
        return {"mode":"dry-run","sources":sources,"files":len(payloads),"frozen_source_identity":"PASS"}
    create_run_dir(root,output)
    try:
        records=[]
        for relative,raw in payloads.items():
            source=pd.read_csv(io.BytesIO(raw))
            destination=project_path(root,output)/Path(relative).name
            with destination.open("xb") as stream:
                stream.write(raw)
            copied=destination.read_bytes()
            if raw!=copied:
                raise ValueError("Copy integrity failure")
            records.append({"source":relative,"output":destination.name,
                "sha256":hashlib.sha256(raw).hexdigest(),"rows":len(source),"columns":list(source.columns),
                "byte_identical":True,"registered_sha256":registry[relative],"frozen_source_identity":"PASS"})
        report={"mapping":sources,"files":records,"status":"PASS"}
        with open_new_output(root,output,"export_manifest.json") as stream:
            json.dump(report,stream,indent=2)
        with open_new_output(root,output,"validation_report.md") as stream:
            stream.write("# Export validation: PASS\n\nByte-identical copies preserve column order, row order, sample counts and numeric precision. See export_manifest.json for source SHA256 and mappings.\n")
        with open_new_output(root,output,"completion.json") as stream:
            json.dump({"status":"complete","files":len(records)},stream)
        return report
    except Exception as error:
        with open_new_output(root,output,"failure.json") as stream:
            json.dump({"status":"failed","message":str(error)},stream)
        raise


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",required=True)
    parser.add_argument("--dry-run",action="store_true")
    args=parser.parse_args()
    print(json.dumps(export(ROOT,args.output_dir,dry_run=args.dry_run),indent=2))
