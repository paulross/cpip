import pytest

from cpip.core import Platform


def test_platform_config():
    platform = Platform.PlatformConfig()
    assert platform is not None

