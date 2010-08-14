from calculon import add, op

def test_addition():
    assert add(1,2) == 3, "1 + 2 yields 3"
    
def test_addition_with_op():
    assert op(add, 1,2) == 3, "1 + 2 yields 3"