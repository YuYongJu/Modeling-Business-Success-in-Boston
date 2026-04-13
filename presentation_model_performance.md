# Model Performance — Presentation Content

Drop-in content for **Slides 4–5 (Results & Insights)**.
All numbers come from `src/modeling.py` on the cleaned Boston DBA dataset
(3,720 businesses after filtering, 69.9% active / 30.1% closed).

---

## Slide 4 — Can we predict which businesses will close?

**The problem:** Given a business's neighborhood and category at the time it
opens, can we predict whether it will eventually close?

**What we tried:** Two classifiers from class — **K-Nearest Neighbors (k=5)**
and **Logistic Regression** — using only features known *before* opening
(zip code, business category, latitude, longitude).

**Baseline to beat:** 69.9% — that's what you get by always guessing "Active."

| Model | Accuracy | Precision | Recall | F1 |
|---|---|---|---|---|
| KNN (k=5) | **66.9%** | 42.6% | 28.1% | **0.34** |
| Logistic Regression | 69.9% | 0% | 0% | 0.00 |

**What this actually means:**

- **Logistic Regression "won" on accuracy but learned nothing.** It hit the
  baseline by predicting *every* business would stay open. Precision and
  recall are zero — it never identifies a closed business. This is a textbook
  warning about why accuracy alone is misleading on imbalanced data.
- **KNN is the more honest model.** It scores *worse* on accuracy but actually
  finds about 28% of the businesses that close, with 43% of its "will close"
  predictions being correct. Its F1 of 0.34 is modest but real.
- **The real takeaway:** Location and category alone are weak predictors of
  closure. To do meaningfully better, we'd need features like revenue,
  staffing, foot traffic, or rent — none of which are in a public DBA
  registry. *That* is the insight worth presenting: the easy public-data
  features are not enough to forecast success.

---

## Slide 5 — How long will a business last? + Where do they cluster?

### Linear Regression — predicting business duration

**Question:** Given neighborhood and business category, can we predict how
many years a business will operate?

| Metric | Value | Interpretation |
|---|---|---|
| **R²** | 0.0006 | Explains essentially **0%** of the variance |
| **MAE** | 2.72 years | Off by ~2.7 years on average |
| Mean duration | 5.0 years | Range: 0 – 12.7 years |

**In plain English:** Knowing a business's neighborhood and category tells us
*almost nothing* about how long it will last. An R² of 0.0006 means our model
is no better than just guessing the average duration for every business.

**Why this is still a useful finding:** It's a negative result that disproves
a common assumption — that "where you open" determines longevity in any
predictable way at the public-data level. Longevity depends on factors not in
the registry (management, capital, product-market fit).

### K-Means Clustering — finding geographic business zones

**Question:** Are there natural geographic clusters of businesses in Boston,
and do some clusters do better than others?

**How we picked k:** We tested k=3 through k=8 using **silhouette score**
(higher = better-separated clusters). k=4 won with a silhouette of **0.6031**,
which indicates well-defined clusters.

| Cluster | # Businesses | Survival Rate | Avg Duration | Avg Diversity |
|---|---|---|---|---|
| 0 | 1,431 | **71.0%** | 5.1 yr | 11.2 |
| 1 | 1,079 | **72.5%** | 5.0 yr | 10.6 |
| 2 | 345 | 66.1% | 5.4 yr | 9.2 |
| 3 | 865 | 66.4% | 4.8 yr | 10.7 |

**What we discovered:** Survival varies by **6 percentage points** across
geographic clusters (66% → 73%). The two best-performing clusters also have
the highest neighborhood *diversity* (more business types nearby), hinting
that mixed-use commercial zones support business survival better than
single-use districts.

### Bonus — Diversity vs survival

| Local diversity | # Businesses | Survival Rate |
|---|---|---|
| Low (0–8 categories) | 175 | 68.6% |
| Medium (9–10) | 826 | 67.7% |
| High (11–12) | 2,719 | **70.7%** |

A small but consistent edge for businesses in commercially diverse areas.

---

## Slide 6 — One-line takeaways

1. **The easy features aren't enough.** Location and category alone can't
   reliably predict whether a Boston business will close — both classifiers
   barely beat (or fail to beat) a "predict majority class" baseline.
2. **Longevity is not a function of geography.** R² ≈ 0 for predicting
   duration from neighborhood + category.
3. **But geography still matters at the cluster level.** K-Means found four
   real geographic zones, and businesses in mixed-use, high-diversity zones
   survive 4–6 percentage points more often than those in low-diversity
   areas.
4. **Honest negative results are insights too.** Our findings tell future
   researchers and policymakers where to *not* look for predictive signal —
   and that more granular data (rent, revenue, traffic) is required to do
   better.
