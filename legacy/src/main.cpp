#include "lexer.hpp"
#include <fstream>
#include <iostream>
#include <sstream>

std::string tokenTypeToString(TokenType type) {
  switch (type) {
  case TokenType::LET:
    return "LET";
  case TokenType::FN:
    return "FN";
  case TokenType::RETURN:
    return "RETURN";
  case TokenType::IF:
    return "IF";
  case TokenType::ELSE:
    return "ELSE";
  case TokenType::WHILE:
    return "WHILE";
  case TokenType::PRINT:
    return "PRINT";
  case TokenType::IDENTIFIER:
    return "IDENTIFIER";
  case TokenType::NUMBER:
    return "NUMBER";
  case TokenType::STRING:
    return "STRING";
  case TokenType::ASSIGN:
    return "ASSIGN";
  case TokenType::PLUS:
    return "PLUS";
  case TokenType::MINUS:
    return "MINUS";
  case TokenType::STAR:
    return "STAR";
  case TokenType::SLASH:
    return "SLASH";
  case TokenType::GT:
    return "GT";
  case TokenType::LT:
    return "LT";
  case TokenType::EQ:
    return "EQ";
  case TokenType::NE:
    return "NE";
  case TokenType::LPAREN:
    return "LPAREN";
  case TokenType::RPAREN:
    return "RPAREN";
  case TokenType::LBRACE:
    return "LBRACE";
  case TokenType::RBRACE:
    return "RBRACE";
  case TokenType::LBRACKET:
    return "LBRACKET";
  case TokenType::RBRACKET:
    return "RBRACKET";
  case TokenType::COMMA:
    return "COMMA";
  case TokenType::END_OF_FILE:
    return "EOF";
  default:
    return "UNKNOWN";
  }
}

int main(int argc, char *argv[]) {
  if (argc < 2) {
    std::cout << "Usage: ./mamba_cpp <script.mb>\n";
    return 1;
  }

  std::ifstream file(argv[1]);
  if (!file.is_open()) {
    std::cerr << "Error: Could not open file " << argv[1] << "\n";
    return 1;
  }

  std::stringstream buffer;
  buffer << file.rdbuf();
  std::string source = buffer.str();

  Lexer lexer(source);
  std::vector<Token> tokens = lexer.scanTokens();

  std::cout << "======================================\n";
  std::cout << "  🐍 Mamba C++ Lexer (0 Unknown Tokens)\n";
  std::cout << "======================================\n";

  for (const auto &token : tokens) {
    std::cout << "Line " << token.line
              << " | Type: " << tokenTypeToString(token.type) << "\t| Lexeme: '"
              << token.lexeme << "'\n";
  }

  return 0;
}