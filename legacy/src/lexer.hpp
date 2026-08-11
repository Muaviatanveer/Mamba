#pragma once

#include <string>
#include <vector>

enum class TokenType {
  LET,
  FN,
  RETURN,
  IF,
  ELSE,
  WHILE,
  PRINT,
  IDENTIFIER,
  NUMBER,
  STRING,
  ASSIGN,   // =
  PLUS,     // +
  MINUS,    // -
  STAR,     // *
  SLASH,    // /
  GT,       // >
  LT,       // <
  EQ,       // ==
  NE,       // !=
  LPAREN,   // (
  RPAREN,   // )
  LBRACE,   // {
  RBRACE,   // }
  LBRACKET, // [
  RBRACKET, // ]
  COMMA,    // ,
  END_OF_FILE,
  UNKNOWN
};

struct Token {
  TokenType type;
  std::string lexeme;
  int line;
};

class Lexer {
private:
  std::string source;
  size_t start = 0;
  size_t current = 0;
  int line = 1;

  bool isAtEnd() { return current >= source.length(); }

  char advance() { return source[current++]; }

  char peek() {
    if (isAtEnd())
      return '\0';
    return source[current];
  }

  void addToken(TokenType type, std::vector<Token> &tokens) {
    std::string text = source.substr(start, current - start);
    tokens.push_back({type, text, line});
  }

public:
  Lexer(const std::string &src) : source(src) {}

  std::vector<Token> scanTokens() {
    std::vector<Token> tokens;
    while (!isAtEnd()) {
      start = current;
      char c = advance();
      switch (c) {
      case ' ':
      case '\r':
      case '\t':
        break;
      case '\n':
        line++;
        break;
      case '(':
        addToken(TokenType::LPAREN, tokens);
        break;
      case ')':
        addToken(TokenType::RPAREN, tokens);
        break;
      case '{':
        addToken(TokenType::LBRACE, tokens);
        break;
      case '}':
        addToken(TokenType::RBRACE, tokens);
        break;
      case '[':
        addToken(TokenType::LBRACKET, tokens);
        break;
      case ']':
        addToken(TokenType::RBRACKET, tokens);
        break;
      case ',':
        addToken(TokenType::COMMA, tokens);
        break;
      case '+':
        addToken(TokenType::PLUS, tokens);
        break;
      case '-':
        addToken(TokenType::MINUS, tokens);
        break;
      case '*':
        addToken(TokenType::STAR, tokens);
        break;
      case '/':
        addToken(TokenType::SLASH, tokens);
        break;
      case '>':
        addToken(TokenType::GT, tokens);
        break;
      case '<':
        addToken(TokenType::LT, tokens);
        break;
      case '=':
        if (peek() == '=') {
          advance();
          addToken(TokenType::EQ, tokens);
        } else {
          addToken(TokenType::ASSIGN, tokens);
        }
        break;
      case '!':
        if (peek() == '=') {
          advance();
          addToken(TokenType::NE, tokens);
        } else {
          addToken(TokenType::UNKNOWN, tokens);
        }
        break;
      case '"': {
        while (peek() != '"' && !isAtEnd()) {
          if (peek() == '\n')
            line++;
          advance();
        }
        if (!isAtEnd())
          advance(); // closing "
        addToken(TokenType::STRING, tokens);
        break;
      }
      default:
        if (isdigit(c)) {
          while (isdigit(peek()))
            advance();
          addToken(TokenType::NUMBER, tokens);
        } else if (isalpha(c) || c == '_') {
          while (isalnum(peek()) || peek() == '_')
            advance();
          std::string text = source.substr(start, current - start);
          if (text == "let")
            addToken(TokenType::LET, tokens);
          else if (text == "fn")
            addToken(TokenType::FN, tokens);
          else if (text == "return")
            addToken(TokenType::RETURN, tokens);
          else if (text == "if")
            addToken(TokenType::IF, tokens);
          else if (text == "else")
            addToken(TokenType::ELSE, tokens);
          else if (text == "while")
            addToken(TokenType::WHILE, tokens);
          else if (text == "print")
            addToken(TokenType::PRINT, tokens);
          else
            addToken(TokenType::IDENTIFIER, tokens);
        } else {
          addToken(TokenType::UNKNOWN, tokens);
        }
        break;
      }
    }
    tokens.push_back({TokenType::END_OF_FILE, "EOF", line});
    return tokens;
  }
};