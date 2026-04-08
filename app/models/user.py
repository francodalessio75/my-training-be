from beanie import Document


class User(Document):
    email: str
    display_name: str
    description: str | None = None
    password_hash: str

    class Settings:
        name = "users"
