import importlib.util
import sys


def is_foundry_local_sdk_installed() -> bool:
    return importlib.util.find_spec("foundry_local_sdk") is not None


def main():
    if is_foundry_local_sdk_installed():
        print("foundry-local-sdk kurulu.")
    else:
        print("foundry-local-sdk kurulu değil.")
        print("Kurmak için şu komutu çalıştırın:")
        print("    pip install foundry-local-sdk")
        sys.exit(1)


if __name__ == "__main__":
    main()
