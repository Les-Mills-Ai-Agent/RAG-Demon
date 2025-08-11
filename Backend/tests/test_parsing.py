import json
import yaml
from src.ragdemon.parsing import parse_file
import pytest

# test that all supported file types are being parsed correctly
def test_parse_json(tmp_path):
    path = tmp_path / "testdata.json"
    path.write_text(json.dumps({"test" : "data"}))
    result = parse_file(str(path))
    assert result == {"test" : "data"}

def test_parse_yaml(tmp_path):
    path = tmp_path / "testdata.yaml"
    path.write_text(yaml.safe_dump({"test" : "data"}))
    result = parse_file(str(path))
    assert result == {"test" : "data"}

def test_parse_markdown(tmp_path):
    path = tmp_path / "testdata.md"
    path.write_text("# test data")
    result = parse_file(str(path))
    assert result == {"content": "# test data"}

def test_parse_html(tmp_path):
    path = tmp_path / "testdata.html"
    path.write_text("<html><body><h1>test data</h1></body</html>")
    result = parse_file(str(path))
    assert "test data" in result["content"]

# test that unsupported file types raises error
def test_unsupported_file_type(tmp_path):
    path = tmp_path / "file.txt"
    with pytest.raises(ValueError):
        parse_file(str(path))

