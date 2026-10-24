from extractor import is_rejection


def test_rejection_detected():
    assert is_rejection('{"error": "not_an_invoice"}')


def test_normal_json_is_not_rejection():
    assert not is_rejection('{"invoice_number": "1"}')


def test_garbage_is_not_rejection():
    assert not is_rejection("not json at all")