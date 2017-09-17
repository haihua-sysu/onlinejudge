#define JUDGING -1
#define PENDING 0
#define AC 1
#define WA 2
#define RTE 3
#define CE 4
#define TLE 5
#define MLE 6
#define UNKNOWNRES 255

#include <string>

const std::string judgeresult[] = {"Pending", "Accepted", "Wrong Answer", "Runtime Error", "Complied Error", "Time Limited Execced", "Memory Limited Execced", "Unknown"};

std::string getResultAsString(int status) {
    if (status == -1) return "Judging";
    return judgeresult[status];
}
