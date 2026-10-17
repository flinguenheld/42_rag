#!/usr/bin/env bash

CACHE_FOLDER="${HOME}/goinfre/rag_cache/"

export UV_PROJECT_ENVIRONMENT="${CACHE_FOLDER}.venv"
export HF_HUB_CACHE="${CACHE_FOLDER}hugging_face"
export HF_HOME="${CACHE_FOLDER}hugging_face"
export UV_CACHE_DIR="${CACHE_FOLDER}uv"
export UV_LINK_MODE="copy"
export TREE_SITTER_LANGUAGE_PACK_CACHE_DIR="${CACHE_FOLDER}tree_sitter"
