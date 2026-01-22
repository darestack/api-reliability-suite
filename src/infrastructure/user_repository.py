from typing import Optional


class UserRepository:
    def __init__(self):
        # Simulated database
        self._db = {
            "demo": "$2b$12$0CcPZHJWc4votGYMFQJXSuEsdUZR4BFXsy83HMLGwVVtMVnvVjnwu"  # password: secret123
        }

    def get_user_hash(self, username: str) -> Optional[str]:
        """
        Retrieves the hashed password for a user.
        In a real app, this would query Postgres.
        """
        return self._db.get(username)


# Singleton instance
user_repository = UserRepository()
