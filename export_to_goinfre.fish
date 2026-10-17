#!/usr/bin/env fish

set -l cache_folder "$HOME/goinfre/rag_cache"

set -gx UV_PROJECT_ENVIRONMENT "$cache_folder/.venv"
set -gx HF_HUB_CACHE "$cache_folder/hugging_face"
set -gx HF_HOME "$cache_folder/hugging_face"
set -gx UV_CACHE_DIR "$cache_folder/uv"
set -gx UV_LINK_MODE copy
set -gx TREE_SITTER_LANGUAGE_PACK_CACHE_DIR "$cache_folder/tree_sitter"
