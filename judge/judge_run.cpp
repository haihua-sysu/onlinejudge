#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/resource.h>
#include <string>

using std::string;

/*
 * argv[1] -> filename
 * argv[2] -> inputfile
 * argv[3] -> outputfile
 * argv[4] -> time_limit
 * argv[5] -> memory_limit
 */

#define DEBUG

int main(int argc, char *argv[]){
    if (argc != 6){
        puts("Usage: ./judge_run filename inputfile outputfile time_limit memory_limit");
        return 1;
    }
#ifdef DEBUG
    for (int i = 0; i < argc; i++) printf("%s\n", argv[i]);
#endif
    string filename(argv[1]),inputfile(argv[2]),outputfile(argv[3]);
    int time_limit = atoi(argv[4]);
    int memory_limit = atoi(argv[5]);

    /* redirect stdin, stdout, stderr */
    int fd_input = open(inputfile.c_str(), O_RDONLY);
    int fd_output = open(outputfile.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0666);
    int fd_error = open("/dev/null",O_WRONLY);
    dup2(fd_input, STDIN_FILENO);
    dup2(fd_output, STDOUT_FILENO);
    dup2(fd_error, STDERR_FILENO);

    struct rlimit limit;
    getrlimit(RLIMIT_CPU, &limit);
    limit.rlim_cur = (time_limit - 1) / 1000 + 2;
    limit.rlim_max = limit.rlim_cur + 2;
    setrlimit(RLIMIT_CPU, &limit);

    execl(filename.c_str(),filename.c_str(),NULL);
    return 0;
}
