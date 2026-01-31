"""Tests for aegis main module."""
import pytest
from aegis.main import main


def test_main(capsys):
    """Test main function output."""
    main()
    captured = capsys.readouterr()
    assert "Hello from aegis!" in captured.out
