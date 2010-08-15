from calculon import sub, op

def test_subtraction():
    assert sub(1,2) == -1, '1 - 2 yields -1'
    
def test_subtraction_with_op():
    assert op(op, 1,2) == 3, '1 + 2 yields 3'