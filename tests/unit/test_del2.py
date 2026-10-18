

def test_log_target_wrapper_recovers_multiplicative_means():
    import numpy as np
    import pandas as pd
    from culinarystate.transition.baselines import D2ProcessMean, LogTarget
    df = pd.DataFrame({"process": ["boil"] * 2 + ["dry"] * 2, "y": [0.5, 2.0, 1.0, 1.0], "y_lower": [None] * 4,
                       "censored": [False] * 4})
    m = LogTarget(D2ProcessMean()).fit(df)
    assert np.allclose(m.predict(df.iloc[[0]]), [1.0])          # geometric mean of 0.5 and 2.0
    assert m.name == "D2_process_mean+log"
