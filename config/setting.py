"""Backward-compatible constants; prefer `config.settings.get_settings()`."""

from config.settings import get_settings

_s = get_settings()

LLM_MODEL: str = _s.llm_model
EMBEDDING_MODEL: str = _s.embedding_model
TEMPERATURE: float = _s.temperature
K_RESULTS: int = _s.k_results
SAVE_PATH: str = _s.faiss_index_path

DEFAULT_LOCATION: str = _s.default_location
SEARCH_ENGINE: str = "google_maps"
LANGUAGE: str = _s.search_language
COUNTRY: str = _s.search_country
GOOGLE_DOMAIN: str = _s.google_domain
MAX_RESULTS: int = _s.food_max_results

PDF_PATH: str = r"data\www-etrip4u-com-du-lich-thong-tin-tong-quat-ve-du-lich-nha-trang.pdf"
