/*
 * 要处理CE的result
 * 处理内存限制
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <sys/times.h>
#include <sys/wait.h>
#include <sys/ptrace.h>
#include <sys/resource.h>
#include <dirent.h>
#include <mysql/mysql.h>

#include "judge.h"
#include "json/json.h"
#include "base64.h"

#include <map>
#include <set>
#include <vector>
#include <fstream>
#include <iostream>
using namespace std;

/* programming language map
 * 1 -> C++
 * 2 -> C
 * 3 -> Java
 * 4 -> Python
 */

#define transfromTime(t) (t.tv_sec*1000 + t.tv_usec/1000)
#define foreach(it, s) for (__typeof(s.begin()) it = s.begin(); it != s.end(); ++it)

const int BufferSize = 4096 * 128;

struct testCase{
    vector<string> inputfile, outputfile;
    string user_outputfile;
    double time_limit;
    int memory_limit, special_judge;

    int size(){
        return inputfile.size();
    }
} testcase;

struct userInfo{
    int user_id, problem_id, language;
    string code;
} userinfo;

struct judgeResult{
    string message;
    int run_time, memory, status;

    judgeResult():message(""), run_time(0), memory(0), status(JUDGING){}
    judgeResult(int run_time, int memory, int status):run_time(run_time), memory(memory), status(status){}

    void update(const judgeResult &rhs){
        run_time = max(run_time, rhs.run_time);
        memory = max(memory, rhs.memory);
        status = max(status, rhs.status);
    }
};

int sid;
MYSQL* db;
char buffer[BufferSize], query[BufferSize], cmd[BufferSize];
map<string, string> OJ_conf;

void finish_judge(const judgeResult &res, const Json::Value &res_detail){
    string result_as_string;
    MYSQL_RES *result;
    MYSQL_ROW row;
    if (res.status == AC){
        int pid, user_id, solved;
        result_as_string = "'Accepted'";

        sprintf(query, "SELECT pid_id, user_id FROM submission_submission WHERE sid=%d;", sid);
        if (mysql_query(db, query)){
#ifdef DEBUG
            printf("%s\n", mysql_error(db));
#endif
        }

        result = mysql_store_result(db);
        row = mysql_fetch_row(result);
        pid = atoi(row[0]), user_id = atoi(row[1]);
        mysql_free_result(result);

        bool has_solved = false;
        sprintf(query, "SELECT sid FROM submission_submission WHERE pid_id=%d and status=1 and user_id=%d;", pid, user_id);
        mysql_query(db, query);
        result = mysql_store_result(db);
        if (mysql_num_rows(result) > 0) {
            has_solved = true;
        }
        mysql_free_result(result);

        if (!has_solved) {
            sprintf(query, "SELECT solved FROM problemset_problem WHERE pid=%d;", pid);
            if (mysql_query(db, query)){
#ifdef DEBUG
                printf("%s\n", mysql_error(db));
#endif
            }
            result = mysql_store_result(db);
            row = mysql_fetch_row(result);
            solved = atoi(row[0]) + 1;
            mysql_free_result(result);
            sprintf(query, "UPDATE problemset_problem SET solved = %d WHERE pid=%d;", solved, pid);
            if (mysql_query(db, query)){
#ifdef DEBUG
                printf("%s\n", mysql_error(db));
#endif
            }

            sprintf(query, "SELECT solved FROM handle_handle WHERE user_id=%d;", user_id);
            if (mysql_query(db, query)){
#ifdef DEBUG
                printf("%s\n", mysql_error(db));
#endif
            }
            result = mysql_store_result(db);
            row = mysql_fetch_row(result);
            solved = atoi(row[0]) + 1;
            mysql_free_result(result);
            sprintf(query, "UPDATE handle_handle SET solved=%d WHERE user_id=%d;", solved, user_id);
            if (mysql_query(db, query)){
#ifdef DEBUG
                printf("%s\n", mysql_error(db));
#endif
            }
        }
    }

    result_as_string = getResultAsString(res.status);
    sprintf(query, "UPDATE submission_submission SET status=%d, judge_result='%s', judge_detail='%s', run_time=%d, memory=%d WHERE sid=%d", res.status, result_as_string.data(), res_detail.toStyledString().data(), res.run_time, res.memory, sid);
    mysql_query(db, query);
    exit(0);
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
    OJ_conf.clear();
    string str, key, val;
    while (getline(in, str)){
        if (split(str, "=", key, val) == -1) continue;
        OJ_conf[key] = val;
    }
    in.close();
}

void generate_testcase_info(int problem_id){
    DIR *cwd = opendir(getcwd(buffer, BufferSize));
    struct dirent *entry;
    set<string> filename;
    while ((entry = readdir(cwd)) != NULL){
        string temp = string(entry->d_name);
        if (temp.find_last_of(".") == -1) continue;
        temp = temp.erase(temp.find_last_of("."));
        filename.insert(temp);
    }

    foreach(it, filename){
        sprintf(buffer, "./%s.in", it->data());
        if (access(buffer, R_OK) < 0) continue;
        sprintf(buffer, "./%s.out", it->data());
        if (access(buffer, R_OK) < 0) continue;


        sprintf(buffer, "%s.in", it->data());
        testcase.inputfile.push_back(string(buffer));
        sprintf(buffer, "%s.out", it->data());
        testcase.outputfile.push_back(string(buffer));
#ifdef DEBUG
        printf("%s\n", it->data());
#endif
    }

    sprintf(buffer, "%d.std", rand());
    testcase.user_outputfile = string(buffer);

    sprintf(query, "SELECT time_limit, memory_limit FROM problemset_problem WHERE pid=%d", problem_id);
    if (mysql_query(db, query)){
        printf("From judge_core: %s ERROR", query);
        exit(1);
    }

    MYSQL_RES *result = mysql_store_result(db);
    MYSQL_ROW row = mysql_fetch_row(result);
    testcase.time_limit = atoi(row[0]);
    testcase.memory_limit = atoi(row[1]) * 1024;
}

void finish_with_error(MYSQL *db){
    //printf("%s\n", mysql_error(db));
    mysql_close(db);
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

#ifdef DEBUG
    puts("From judge_core: connect mysql success");
#endif
    return 0;
}

int compile_source_code(string code, int lang){
    string source_file = "";
    if (lang == 0) {
	source_file = "Main.pas";
        sprintf(cmd, "fpc %s", source_file.data());
    } else if (lang == 1){
        source_file = "Main.cpp";
        sprintf(cmd, "g++ %s -o Main", source_file.data());
    }
    ofstream out;
    out.open(source_file.data(), ofstream::out);
    out << code;
    out.close();
    string info;
    FILE *info_file = popen(cmd, "r");
    while (fscanf(info_file, "%[^\n]\n", buffer) > 0){
        info += string(buffer) + "\n";
    }

    if (pclose(info_file) > 0){
        judgeResult res;
        res.message = base64_encode(reinterpret_cast<const unsigned char*>(info.c_str()), info.length());
        res.status = CE;
        Json::Value detail;
        detail["score"] = 0.0;
        detail["message"] = res.message;
        finish_judge(res, detail);
    }
}

void init(){
    read_OJconf();
#ifdef DEBUG
    puts("From judge_core: read conf finish");
#endif

    if (connect_mysql(OJ_conf["OJ_DB_USER"], OJ_conf["OJ_DB_PASSWORD"], OJ_conf["OJ_DB_NAME"]) == -1){
        exit(1);
    }

    sprintf(query, "SELECT pid_id, user_id, code, language FROM submission_submission WHERE sid=%d", sid);
    if (mysql_query(db, query)){
#ifdef DEBUG
        printf("From judge_core: query error: %d\n", sid);
#endif
        exit(1);
    }

    MYSQL_RES *result = mysql_store_result(db);
    MYSQL_ROW row = mysql_fetch_row(result);

    userinfo.problem_id = atoi(row[0]);
    userinfo.user_id = atoi(row[1]);
    userinfo.code = string(row[2]);
    userinfo.language = atoi(row[3]);

    mysql_free_result(result);

    generate_testcase_info(userinfo.problem_id);
#ifdef DEBUG
    puts("From judge_core: generate finish");
#endif

    compile_source_code(userinfo.code, userinfo.language);
#ifdef DEBUG
    puts("From judge_core: compile finish");
#endif

#ifdef DEBUG
    printf("%.2lf\n", testcase.time_limit);
    printf("%d\n", testcase.memory_limit);
    printf("%d\n", userinfo.language);
    //printf("%s\n", userinfo.code.data());
#endif
}

judgeResult judge(string prog, string inputfile, string outputfile, string user_outputfile, int time_limit, int memory_limit){
#ifdef RUNNING
    puts("Juding");
#endif
    char t_limit[16], m_limit[16];
    sprintf(t_limit, "%d", time_limit);
    sprintf(m_limit, "%d", memory_limit);
    pid_t pid;
    if ((pid = fork()) < 0){
        puts("fork error in running testcase");
    }

    if (pid == 0){
#ifdef RUNNING
        puts("RUNNING @child");
        puts(prog.data());
        puts(inputfile.data());
        puts(user_outputfile.data());
        printf("%d\n", time_limit);
        printf("%d\n", memory_limit);
#endif
        ptrace(PTRACE_TRACEME, 0, NULL, NULL);
        if (execl("/usr/bin/judge_run", "judge_run", prog.data(), inputfile.data(), user_outputfile.data(), t_limit, m_limit, NULL) == -1){
            puts("execl error");
        }
    } else{
        int status;
        struct rusage resource_info;
        int run_time = 0; //transfromTime(resource_info.ru_utime) + transfromTime(resource_info.ru_stime);
        int memory_usage = 0; //resource_info.ru_maxrss;
        while (true){
            wait4(pid, &status, WUNTRACED, &resource_info);
            run_time = transfromTime(resource_info.ru_utime) + transfromTime(resource_info.ru_stime);
            memory_usage = max(memory_usage, (int)resource_info.ru_maxrss);
            if (WIFEXITED(status)){
                break;
            } else if (WIFSIGNALED(status)){
                break;
            } else if (WIFSTOPPED(status)){
                if (run_time > time_limit || memory_usage > memory_limit){
                    ptrace(PTRACE_KILL, pid, 0, 0);
                    break;
                }
                ptrace(PTRACE_SYSCALL, pid, NULL, NULL);
            }
        }
#ifdef WATCHMEMORY
        printf("%s\n", inputfile.data());
        printf("ru_maxrss: %d\n", resource_info.ru_maxrss);
        puts("");
#endif

        if (run_time > time_limit){
            return judgeResult(run_time, memory_usage, TLE);
        }
        if (memory_usage > memory_limit){
            return judgeResult(run_time, memory_usage, MLE);
        }

        if (WIFSIGNALED(status)){
            if (WTERMSIG(status) == SIGXCPU){
                return judgeResult(run_time, memory_usage, TLE);
            } else{
                return judgeResult(run_time, memory_usage, RTE);
            }
        }
        if (access(user_outputfile.data(), F_OK) == -1){
            return judgeResult(run_time, memory_usage, UNKNOWNRES);
        }
        sprintf(cmd, "diff --strip-trailing-cr -B -w %s %s >/dev/null 2>&1", user_outputfile.data(), outputfile.data());
        status = system(cmd);
#ifdef RUNNING
        printf("=================RUNNING STATUS=========================\n");
        printf("status code: %d\n", status);
        sprintf(cmd, "cat %s", user_outputfile.data());
        system(cmd);
        sprintf(cmd, "cat %s", outputfile.data());
        system(cmd);
        printf("========================================================\n");
#endif
        if (status == 0){
            return judgeResult(run_time, memory_usage, AC);
        } else{
            return judgeResult(run_time, memory_usage, WA);
        }
    }
}

void runTestCase(){
#ifdef RUNNING
    puts("RUNNING");
#endif
    judgeResult res, temp;
    int judge_cnt;
    Json::Value finalresult, allres;
    finalresult["score"] = 0.0;
    for (int i = 0; i < testcase.size(); i++){
#ifdef RUNNING
        printf("From judge_core: Running @%d testcase\n", i);
#endif
        judge_cnt = 0;
        while (judge_cnt++ < 2){
            temp = judge("Main", testcase.inputfile[i], testcase.outputfile[i], testcase.user_outputfile, testcase.time_limit, testcase.memory_limit);
            if (temp.status != JUDGING) break;
        }
        res.update(temp);
        if (temp.status == AC) {
            double score = finalresult["score"].asDouble();
            score += 1.0 / testcase.size() * 100;
            finalresult["score"] = score;
        }

        Json::Value item;
        item["caseno"] = i;
        item["run_time"] = temp.run_time;
        item["memory"] = temp.memory;
        item["result"] = getResultAsString(temp.status);
        allres.append(item);
    }

    finalresult["allres"] = allres;
    finish_judge(res, finalresult);
}

int main(int argc, char *argv[]){
    if (argc != 3){
        puts("Usage: judge_core RunPath sid");
        exit(1);
    }

    if (chdir(argv[1]) < 0){
#ifdef DEBUG
        printf("Form judge_core: change to %s error!", argv[1]);
#endif
        exit(1);
    }

    sid = atoi(argv[2]);
    init();
    runTestCase();
#ifdef DEBUG
    puts("From judge_core: Judge finished");
#endif
    return 0;
}
