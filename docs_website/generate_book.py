import os

docs = [
    "getting-started.md",
    "language-basics.md",
    "collections.md",
    "standard-library.md",
    "web-development.md",
    "database.md",
    "tooling.md",
    "architecture.md",
    "mamba-cloud.md",
    "ecosystem.md"
]

with open("mamba_book.md", "w") as out:
    out.write("# The Mamba Programming Language (v0.3.0)\n\n")
    out.write("> Simple syntax. Native performance. Multiple targets.\n\n")
    out.write("---\n\n")
    
    for doc in docs:
        path = os.path.join("docs", doc)
        with open(path, "r") as f:
            out.write(f.read())
            out.write("\n\n---\n\n")
            
print("mamba_book.md created.")
