import json
import pytest
from shop.repository import Repository


def test_repository_save_and_load(tmp_path):
    path = tmp_path / "test.json"
    repo = Repository(str(path))
    data = {"hello": "world"}
    repo.save(data)

    loaded = repo.load()
    assert loaded == data


def test_repository_broken_json(tmp_path):
    path = tmp_path / "test.json"
    path.write_text("{ broken json")
    repo = Repository(str(path))
    with pytest.raises(ValueError):
        repo.load()