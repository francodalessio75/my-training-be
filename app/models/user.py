from beanie import Document


class User(Document):
    email: str
    display_name: str
    description: str | None = None
    hashed_password: str

    class Settings:
        name = "users"
