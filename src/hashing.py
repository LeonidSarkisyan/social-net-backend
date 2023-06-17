from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hash:
    @staticmethod
    def bcrypt(password: str):
        return pwd_context.hash(password)

    @staticmethod
    def verify(hashed_password, simple_password):
        return pwd_context.verify(simple_password, hashed_password)
