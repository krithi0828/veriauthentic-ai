import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

from app.config import DATA_DIR, MODELS_DIR
from ml.model_config import NUMERICAL_FEATURES, BINARY_FEATURES, TEXT_FEATURE, TFIDF_MAX_FEATURES, TFIDF_NGRAM_RANGE
from ml.feature_engineering import engineer_features_df, extract_features_single

def prepare_dataset(raw_csv_path: Path = None, processed_csv_path: Path = None) -> pd.DataFrame:
    if raw_csv_path is None:
        raw_csv_path = DATA_DIR / "raw" / "products_demo.csv"
    if processed_csv_path is None:
        processed_csv_path = DATA_DIR / "processed" / "products_processed.csv"
        
    df_raw = pd.read_csv(raw_csv_path)
    df_processed = engineer_features_df(df_raw)
    
    os_dir = processed_csv_path.parent
    os_dir.mkdir(parents=True, exist_ok=True)
    df_processed.to_csv(processed_csv_path, index=False)
    print(f"Preprocessed dataset saved with {len(df_processed)} rows to {processed_csv_path}")
    return df_processed

def get_preprocessor():
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERICAL_FEATURES),
            ("text", TfidfVectorizer(max_features=TFIDF_MAX_FEATURES, ngram_range=TFIDF_NGRAM_RANGE), TEXT_FEATURE),
            ("bin", "passthrough", BINARY_FEATURES)
        ],
        remainder="drop"
    )
    return preprocessor
