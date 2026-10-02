# Machine Learning Pipeline Configuration & Constants

RANDOM_SEED = 42

# Numerical features for scaling
NUMERICAL_FEATURES = [
    "listed_price",
    "reference_price",
    "price_deviation_pct",
    "seller_account_age_days",
    "seller_rating",
    "seller_credibility_score",
    "review_count",
    "average_rating",
    "rating_variance",
    "extreme_rating_ratio",
    "one_star_pct",
    "five_star_pct",
    "review_authenticity_signal",
    "desc_length",
    "uppercase_ratio",
    "suspicious_keyword_count",
    "code_verification_count"
]

# Binary / Categorical features
BINARY_FEATURES = [
    "seller_verified",
    "suspicious_review_pattern",
    "code_registered"
]

# Text feature column
TEXT_FEATURE = "product_description"

# TF-IDF Configuration
TFIDF_MAX_FEATURES = 100
TFIDF_NGRAM_RANGE = (1, 2)

# Random Forest Hyperparameter Grid for GridSearchCV
PARAM_GRID_RF = {
    "n_estimators": [50, 100, 150],
    "max_depth": [5, 10, 15, None]
}

# Suspicious keywords for text analysis
SUSPICIOUS_KEYWORDS = [
    "replica", "fake", "copy", "100% original copy", "grade 1a", "mirror quality",
    "oem", "no box", "direct factory", "liquidation", "cheap", "super copy",
    "unauthorized", "parallel import", "overstock clearance"
]
