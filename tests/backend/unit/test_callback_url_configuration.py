"""Unit tests for SignalHireClient callback URL resolution logic."""

import os

import pytest

from src.services.signalhire_client import SignalHireClient, DEFAULT_CALLBACK_URL


@pytest.fixture(autouse=True)
def reset_callback_env(monkeypatch):
    """Ensure callback-related env vars are cleared before each test."""
    monkeypatch.delenv("SIGNALHIRE_CALLBACK_URL", raising=False)
    monkeypatch.delenv("PUBLIC_CALLBACK_URL", raising=False)
    monkeypatch.delenv("SIGNALHIRE_DEFAULT_CALLBACK_URL", raising=False)
    yield


def test_client_uses_explicit_callback_override():
    client = SignalHireClient(callback_url="https://example.com/callback")
    assert client.callback_url == "https://example.com/callback"


def test_client_reads_signalhire_callback_url_env(monkeypatch):
    monkeypatch.setenv("SIGNALHIRE_CALLBACK_URL", "https://env.example.com/callback")
    client = SignalHireClient()
    assert client.callback_url == "https://env.example.com/callback"


def test_client_reads_public_callback_url_fallback(monkeypatch):
    monkeypatch.setenv("PUBLIC_CALLBACK_URL", "https://public.example.com/callback")
    client = SignalHireClient()
    assert client.callback_url == "https://public.example.com/callback"


def test_client_defaults_to_constant_when_no_env_present():
    client = SignalHireClient()
    assert client.callback_url == DEFAULT_CALLBACK_URL


def test_default_callback_can_be_overridden_via_env(monkeypatch):
    monkeypatch.setenv("SIGNALHIRE_DEFAULT_CALLBACK_URL", "https://override.example.com/callback")
    client = SignalHireClient()
    assert client.callback_url == "https://override.example.com/callback"
