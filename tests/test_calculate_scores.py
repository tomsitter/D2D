import calculate_scores as cs

def test_calculate_scores():

    filename = 'data/pss.test.deid.csv'

    result = cs.calc_score(emr='accuro', filename=filename, field='Md Physician #')

    assert len(result.keys()) == 4
