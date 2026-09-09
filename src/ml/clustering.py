"""
src/ml/clustering.py
=====================================================================
Unified Clustering Module & Facade

Provides backward compatibility and a single entry point for both:
- K-Means Baseline Segmentation (V1, K=3): from src.ml.clustering_v1
- K-Means Competency Stratification (V2, K=4): from src.ml.clustering_v2
"""

import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.dirname(_THIS_DIR)
for _p in (_THIS_DIR, _SRC_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from .clustering_v1 import (
        run_kmeans_clustering,
        load_data,
        audit_data,
        create_features,
        validate_features,
        scale_features,
        evaluate_k,
        fit_kmeans,
        profile_clusters,
        assign_personas,
        generate_visualizations,
        export_results,
    )
    from .clustering_v2 import run_clustering_v2
except (ImportError, ValueError):
    from clustering_v1 import (
        run_kmeans_clustering,
        load_data,
        audit_data,
        create_features,
        validate_features,
        scale_features,
        evaluate_k,
        fit_kmeans,
        profile_clusters,
        assign_personas,
        generate_visualizations,
        export_results,
    )
    from clustering_v2 import run_clustering_v2

__all__ = [
    "run_kmeans_clustering",
    "run_clustering_v2",
    "load_data",
    "audit_data",
    "create_features",
    "validate_features",
    "scale_features",
    "evaluate_k",
    "fit_kmeans",
    "profile_clusters",
    "assign_personas",
    "generate_visualizations",
    "export_results",
]


if __name__ == "__main__":
    print("=" * 80)
    print("RUNNING PRIMARY COMPETENCY CLUSTERING (V2)")
    print("=" * 80)
    run_clustering_v2()

    print("\n" + "=" * 80)
    print("RUNNING BASELINE K-MEANS CLUSTERING (V1)")
    print("=" * 80)
    run_kmeans_clustering()
