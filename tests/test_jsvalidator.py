from django.core.exceptions import ValidationError

import pytest

from hope_flex_fields.validators import JsValidator


def test_jsvalidator():
    code = "result=value*2"
    v = JsValidator(code)
    assert v(22)


def test_jsvalidator_fail():
    code = "result=value==2"
    v = JsValidator(code)
    with pytest.raises(ValidationError) as e:
        v(22)
    assert e.value.messages == ["Please insert a valid value"]


def test_jsvalidator_return_dict():
    code = 'result={"value": "error"}'
    v = JsValidator(code)
    with pytest.raises(ValidationError) as e:
        v(22)
    assert e.value.message_dict == {"value": ["error"]}


def test_jsvalidator_return_tuple():
    code = 'result=["1","2","3"]'
    v = JsValidator(code)
    with pytest.raises(ValidationError) as e:
        v(22)
    assert e.value.messages == ["1", "2", "3"]


def test_jsvalidator_fail_custom_message():
    code = """
if (value <2){
    result = "Provided number must be less than or equal to 2!";
}else if (value > 5){
    result = "Provided number must be greater than or equal to 5!";
}
"""
    v = JsValidator(code)
    with pytest.raises(ValidationError) as e:
        v(22)
    assert e.value.messages == ["Provided number must be greater than or equal to 5!"]


def test_jsvalidator_return_error():
    code = "result={}"
    v = JsValidator(code)
    with pytest.raises(ValidationError) as e:
        v(22)
    assert e.value.message_dict == {}
