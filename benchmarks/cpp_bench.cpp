#include <cstring>
#include <iostream>
#include <netinet/in.h>
#include <string>
#include <sys/socket.h>
#include <unistd.h>

int main() {
  int server_fd = socket(AF_INET, SOCK_STREAM, 0);
  int opt = 1;
  setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

  sockaddr_in address;
  address.sin_family = AF_INET;
  address.sin_addr.s_addr = INADDR_ANY;
  address.sin_port = htons(3002);

  bind(server_fd, (struct sockaddr *)&address, sizeof(address));
  listen(server_fd, 10);

  std::cout << "⚡ Raw C++ Server running on http://localhost:3002"
            << std::endl;

  std::string resp =
      "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: "
      "73\r\n\r\n{\"name\": \"Muavia\", \"project\": \"Mamba\", \"role\": \"AI "
      "Engineer\", \"version\": \"0.1.0\"}";

  while (true) {
    int client_fd = accept(server_fd, NULL, NULL);
    if (client_fd < 0)
      continue;
    char buffer[1024] = {0};
    read(client_fd, buffer, 1024);
    write(client_fd, resp.c_str(), resp.length());
    close(client_fd);
  }
  return 0;
}