"""One model loader for every GPU step: bf16 weights at a pinned revision, SDPA attention, left padding.
Replaces the FP8 loader of the sealed runs. Settings come from
config/run.json; nothing here may change between the first bf16 run and the clean run."""
import json, os, sys, time
from pathlib import Path

R = Path(__file__).resolve().parent.parent                 # replication/
CFG = json.load(open(R / "config" / "run.json", encoding="utf-8"))
MODELS = {k: v["id"] for k, v in CFG["models"].items()}  # the run models: every per-model step loops over these
REF = next(iter(MODELS))                                    # reference model (first in config): qwen in the shipped configuration
# Judge models that are not run models; loadable, never looped over.
_ALL = {**CFG.get("judge_models", {}), **CFG["models"]}
ALL_MODELS = {k: v["id"] for k, v in _ALL.items()}
REVISION = {v["id"]: v["revision"] for v in _ALL.values()}
TEMPLATE_KW = {v["id"]: v["chat_template_kwargs"] for v in _ALL.values() if v.get("chat_template_kwargs")}   # e.g. Qwen3 enable_thinking=False


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def batch(name):
    """Fixed batch size of a step (config/run.json "batch")."""
    return int(CFG["batch"][name])


def free_ram_gb():
    import psutil
    return psutil.virtual_memory().available / 2**30


def ram_guard(need_gb=None, max_wait_s=3 * 3600):
    need_gb = CFG["ram_guard_gb"] if need_gb is None else need_gb
    t0 = time.time()
    while free_ram_gb() < need_gb:
        if time.time() - t0 > max_wait_s:
            raise SystemExit(f"RAM guard: < {need_gb} GB free for {max_wait_s}s")
        log(f"RAM guard: {free_ram_gb():.1f} GB free, waiting"); time.sleep(60)


def deterministic():
    """Bitwise-reproducible GPU computation. Without it, two identical s1 runs on the H200 sampled different texts
    (13-22% identical responses; tools/det_test.py: 59% without, 100% with). Needs CUBLAS_WORKSPACE_CONFIG=:4096:8 in the environment
    before CUDA starts (run_pipeline.py sets it); an operation without a deterministic implementation raises instead of running."""
    import torch
    if os.environ.get("CUBLAS_WORKSPACE_CONFIG") not in (":4096:8", ":16:8"):
        raise SystemExit("set CUBLAS_WORKSPACE_CONFIG=:4096:8 (run_pipeline.py does) for deterministic cuBLAS")
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False


def cap_gpu():
    """Per-process VRAM cap in GB (several processes share one GPU; their caps sum below the card). Also turns on deterministic mode."""
    import torch
    deterministic()
    total = torch.cuda.get_device_properties(0).total_memory / 2**30
    gb = float(os.environ.get("GPU_GB", CFG["gpu_gb_per_process"]))      # run_pipeline.py sets GPU_GB per step (memory budget)
    torch.cuda.set_per_process_memory_fraction(min(1.0, gb / total), 0)


def revision_of(model_id):
    if model_id not in REVISION:
        raise SystemExit(f"model {model_id} has no pinned revision in config/run.json")
    return REVISION[model_id]


def load_model(model_id):
    import torch
    from transformers import AutoModelForCausalLM
    assert CFG["precision"] == "bf16", CFG["precision"]
    m = AutoModelForCausalLM.from_pretrained(model_id, revision=revision_of(model_id), dtype=torch.bfloat16,
                                             attn_implementation="sdpa", device_map={"": 0})
    m.eval()
    return m


def template_defaults(tok, model_id):
    """Fixed chat-template arguments of a model (config "chat_template_kwargs"), applied to every apply_chat_template call of this
    tokenizer; callers may not override them. No entry (Qwen2.5, Llama): the tokenizer is returned unchanged."""
    kw = TEMPLATE_KW.get(model_id)
    if kw and not getattr(tok, "_template_kw", None):
        orig = tok.apply_chat_template
        def act(*a, **k):
            for x, y in kw.items():
                if k.setdefault(x, y) != y:
                    raise SystemExit(f"{model_id}: chat template argument {x} is fixed to {y} by config/run.json")
            return orig(*a, **k)
        tok.apply_chat_template = act; tok._template_kw = kw
    return tok


def load_tokenizer(model_id):
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model_id, revision=revision_of(model_id)); tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    return template_defaults(tok, model_id)


def load(key):
    """bf16 model + tokenizer for a model key (a run model or a judge model)."""
    import torch
    cap_gpu(); ram_guard()
    mid = ALL_MODELS[key]
    tok, model = load_tokenizer(mid), load_model(mid)
    log("loaded", mid, f"bf16 rev {revision_of(mid)[:8]} | layers {model.config.num_hidden_layers} | GPU {torch.cuda.memory_allocated()/2**30:.1f} GB")
    return tok, model


def pin_from_pretrained():
    """For Kim's congress_map scripts run unchanged through runpy: they already load bf16 (01:37, 03:75); this only adds the pinned
    revision to every from_pretrained call (model and tokenizer) and applies the GPU cap and RAM guard."""
    import transformers
    cap_gpu(); ram_guard()
    for cls in (transformers.AutoModelForCausalLM, transformers.AutoTokenizer):
        orig = cls.from_pretrained.__func__ if hasattr(cls.from_pretrained, "__func__") else cls.from_pretrained
        def wrapped(c, model_id, *a, _orig=orig, _tok=cls is transformers.AutoTokenizer, **kw):
            kw.setdefault("revision", revision_of(model_id))
            obj = _orig(c, model_id, *a, **kw)
            return template_defaults(obj, model_id) if _tok else obj
        cls.from_pretrained = classmethod(wrapped)


def oom_stop(step, exc):
    """an out-of-memory error stops the step; batches are never lowered (they change outputs)."""
    raise SystemExit(f"{step}: CUDA out of memory at the fixed batch; free GPU memory and rerun the step from scratch ({exc})")


def shard_of(n_items, shard):
    """Row range of shard 'i/n' (contiguous blocks). Only batch-1 steps are sharded, so outputs do not depend on n."""
    if not shard:
        return 0, n_items
    i, n = map(int, shard.split("/"))
    assert 0 <= i < n, shard
    step = -(-n_items // n)
    return i * step, min(n_items, (i + 1) * step)
