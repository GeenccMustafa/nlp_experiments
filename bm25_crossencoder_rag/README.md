# BM25 + Cross-Encoder Re-ranking Experiment

This experiment demonstrates a two-stage retrieval system:
- **BM25**: Lexical-based initial retrieval
- **Cross-Encoder**: Transformer-based semantic re-ranking

## How to Run

1. Create the conda environment:
```bash
conda env create -f environment.yml
conda activate bm25_reranker
