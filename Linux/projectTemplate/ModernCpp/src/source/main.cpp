#include "example.h"

#include <ctime>
#include <iostream>

//#include <fmt/core.h>

void hello() {
    //fmt::print("Hello from template!\n");
    //time_t now = time(NULL);
    //char* dt = ctime(&now);
    //fmt::print("Time: {}", dt);
    std::cout << "Hello, world!" << std::endl;
    
}

int main() {
    hello();
    return 0;
}
