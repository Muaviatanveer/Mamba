---
layout: home

hero:
  name: "Mamba"
  text: "The Mamba Programming Language"
  tagline: "Simple syntax. Native performance. Multiple targets."
  image:
    src: https://raw.githubusercontent.com/Muaviatanveer/Mamba/main/icons/black_mamba.png
    alt: Mamba Logo
  actions:
    - theme: brand
      text: Get Started
      link: /getting-started
    - theme: alt
      text: View on GitHub
      link: https://github.com/Muaviatanveer/Mamba

features:
  - title: Python-like Readability
    details: Clean braces {}, explicit let / fn keywords, zero indentation bugs.
  - title: Native Performance
    details: Compiles to a standalone C++ binary (optimized with -O3) featuring a zero-dependency POSIX socket HTTP server.
  - title: Multi-Target Compiler
    details: Transpile to Native C++20 or PHP web scripts. Write once, run everywhere.
  - title: Built-in Web Primitives
    details: Web endpoints are first-class keywords. Build APIs without importing massive web frameworks.
  - title: Built-in Database
    details: Natively embeds SQLite with prepared statement parameter binding to prevent SQL injection.
  - title: Mamba Cloud PaaS
    details: Includes its own mini deployment engine. Deploy directly from git with zero configuration.
---
