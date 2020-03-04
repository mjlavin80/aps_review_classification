from sklearn.metrics import cohen_kappa_score
rater1 = ["single", "single", "not_single", "single", "single", "single", "not_single", "single", "not_single", "not_single"]
rater2 = ["single", "single", "not_single", "single", "single", "single", "not_single", "single", "not_single", "single"]

# the kappa expresses how much better than chance the agreement was
print(cohen_kappa_score(rater1, rater2))

# 0 poor
# 0.2 slight
# 0.4 fair
# 0.6 moderate
# 0.8 substantial 
# 1.0 perfect agreement

# however, with this few observations, one mistake can bump us from .78 to .58!

rater1 = ["single", "single", "not_single", "single", "single", "single", "not_single", "single", "not_single", "not_single"]
rater2 = ["single", "not_single", "not_single", "single", "single", "single", "not_single", "single", "not_single", "single"]

print(cohen_kappa_score(rater1, rater2))
