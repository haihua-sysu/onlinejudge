#include <sys/stat.h>
#include <unistd.h>
#include <stdlib.h>
#include <signal.h>
#include <syslog.h>
#include <fcntl.h>
#include <sys/resource.h>
#include <mysql/mysql.h>
#include <sys/wait.h>
#include <stdio.h>
#include <json/json.h>

#include "judge.h"

#include <map>
#include <fstream>
#include <algorithm>
using namespace std;

#define foreach(it, s) for (__typeof(s.begin()) it = s.begin(); it != s.end(); ++it)

const int BufferSize = 4096;
const int MAXRUNNING = 4;

int max_running, running;

char query[BufferSize], RunPath[BufferSize], testdata_dir[BufferSize], cmd[BufferSize];
map<string, string> OJ_conf;
MYSQL *db;

void error_quit(const char *error_msg){
    syslog(LOG_INFO, error_msg);
    exit(1);
}

void finish_with_error(MYSQL *db){
    syslog(LOG_INFO, mysql_error(db));
    mysql_close(db);
}

void daemonize(){
    int fd0, fd1, fd2;
    pid_t pid;

    struct rlimit rl;
    struct sigaction sa;

    if (getrlimit(RLIMIT_NOFILE, &rl) < 0){
        error_quit("can't get file limit");
    }

    printf("parent:%d\n", getpid());
    umask(0);
    if ((pid = fork()) < 0){
        error_quit("fork error");
    } else if (pid){
        printf("son: %d\n", pid);
        exit(0);
    }
    setsid();

    if (chdir("/") < 0){
        error_quit("can't change directory to /");
    }

    //if (rl.rlim_max == RLIM_INFINITY) rl.rlim_max = 1024;
    //for (int i = 0; i < rl.rlim_max; i++) close(i);

    //fd0 = open("/dev/null", O_RDWR);
    //fd1 = dup(0);
    //fd2 = dup(0);

    openlog("judged", LOG_PID, LOG_USER);
}

int split(const string &str, const string &fs, string &key, string &val){
    int pos = str.find(fs);
    if (pos == -1) return -1;
    key = str.substr(0, pos);
    val = str.substr(pos + 1);
    return 0;
}

void read_OJconf(){
    ifstream in("/etc/judged.conf");
    string str, key, val;
    while (getline(in, str)){
        if (split(str, "=", key, val) == -1) continue;
        OJ_conf[key] = val;
    }
    in.close();
    //foreach(it, OJ_conf) printf("%s %s\n", it->first.c_str(), it->second.c_str());
}

int connect_mysql(const string &user, const string &password, const string &db_name){
    db = mysql_init(NULL);
    if (db == NULL){
        finish_with_error(db);
        return -1;
    }

    if (mysql_real_connect(db, OJ_conf["OJ_DB_HOST"].c_str(), user.c_str(), password.c_str(), db_name.c_str(), 0, NULL, 0) == NULL){
        printf("%s\n", mysql_error(db));
        finish_with_error(db);
        return -1;
    }

    syslog(LOG_INFO, "connect mysql success");
    return 0;
}

void sigchld_handler(int signo){
    if (signo == SIGCHLD){
        while (waitpid(-1, NULL, WNOHANG) > 0) running--;
    }
}

void bind_signal(){
    signal(SIGCHLD, sigchld_handler);
}

void init(){
    daemonize();
    read_OJconf();
    if (connect_mysql(OJ_conf["OJ_DB_USER"], OJ_conf["OJ_DB_PASSWORD"], OJ_conf["OJ_DB_NAME"]) == -1){
        error_quit("connected mysql failed!");
    }

    if (OJ_conf.count("OJ_MAX_RUNNING")){
        max_running = atoi(OJ_conf["OJ_MAX_RUNNING"].c_str());
    }
    if (max_running < 0) max_running = 1;
    if (max_running > MAXRUNNING) max_running = MAXRUNNING;

    bind_signal();
}

bool have_judge(){
    sprintf(query, "SELECT sid,pid_id FROM submission_submission WHERE status=%d;", PENDING);

    if (mysql_query(db, query)){
        printf("%s\n", mysql_error(db));
        //syslog(LOG_INFO, mysql_error(db));
        exit(0);
    }

    MYSQL_RES *result = mysql_store_result(db);
    int num_rows = mysql_num_rows(result);
    if (!num_rows){
        mysql_free_result(result);
        return false;
    }

    if (running < max_running){
        MYSQL_ROW row = mysql_fetch_row(result);
        int sid = atoi(row[0]), problem_id = atoi(row[1]);
        mysql_free_result(result);

        sprintf(query, "UPDATE submission_submission SET status=%d, judge_result=%s WHERE sid=%d", JUDGING, "'Judging'", sid);
        if (mysql_query(db, query)){
            printf("%s\n", mysql_error(db));
            return false;
        }

        pid_t pid;
        if ((pid = fork()) < 0){
            sprintf(query, "UPDATE submission_submission SET status=%d, judge_result=%s WHERE sid=%d", PENDING, "'Pending'", sid);
            mysql_query(db, query);
            puts("From judged: fork error");
            return false;
        }

        ++running;
        if (pid == 0){
            //generate run_dir with rand int
            sprintf(RunPath, "/tmp/oj/%d", sid);

            //create run_dir
            sprintf(cmd, "mkdir -p %s", RunPath);
            system(cmd);

            //copy testdata to run_dir
            sprintf(testdata_dir, "%s/%d", OJ_conf["OJ_TESTDATA_DIR"].data(), problem_id);
            sprintf(cmd, "cp -f %s/*.in %s/*.out %s", testdata_dir, testdata_dir, RunPath);
            system(cmd);

            //copy judge program to run_dir
            sprintf(cmd, "cp -f /usr/bin/judge_core %s", RunPath);
            system(cmd);

#ifdef DEBUG
            printf("From judged: %s : %d\n", RunPath, sid);
#endif
            //run judge
            sprintf(cmd, "%s/judge_core %s %d", RunPath, RunPath, sid);
            system(cmd);

            //delete run_dir
            sprintf(cmd, "rm -R -f %s", RunPath);
#ifdef DEBUG
            printf("From judged: %s\n", cmd);
#endif
            system(cmd);

            exit(0);
        }
    } else{
        mysql_free_result(result);
        return false;
    }

    return true;
}

void judged(){
    running = 0;
    while (true){
        if (!have_judge()) sleep(1);
    }
}

int main(){
    init();
    judged();
    return 0;
}
