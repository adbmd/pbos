"""
Train Google News using the same parameter as table 6

To be specific,
    Method = KVQ-FH
    F = 0.50M
    H = 0.04M

"""

from pathlib import Path

from datasets.google import prepare_google_paths
from datasets.polyglot_emb import prepare_polyglot_emb_paths
from datasets.ws_bench import BENCHS, prepare_bench_paths, prepare_combined_query_path
from sasaki_utils import train, inference, get_latest_in_dir, prepare_codecs_path
from ws_eval import eval_ws

epoch = 20


def exp(ref_vec_path, embed_dim, result_path):
    codecs_path = prepare_codecs_path(ref_vec_path, result_path)
    train(
        ref_vec_path,
        result_path,
        codecs_path=codecs_path,
        H=40_000,
        F=500_000,
        embed_dim=embed_dim,
        epoch=epoch,
    )

    result_path = get_latest_in_dir(result_path / "sep_kvq")
    model_path = result_path / f"model_epoch_{epoch}"

    combined_query_path = prepare_combined_query_path()
    inference(model_path, codecs_path, combined_query_path)
    result_emb_path = result_path / f"inference_embedding_epoch{epoch}" / "embedding.txt"

    for name in BENCHS:
        bench_paths = prepare_bench_paths(name)
        eval_ws(bench_paths.txt_path, result_emb_path, lower=True)
        eval_ws(bench_paths.txt_path, result_emb_path, lower=False)


for name, ref_vec_path, embed_dim in [
    ("polyglot", prepare_polyglot_emb_paths("en").w2v_path, 64),
    ("google_news", prepare_google_paths().w2v_path, 300),
]:
    result_path = Path(".") / "results" / "sasaki" / f"ws_{name}"
    exp(ref_vec_path, embed_dim, result_path)
