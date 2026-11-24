import os

if __name__ == "__main__":
    print(os.getenv("ENV_TEST", "ENV_TEST is missing"))