import os
import json
import shutil

# 1. Define Paths for BOTH VS Code and Cursor IDE
home = os.path.expanduser("~")
ide_paths = [
    os.path.join(home, ".vscode", "extensions", "mamba-lang"),
    os.path.join(home, ".cursor", "extensions", "mamba-lang") # ADDED CURSOR SUPPORT!
]

# 2. Extension Data
pkg = {
  "name": "mamba-lang",
  "displayName": "Mamba",
  "version": "0.1.0",
  "publisher": "mamba-creator", 
  "engines": {"vscode": "^1.60.0"},
  "contributes": {
    "languages": [{
        "id": "mamba", 
        "aliases": ["Mamba", "mamba"],
        "extensions": [".mb"], 
        "configuration": "./lang-conf.json"
    }],
    "grammars": [{
        "language": "mamba", 
        "scopeName": "source.mamba", 
        "path": "./syntaxes/mamba.tmLanguage.json"
    }]
  }
}

conf = {
  "comments": {"lineComment": "#"},
  "autoClosingPairs": [
    { "open": "{", "close": "}" },
    { "open": "[", "close": "]" },
    { "open": "(", "close": ")" },
    { "open": "\"", "close": "\"", "notIn": ["string"] }
  ]
}

tm = {
  "$schema": "https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json",
  "name": "Mamba",
  "scopeName": "source.mamba",
  "patterns": [
    { "name": "keyword.control.mamba", "match": "\\b(if|else|while|return|route|import)\\b" },
    { "name": "keyword.other.mamba", "match": "\\b(let|fn)\\b" },
    { "name": "support.function.mamba", "match": "\\b(print|len|input|str|int)\\b" },
    { "name": "entity.name.function.mamba", "match": "\\b([a-zA-Z_][a-zA-Z0-9_]*)(?=\\()" },
    { "name": "string.quoted.double.mamba", "begin": "\"", "end": "\"", "patterns": [{"name": "constant.character.escape.mamba", "match": "\\\\."}] },
    { "name": "comment.line.number-sign.mamba", "match": "#.*$" },
    { "name": "constant.numeric.mamba", "match": "\\b[0-9]+(\\.[0-9]+)?\\b" }
  ]
}

# 3. Install to all IDEs
for ext_path in ide_paths:
    syntaxes_path = os.path.join(ext_path, "syntaxes")
    
    if os.path.exists(ext_path):
        shutil.rmtree(ext_path)
        
    os.makedirs(syntaxes_path, exist_ok=True)
    
    with open(os.path.join(ext_path, "package.json"), "w") as f: 
        json.dump(pkg, f, indent=2)
    with open(os.path.join(ext_path, "lang-conf.json"), "w") as f: 
        json.dump(conf, f, indent=2)
    with open(os.path.join(syntaxes_path, "mamba.tmLanguage.json"), "w") as f: 
        json.dump(tm, f, indent=2)

print("✅ Mamba Extension installed successfully for BOTH Cursor & VS Code!")