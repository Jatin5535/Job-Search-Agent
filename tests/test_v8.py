from job_agent.regression import run_regression

def test_regression():
    r=run_regression()
    assert r['guard']['consistent']
    assert 0 <= r['score'] <= 100
