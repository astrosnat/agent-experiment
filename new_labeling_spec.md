Define a label ontology with namespaces and exclusivity rules.
descriptor.asset_class and descriptor.region are exclusive groups. exposure.trend, exposure.carry, behavior.mean_reversion, risk.high_volatility, behavior.crisis_convexity, and similar labels are non-exclusive and should be probabilities, not strings. Every label record should include name, probability, active, window, evidence, source, confidence, and version. This is the minimum needed for a real multilabel system with calibratable outputs.
LabelRecord = {
    "name": "exposure.trend",
    "probability": 0.82,
    "active": True,
    "window": "252d",
    "source": "weak_supervision+classifier_chain",
    "confidence": "medium",
    "evidence": [
        "trend_beta_252d=0.41",
        "pnl_slope_252d=+0.9_sigma"
    ],
    "version": "labels_v2"
}
Build the feature layer properly.
Inputs should include standardized net returns, factor and benchmark returns, optional holdings or positions, turnover, leverage, holding period, and metadata. Features should be computed over multiple windows such as 20/60/252 days and normalized within peer groups. For style inference, use factor regressions or returns-based style analysis to estimate exposure to equity beta, rates duration, curve, carry, credit, FX, commodity, and trend/momentum rather than guessing from text fields. Trend and carry are established as distinct styles, so they should be separate exposure channels, not aliases for average return or Sharpe.
Generate weak labels instead of pretending your first heuristic is ground truth.
For each semantic label, write several labeling functions that can vote positive, negative, or abstain. Example: trend_like_252d votes positive if trend-factor beta is high and PnL slope is positive; carry_like votes positive if roll, yield, or basis features are persistently strong; mean_reversion_20d votes positive if short-lag autocorrelation is materially negative and the reversion fit is stable. Systems like Snorkel exist specifically to combine noisy, correlated heuristics into probabilistic training labels without requiring you to hand-label everything.
Train an actual multilabel model on those probabilistic targets.
Baseline: one-vs-rest binary models for each label. Better: an ensemble of classifier chains or a native multi-output learner, because multilabel problems often have correlated labels and classifier chains are designed to exploit that dependence instead of assuming every label is independent. Calibrate the resulting probabilities before thresholding them. Scikit-learn’s own example shows classifier chains beating the naive independent baseline on multilabel tasks, and it provides cross-validated calibration tools for probability outputs.
Keep unsupervised families as a sidecar, not the main taxonomy.
Fit a GMM or HDBSCAN on the same feature space or on a learned embedding, and store latent_family_probs as soft memberships. If you want a human-readable hierarchy, add agglomerative clustering for dendrogram-style grouping. This lets the computer discover latent structure without confusing cluster IDs with semantic labels like trend, carry, or mean reversion. Those are different jobs.
Evaluate it like a multilabel system.
Track per-label precision/recall and average precision, sample-level Jaccard for set overlap, and ranking metrics such as LRAP if you care about ordered scores. Also check calibration and label stability across rolling windows. If a label flips constantly or is poorly calibrated, it is not production-ready even if the point estimate looks clever.

The shortest practical migration path from your current file is simple: delete carry_proxy_label(), replace factor_exposure_labels() with measured factor exposures, make every label function return {score, probability, abstain, evidence, window} instead of a bare string, add peer-normalized multi-horizon features, then train a real multilabel model on weak labels and keep a separate soft-cluster family vector for discovery and search. That would be recognizably “Experiment A done properly” instead of a dressed-up bucketizer.Well