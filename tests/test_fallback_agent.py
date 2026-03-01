#!/usr/bin/env python3
"""Unit tests for the fallback_agent module"""

import sys
import os
import pytest
from botocore.exceptions import ClientError
from unittest.mock import patch

# make sure src package is on path like other tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def make_client_error(code, message):
    return ClientError(
        {
            'Error': {
                'Code': code,
                'Message': message
            }
        },
        operation_name='Converse'
    )


class DummyClient:
    def __init__(self, exc=None):
        self.exc = exc
        self.last_kwargs = None

    def converse(self, *args, **kwargs):
        self.last_kwargs = kwargs
        if self.exc:
            raise self.exc
        return {
            'output': {
                'message': {
                    'content': [{'text': 'dummy response'}]
                }
            }
        }


@patch('agents.fallback_agent.boto3.client')
def test_with_inference_profile(mock_client, monkeypatch):
    """When an inference profile is set, it should be passed to converse."""
    from src.agents.fallback_agent import fallback_agent

    # override env
    monkeypatch.setenv('BEDROCK_INFERENCE_PROFILE', 'arn:aws:profile:123')
    client = DummyClient()
    mock_client.return_value = client
    resp = fallback_agent("hi")
    assert resp == 'dummy response'
    assert client.last_kwargs is not None
    assert 'inferenceProfileArn' in client.last_kwargs
    assert client.last_kwargs['inferenceProfileArn'] == 'arn:aws:profile:123'


@patch('agents.fallback_agent.boto3.client')
def test_fallback_success(mock_client):
    from src.agents.fallback_agent import fallback_agent

    client = DummyClient()
    mock_client.return_value = client
    resp = fallback_agent("hello world")
    assert resp == 'dummy response'
    # should have sent a modelId key since no profile was defined
    assert 'modelId' in client.last_kwargs


@patch('agents.fallback_agent.boto3.client')
def test_fallback_operation_not_allowed(mock_client):
    from src.agents.fallback_agent import fallback_agent

    err = make_client_error('ValidationException', 'Operation not allowed')
    mock_client.return_value = DummyClient(exc=err)

    with pytest.raises(RuntimeError) as excinfo:
        fallback_agent("test")
    # error hint should mention permission or operation not allowed
    errstr = str(excinfo.value)
    assert 'permission' in errstr or 'Operation not allowed' in errstr


@patch('agents.fallback_agent.boto3.client')
def test_fallback_other_error(mock_client):
    from src.agents.fallback_agent import fallback_agent

    err = make_client_error('SomeOtherError', 'Something went wrong')
    mock_client.return_value = DummyClient(exc=err)

    with pytest.raises(ClientError):
        fallback_agent("test")
