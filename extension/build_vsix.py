import os
import json
import zipfile

# 1. Locate icon.png in root or extension folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
icon_path = os.path.join(BASE_DIR, "icon.png")

if not os.path.exists(icon_path):
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")

if not os.path.exists(icon_path):
    print("⚠️ Error: 'icon.png' not found! Please place your new image as 'icon.png' in your Mamba root folder.")
    exit(1)

with open(icon_path, "rb") as f:
    icon_bytes = f.read()

# 2. Package Metadata
package_json = {
  "name": "mamba-lang",
  "displayName": "Mamba Programming Language",
  "description": "Official Black Mamba Language Support & Syntax Highlighting (.mb)",
  "version": "0.1.0",
  "publisher": "mamba-dev",
  "icon": "icon.png",
  "engines": {
    "vscode": "^1.60.0"
  },
  "categories": [
    "Programming Languages"
  ],
  "contributes": {
    "languages": [
      {
        "id": "mamba",
        "aliases": ["Mamba", "mamba"],
        "extensions": [".mb", ".mamba"],
        "configuration": "./language-configuration.json",
        "icon": {
          "light": "./icon.png",
          "dark": "./icon.png"
        }
      }
    ],
    "grammars": [
      {
        "language": "mamba",
        "scopeName": "source.mamba",
        "path": "./syntaxes/mamba.tmLanguage.json"
      }
    ]
  }
}

lang_conf = {
  "comments": {"lineComment": "#"},
  "brackets": [["{", "}"], ["[", "]"], ["(", ")"]],
  "autoClosingPairs": [
    {"open": "{", "close": "}"},
    {"open": "[", "close": "]"},
    {"open": "(", "close": ")"},
    {"open": "\"", "close": "\"", "notIn": ["string"]}
  ]
}

tm_grammar = {
  "$schema": "https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json",
  "name": "Mamba",
  "scopeName": "source.mamba",
  "patterns": [
    {"include": "#keywords"},
    {"include": "#strings"},
    {"include": "#comments"},
    {"include": "#numbers"},
    {"include": "#functions"}
  ],
  "repository": {
    "keywords": {
      "patterns": [
        {"name": "keyword.control.mamba", "match": "\\b(if|else|while|return|route|import)\\b"},
        {"name": "keyword.other.mamba", "match": "\\b(let|fn)\\b"},
        {"name": "support.function.mamba", "match": "\\b(print|len|input|str|int)\\b"}
      ]
    },
    "functions": {
      "patterns": [
        {"name": "entity.name.function.mamba", "match": "\\b([a-zA-Z_][a-zA-Z0-9_]*)(?=\\()"}
      ]
    },
    "strings": {
      "name": "string.quoted.double.mamba",
      "begin": "\"",
      "end": "\"",
      "patterns": [{"name": "constant.character.escape.mamba", "match": "\\\\."}]
    },
    "comments": {
      "patterns": [{"name": "comment.line.number-sign.mamba", "match": "#.*$"}]
    },
    "numbers": {
      "patterns": [{"name": "constant.numeric.mamba", "match": "\\b[0-9]+(\\.[0-9]+)?\\b"}]
    }
  }
}

vsix_manifest = """<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011">
  <Metadata>
    <Identity Id="mamba-lang" Version="0.1.0" Publisher="mamba-dev" Language="en-US" />
    <DisplayName>Mamba Programming Language</DisplayName>
    <Description>Official Black Mamba Language Support</Description>
    <Categories>Programming Languages</Categories>
    <Icon>extension/icon.png</Icon>
  </Metadata>
  <Installation>
    <InstallationTarget Id="Microsoft.VisualStudio.Code" />
  </Installation>
  <Dependencies />
  <Assets>
    <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true" />
    <Asset Type="Microsoft.VisualStudio.Services.Icons.Default" Path="extension/icon.png" Addressable="true" />
  </Assets>
</PackageManifest>
"""

content_types = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension=".json" ContentType="application/json" />
  <Default Extension=".vsixmanifest" ContentType="text/xml" />
  <Default Extension=".md" ContentType="text/markdown" />
  <Default Extension=".png" ContentType="image/png" />
</Types>
"""

# 3. Build .vsix Package inside extension/ directory
vsix_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mamba-0.1.0.vsix")

with zipfile.ZipFile(vsix_filename, 'w', zipfile.ZIP_DEFLATED) as vsix:
    vsix.writestr("[Content_Types].xml", content_types)
    vsix.writestr("extension.vsixmanifest", vsix_manifest)
    vsix.writestr("extension/package.json", json.dumps(package_json, indent=2))
    vsix.writestr("extension/language-configuration.json", json.dumps(lang_conf, indent=2))
    vsix.writestr("extension/syntaxes/mamba.tmLanguage.json", json.dumps(tm_grammar, indent=2))
    vsix.writestr("extension/icon.png", icon_bytes)
    vsix.writestr("extension/README.md", "# Mamba Language\nOfficial Black Mamba language extension for `.mb` files.")

print(f"🔥 Success! Rebuilt extension package with your new icon: '{vsix_filename}'")