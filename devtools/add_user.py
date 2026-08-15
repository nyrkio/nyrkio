import argparse
import sys
from passlib.context import CryptContext
from pymongo import MongoClient

# Configure Bcrypt password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def main():
    parser = argparse.ArgumentParser(description="Add a new user to MongoDB.")
    parser.add_argument(
        "--email", required=True, help="User email address"
    )
    parser.add_argument(
        "--password", required=True, help="User password"
    )
    parser.add_argument(
        "--mongo-uri",
        default="mongodb://localhost:27017/",
        help="MongoDB connection URI (default: mongodb://localhost:27017/)",
    )
    parser.add_argument(
        "--superuser", action="store_true", help="Set user as superuser"
    )

    args = parser.parse_args()

    # Connect to MongoDB
    client = MongoClient(args.mongo_uri)
    db = client["nyrkiodb"]
    user_collection = db["User"]

    # Check if user already exists
    if user_collection.find_one({"email": args.email}):
        print(f"Error: User with email '{args.email}' already exists.")
        sys.exit(1)

    # Hash the password using Bcrypt
    hashed_password = pwd_context.hash(args.password)

    # Prepare user document matching your schema
    new_user = {
        "email": args.email,
        "hashed_password": hashed_password,
        "is_active": True,
        "is_superuser": args.superuser,
        "is_verified": False,
        "oauth_accounts": [],
    }

    # Insert document
    result = user_collection.insert_one(new_user)
    print(f"User successfully created with _id: {result.inserted_id}")


if __name__ == "__main__":
    main()
