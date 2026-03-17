import pytest
from your_module import (
    validate_input_text,
    deduplicate_preserving_order,
    extract_keywords_spacy,
)

# ---------------------------------------------------------------------------
# validate_input_text
# ---------------------------------------------------------------------------


class TestValidateInputText:

    def test_empty_string_returns_empty_list(self):
        assert validate_input_text("") == []

    def test_valid_string_returns_none(self):
        assert validate_input_text("some text") is None

    def test_none_raises_type_error(self):
        with pytest.raises(TypeError, match="got NoneType instead"):
            validate_input_text(None)

    def test_integer_raises_type_error(self):
        with pytest.raises(TypeError, match="got int instead"):
            validate_input_text(123)


# ---------------------------------------------------------------------------
# deduplicate_preserving_order
# ---------------------------------------------------------------------------

class TestDeduplicatePreservingOrder:

    def test_removes_duplicates_and_preserves_order(self):
        assert deduplicate_preserving_order(["paris", "scandal", "paris"]) == [
            "paris", "scandal"]

    def test_empty_list_returns_empty_list(self):
        assert deduplicate_preserving_order([]) == []
