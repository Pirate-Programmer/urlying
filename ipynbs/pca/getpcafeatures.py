import numpy as np
import joblib
import pandas as pd

scaler = joblib.load("scaler.pkl")
eigvecs = np.load("eigvecs_95.npy")   
# eigvecs = np.load("eigvecs_90.npy")   

#extract these features and put in model
X_new = pd.DataFrame({
    "dots": [2],
    "equals": [4],
    "slashes": [5],
    "hyphens": [5],
    "colons": [1],
    "question_marks": [1],
    "digits": [23],
    "and": [3],
    "underscore": [5],
    "tilde": [0],
    "percent": [8],
    "lowercase": [168],
    "uppercase": [0],
    "upper_to_lower_ratio": [0],
    "is_https": [0],
    "url_length": [231],
    "domain_length": [17],
    "path_length": [53],
    "path_depth": [3],
    "query_length": [153],
    "query_count": [4],
    "fragment_length": [0],
    "se_url": [4.86],
    "se_domain": [3.45],
    "se_path": [4.25],
    "se_query": [4.61],
    "cte_domain": [3.75],
    "subdomains": [1],
    "special_chars": [6],
    "digit_to_length_ratio": [0.1],
    "char_to_length_ratio": [0.73],
    "specialchar_to_length_ratio": [0.03],
})

X_new_scaled = scaler.transform(X_new)
X_new_pca = X_new_scaled.dot(eigvecs)
df_new_pca = pd.DataFrame(X_new_pca, columns=[f"PC{i+1}" for i in range(eigvecs.shape[1])])
print(df_new_pca)
