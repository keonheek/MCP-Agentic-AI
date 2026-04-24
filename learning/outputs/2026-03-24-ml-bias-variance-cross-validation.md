# ML/Deep Learning — Bias-Variance, Train/Val/Test, Cross-Validation
_Track 4 | Week 1 | Date: 2026-03-24_

---

## Concept (10 min read)

### What went wrong in your Samsung model

Your Samsung stock prediction model used Linear Regression on historical price data. If you trained on the full dataset and checked the error on that same data, the model looks accurate — but that accuracy is fake. It memorized the data, not the pattern.

This is the core problem bias-variance addresses.

---

### Bias vs. Variance

**Bias** = the model is too simple to capture the real pattern.
- It underfits. Error is high on both training and new data.
- Example: fitting a straight line to Samsung's price when the trend clearly curves over time.

**Variance** = the model is too complex, so it chases the noise in training data.
- It overfits. Error is low on training data, high on new data.
- Example: a 15-degree polynomial that perfectly follows every price wiggle from 2020-2023 but completely falls apart predicting 2024.

The tradeoff: as you add complexity, bias drops but variance rises. You want the middle — low enough complexity to generalize, high enough to capture real signal.

In your Samsung project, Linear Regression sits on the high-bias side. That is why its R² looked decent but predictions drifted when you moved past the training window.

---

### Train / Validation / Test Split

The fix is to hold out data the model never sees during training, and evaluate on that.

- **Train set** (70-80%): what the model learns from.
- **Validation set** (10-15%): what you use to tune hyperparameters or compare models. You look at this.
- **Test set** (10-15%): what you use exactly once, at the end, to report final performance. You do not look at this while building.

For time series (Samsung prices), random shuffling breaks temporal order. You must split by time — train on older data, test on recent data.

---

### Cross-Validation

With small datasets, a single train/val split is noisy. K-Fold cross-validation solves this:

1. Split data into K folds (typically 5 or 10).
2. Train on K-1 folds, validate on the remaining fold.
3. Repeat K times, each fold gets a turn as validation.
4. Average the K scores — this is your real model performance.

Result: you use all your data for training AND get a reliable validation signal. The variance in your score estimate drops significantly.

Note: for time series, use `TimeSeriesSplit` instead of standard `KFold` — it preserves temporal order.

---

## Key Terms

- **Bias**: error from a model being too simple to fit the data. High bias = underfitting.
- **Variance**: error from a model being too sensitive to training data noise. High variance = overfitting.
- **Generalization**: how well a model performs on data it has never seen.
- **Train/val/test split**: dividing a dataset into three non-overlapping partitions with distinct roles.
- **K-Fold cross-validation**: rotating validation scheme across K subsets of training data to get a stable performance estimate.
- **Learning curve**: plot of training vs. validation error as training set size grows — diagnoses bias/variance.
- **TimeSeriesSplit**: sklearn's cross-validation variant that respects temporal order — required for stock/financial data.

---

## Working Code

```python
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import (
    train_test_split, KFold, TimeSeriesSplit, cross_val_score
)
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import make_pipeline

# --- 1. Load Samsung data (005930.KS) ---
df = yf.download("005930.KS", start="2020-01-01", end="2024-12-31")
df = df[["Close"]].dropna().copy()

# Simple lag features — same approach as your Samsung project
for lag in [1, 5, 10, 20]:
    df[f"lag_{lag}"] = df["Close"].shift(lag)
df.dropna(inplace=True)

X = df.drop(columns=["Close"]).values
y = df["Close"].values


# --- 2. Train/Test Split (time-aware — NO shuffle) ---
split_idx = int(len(X) * 0.8)
X_train, X_test = X[:split_idx], X[split_idx:]
y_train, y_test = y[:split_idx], y[split_idx:]

model = LinearRegression()
model.fit(X_train, y_train)

train_rmse = mean_squared_error(y_train, model.predict(X_train), squared=False)
test_rmse  = mean_squared_error(y_test,  model.predict(X_test),  squared=False)

print(f"Train RMSE: {train_rmse:,.0f} KRW")
print(f"Test  RMSE: {test_rmse:,.0f} KRW")
# If test RMSE >> train RMSE → high variance (overfitting)
# If both are high             → high bias  (underfitting)


# --- 3. TimeSeriesSplit Cross-Validation ---
tscv = TimeSeriesSplit(n_splits=5)
pipe = make_pipeline(StandardScaler(), LinearRegression())

cv_scores = cross_val_score(
    pipe, X, y,
    cv=tscv,
    scoring="neg_root_mean_squared_error"
)
cv_rmse = -cv_scores  # flip sign

print(f"\nCV RMSE per fold: {cv_rmse.round(0)}")
print(f"Mean CV RMSE:     {cv_rmse.mean():,.0f} KRW")
print(f"Std  CV RMSE:     {cv_rmse.std():,.0f} KRW")
# High std across folds = high variance model


# --- 4. Learning Curve — diagnose bias/variance visually ---
train_sizes = np.linspace(0.1, 1.0, 10)
train_rmses, val_rmses = [], []

for size in train_sizes:
    n = max(int(len(X_train) * size), 20)
    X_sub, y_sub = X_train[:n], y_train[:n]

    m = LinearRegression()
    m.fit(X_sub, y_sub)

    train_rmses.append(
        mean_squared_error(y_sub, m.predict(X_sub), squared=False)
    )
    val_rmses.append(
        mean_squared_error(y_test, m.predict(X_test), squared=False)
    )

plt.figure(figsize=(9, 5))
plt.plot(train_sizes, train_rmses, label="Train RMSE", marker="o")
plt.plot(train_sizes, val_rmses,   label="Val RMSE",   marker="s")
plt.xlabel("Training set fraction")
plt.ylabel("RMSE (KRW)")
plt.title("Learning Curve — Samsung LinearRegression")
plt.legend()
plt.tight_layout()
plt.savefig("samsung_learning_curve.png", dpi=120)
plt.show()

# Reading the plot:
# Both curves converge at HIGH error → high bias → try more features or a richer model
# Large gap between train and val    → high variance → simplify or add regularization
```

---

## Exercises

**1. Apply proper time-aware train/test split to your Samsung dataset**

Your original Samsung project likely used `train_test_split(shuffle=True)` or trained/evaluated on the same data. Rerun it with a strict chronological split (80% train, 20% test, no shuffle). Compare the RMSE you get now to the original number. The difference tells you how much your original evaluation was inflated.

**2. Compare a single split vs. cross-validation on the same Samsung data**

Run `cross_val_score` with `TimeSeriesSplit(n_splits=5)` and compare the mean CV RMSE to your single holdout RMSE. If they are close, your single split was representative. If they diverge, the single split was misleading — and you now have a more honest estimate.

**3. Challenge — detect overfitting in your existing Linear Regression**

Add polynomial features to your Samsung model using `sklearn.preprocessing.PolynomialFeatures(degree=3)` inside a pipeline. Plot the learning curve for degree=1 (current) vs. degree=3. Observe what happens to the train/val gap as degree increases. Find the degree where the gap is smallest — that is the sweet spot for this dataset.

```python
from sklearn.preprocessing import PolynomialFeatures

for degree in [1, 2, 3, 5]:
    pipe = make_pipeline(
        PolynomialFeatures(degree),
        StandardScaler(),
        LinearRegression()
    )
    scores = cross_val_score(
        pipe, X, y, cv=TimeSeriesSplit(n_splits=5),
        scoring="neg_root_mean_squared_error"
    )
    print(f"Degree {degree} | CV RMSE: {-scores.mean():,.0f} ± {scores.std():,.0f}")
```

---

## Resource

- Primary: ML Zoomcamp Week 1 — https://github.com/DataTalks-Club/machine-learning-zoomcamp
- sklearn cross-validation docs — https://scikit-learn.org/stable/modules/cross_validation.html
- sklearn TimeSeriesSplit — https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html

---

## Cross-Apply

**FinAgent distress model** (`projects/consulting-emulation/models/distress_model.py`): Any classification model predicting financial distress is a classic overfitting target — limited labeled examples, many financial ratios as features. Apply `StratifiedKFold` (preserves class balance) instead of standard KFold. The train/val gap in that model is likely large; regularized Logistic Regression or a shallow tree with `max_depth=3` will generalize better than the default.

**RAGAS evaluation splits**: When you eventually run RAGAS on FinAgent's RAG pipeline, the same principle applies — never evaluate retrieval quality on the same chunks you used to build the index. Hold out a test set of Q&A pairs before indexing. This is the RAG equivalent of a test split. (RAGAS is on hold per cost policy, but the mental model transfers now.)
