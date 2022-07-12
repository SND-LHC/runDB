"""This module tests the factory."""
import pytest

from factory import APIFactory
from databases.mongodb.mongodbadapter import MongoToCDBAPIAdapter


@pytest.fixture
def supply_dbAPI():
    """Create an instance of the CDB API.

    This can be used by other functions.
    """
    factory = APIFactory()
    db_api = factory.construct_DB_API()
    return db_api


@pytest.mark.smoke_test
def test_create_mongo_api():
    """Check whether the factory can create an instance of the API for MongoDB."""
    factory = APIFactory()
    db_api = factory.construct_DB_API()
    assert isinstance(db_api, MongoToCDBAPIAdapter)


@pytest.mark.smoke_test
def test_create_unknown_api():
    """Check whether the factory can raise a proper exception if an unsupported database type is specified in the configuration file."""
    factory = APIFactory()

    with pytest.raises(NotImplementedError):
        assert factory.construct_DB_API("tests/test_config.yml")
