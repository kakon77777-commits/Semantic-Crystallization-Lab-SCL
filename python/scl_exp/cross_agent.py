from __future__ import annotations

import numpy as np
import torch
from torch import nn

from .model import encode_batch


def symbol_feature_signature(model, tokenizer, symbol: str, max_len: int) -> np.ndarray:
    batch = encode_batch(tokenizer, [symbol], max_len=max_len)
    model.eval()
    with torch.no_grad():
        _, logits = model(batch["input_ids"], batch["attention_mask"])
        probs = torch.sigmoid(logits)[0]
    return probs.detach().cpu().numpy().astype(float)


def align_symbol_to_signature(
    model,
    tokenizer,
    symbol: str,
    target_signature,
    *,
    epochs: int = 80,
    lr: float = 0.015,
    max_len: int = 384,
) -> dict:
    if symbol not in tokenizer.vocab:
        raise ValueError(f"symbol not in vocabulary: {symbol}")
    target = torch.tensor(np.asarray(target_signature, dtype=float), dtype=torch.float32).reshape(1, -1)
    if target.shape[1] != model.feature_prototypes.shape[0]:
        raise ValueError("target signature width does not match feature count")

    for p in model.parameters():
        p.requires_grad_(False)
    model.token_embedding.weight.requires_grad_(True)
    sid = tokenizer.vocab[symbol]
    before = model.token_embedding.weight.detach().clone()
    grad_mask = torch.zeros_like(model.token_embedding.weight)
    grad_mask[sid] = 1.0
    hook = model.token_embedding.weight.register_hook(lambda grad: grad * grad_mask)
    batch = encode_batch(tokenizer, [symbol], max_len=max_len)
    optimizer = torch.optim.Adam([model.token_embedding.weight], lr=float(lr))
    criterion = nn.BCEWithLogitsLoss()
    losses = []
    model.train()
    try:
        for _ in range(int(epochs)):
            optimizer.zero_grad(set_to_none=True)
            _, logits = model(batch["input_ids"], batch["attention_mask"])
            loss = criterion(logits, target)
            loss.backward()
            optimizer.step()
            losses.append(float(loss.detach().cpu()))
    finally:
        hook.remove()
    model.eval()
    after = model.token_embedding.weight.detach().clone()
    delta = torch.linalg.vector_norm(after - before, dim=1).cpu().numpy()
    non_symbol = np.delete(delta, sid)
    return {
        "symbol": symbol,
        "epochs": int(epochs),
        "learning_rate": float(lr),
        "loss_start": losses[0] if losses else None,
        "loss_end": losses[-1] if losses else None,
        "symbol_embedding_l2_change": float(delta[sid]),
        "max_non_symbol_embedding_change": float(non_symbol.max()) if len(non_symbol) else 0.0,
    }
