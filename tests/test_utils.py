from unittest.mock import MagicMock, patch

from src.utils.common_utils import generate_credential_id
from src.utils.db_utils import (
    get_certificate_by_credential,
    get_signatures_by_ids,
    seed_certificates,
    seed_signatures,
)


def test_generate_credential_id():
    cred_id = generate_credential_id()
    assert isinstance(cred_id, str)
    assert len(cred_id) > 0
    assert cred_id[0].islower()  

@patch("utils.db_utils.db")
def test_get_certificate_by_credential(mock_db):
    fake_cert = {"credentialId": "abc123", "_id": 123}
    mock_collection = MagicMock()
    mock_collection.find_one.return_value = fake_cert
    mock_db.__getitem__.return_value = mock_collection

    result = get_certificate_by_credential("abc123")
    assert result["_id"] == "123"
    assert result["credentialId"] == "abc123"

@patch("utils.db_utils.db")
def test_get_signatures_by_ids(mock_db, caplog):
    fake_signatures = [
        {"id": "sig1", "_id": 1},
        {"id": "sig2", "_id": 2},
    ]
    mock_collection = MagicMock()
    mock_collection.find.return_value = fake_signatures
    mock_db.__getitem__.return_value = mock_collection

    caplog.set_level("INFO")
    result = get_signatures_by_ids(["sig1", "sig2", "sig3"])
    assert len(result) == 2
    assert "_id" in result[0]
    assert "Signatures not found" in caplog.text

@patch("utils.db_utils.db")
def test_seed_signatures(mock_db):
    mock_collection = MagicMock()
    mock_collection.count_documents.return_value = 0
    mock_db.__getitem__.return_value = mock_collection

    seed_signatures()
    mock_collection.insert_many.assert_called()

@patch("utils.db_utils.db")
def test_seed_certificates(mock_db):
    mock_collection = MagicMock()
    mock_collection.count_documents.return_value = 0
    mock_db.__getitem__.return_value = mock_collection

    seed_certificates()
    mock_collection.insert_one.assert_called()

