from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Password hashing
ph = PasswordHasher()


def hash_password(password: str) -> str:
    """
        Hash a password
        Args:
            password: The plain form of password needed to be hashed
        Returns:
            The hashed password    
    """
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
        Verify a password against its hash
        Args:
            plain_password: The plain form of password to verify
            hashed_password: The hashed password to compare against
        Returns:
            True if the password is correct
            False otherwise
    """
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False
