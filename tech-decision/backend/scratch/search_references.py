import os

def search_files(directory, query):
    matches = []
    for root, dirs, files in os.walk(directory):
        # Skip virtual environment
        if ".venv" in root or "__pycache__" in root or ".git" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        for i, line in enumerate(f, 1):
                            if query.lower() in line.lower():
                                matches.append((path, i, line.strip()))
                except Exception:
                    pass
    return matches

def main():
    print("Searching for PriceListing...")
    for path, line_no, content in search_files(".", "PriceListing"):
        print(f"{path}:{line_no}: {content}")
        
    print("\nSearching for price_listings...")
    for path, line_no, content in search_files(".", "price_listings"):
        print(f"{path}:{line_no}: {content}")

if __name__ == "__main__":
    main()
