#include <iostream>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>

using namespace std;

int main(int argc, char *argv[]) {
    if (argc != 5) {
        cout << "Usage: ./primexarmy <IP> <PORT> <TIME> <METHOD>" << endl;
        return 1;
    }

    char *ip = argv[1];
    int port = stoi(argv[2]);
    int duration = stoi(argv[3]);
    char *method = argv[4];

    cout << "🚀 PRIMEXARMY System Initiated!" << endl;
    cout << "Target: " << ip << ":" << port << " | Method: " << method << endl;

    // Yahan aapka actual attack/test logic aayega
    // For demonstration, ye sirf countdown dikhayega
    sleep(duration);

    cout << "✅ Task Completed." << endl;
    return 0;
}