from revvision.detection import detect_file_type


def test_detect_qcp_by_content():
    match = detect_file_type("calc.js", "function onCalculate(){ return []; } SBQQ")
    assert match.type_key == "qcp"


def test_detect_apex_class_by_extension():
    match = detect_file_type("MyClass.cls", "public class MyClass {}")
    assert match.type_key == "apex_class"
