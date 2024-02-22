#include <stdio.h>
#include <stdlib.h>
#include <algorithm.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>

#define N 5  // Number of philosophers

// index of left and right chopstick
#define LEFT (i + N - 1) % N
#define RIGHT (i + 1) % N

// Semaphores
// array of semaphores for each chopstick
sem_t chopstick[N];

// mutex semaphore for critical section
// we need to use mutex because we are using shared resources and we need to make sure that only one philosopher can pick up the chopstick at a time
sem_t mutex;

// A philosopher thinks for a random amount of time, then gets hungry and tries to pick up the chopsticks. If successful, the philosopher eats for a random amount of time, then puts the chopsticks down and repeats the process.
// The problem is that if all philosophers get hungry at the same time, they will all pick up their left chopstick and then wait forever for their right chopstick, causing a deadlock.
void *philosopher(void *arg) {

    // get the philosopher number
    int i = *((int *)arg);

    // free the memory allocated for arg
    free(arg);


    // only two states allowed for a philosopher
    // 1. thinking
    // 2. eating
    while (1) {
        // Think
        printf("Philosopher %d is thinking\n", i + 1);
        sleep(rand() % 3);

        // Pick up chopsticks
        sem_wait(&mutex);
        printf("Philosopher %d is hungry\n", i + 1);
        sem_post(&mutex);

        // chopstick taken
        printf("Chopstick LEFT at index %d is taken",i+1)
        sem_wait(&chopstick[i]);
        printf("Chopstick RIGHT at index %d is taken",(i+1+1)%N)
        sem_wait(&chopstick[RIGHT]);

        // Eat
        printf("Philosopher %d is eating\n", i + 1);
        sleep(rand() % 3);

        // Put down chopsticks
        sem_post(&chopstick[i]);
        sem_post(&chopstick[RIGHT]);
    }
}

int main() {
    // Initialize semaphores
    sem_init(&mutex, 0, 1);
    for (int i = 0; i < N; i++) {
        sem_init(&chopstick[i], 0, 1);
    }

    // Create philosopher threads
    pthread_t philosophers[N];
    for (int i = 0; i < N; i++) {
        int *arg = malloc(sizeof(*arg));
        *arg = i;
        pthread_create(&philosophers[i], NULL, philosopher, arg);
    }

    // Wait for philosopher threads to finish (which will never happen)
    for (int i = 0; i < N; i++) {
        pthread_join(philosophers[i], NULL);
    }

    // Clean up semaphores
    sem_destroy(&mutex);
    for (int i = 0; i < N; i++) {
        sem_destroy(&chopstick[i]);
    }

    return 0;
}
