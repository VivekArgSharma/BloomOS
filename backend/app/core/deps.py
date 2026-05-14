from app.db.mock_store import MockStore


store = MockStore()


def get_store() -> MockStore:
    return store
