from app.core.errors import RuneError


def test_rune_error_behaves_like_a_normal_python_exception() -> None:
    error = RuneError(code="example", message="Readable message")

    error.__traceback__ = None

    assert str(error) == "Readable message"
