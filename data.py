FOLDER_PROCESSED = "./data/processed/"
FOLDER_BM25 = "bm25"
FILE_CHUNKS = "chunks.json"
FOLDER_RAW = "./data/raw/"

# Trade-off: more sources = correct source more often in the prompt,
# but more noise for the 0.6B model (measured: 3000 is a good balance)
# SOURCE_MAX_TOKENS = 4000
SOURCE_MAX_TOKENS = 3000
# SOURCE_MAX_TOKENS = 2000
