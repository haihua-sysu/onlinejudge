#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <sys/times.h>
#include <sys/wait.h>
#include <dirent.h>

#define MAXLEN 256 
#define DEBUG

#define transfromTime(t) (t.tv_sec*1000 + t.tv_usec/1000)

struct testCase{
	vector<int> inputfile, outputfile;
	string user_outputfile;
	double time_limit;
} testcase;

int judge(char *filepath, char *filename, char *inputfile, char *outputfile, char *stdoutputfile, char *time_limit, int firstCase){
	char cmd[MAXLEN];
	pid_t pid;
	int status;
	if (firstCase){
		if ((pid = fork())<0){
			puts("fork error in compile");
			return 1;
		} else if (!pid){
			execl("/home/acfast/OJ/core/judge_compile","judge_compile",filepath,filename,"C++",NULL);
			exit(0);
		} else{
			wait(&status);
			char cefile[MAXLEN];
			sprintf(cefile,"%s%s",filepath,"CE.ERROR");
			if (access(cefile,F_OK)!=-1){
				sprintf(cmd,"%s%s","rm -f ",cefile);
				system(cmd);
				puts("Compile Error");
				return 0;
			}
		}
	}

	if ((pid = fork())<0){
		puts("fork error in running");
		return 1;
	} else if (!pid){
		execl("/home/acfast/OJ/core/judge_run","judge_run",filepath,"Main",inputfile,outputfile,time_limit,NULL);
		exit(0);
	} else{
		struct rusage resource_info;
		wait4(pid,&status,0,&resource_info);
		int time_usage=transfromTime(resource_info.ru_utime)+transfromTime(resource_info.ru_stime);
		if (WIFSIGNALED(status)){
			if (WTERMSIG(status) == SIGXCPU){
				printf("testCase %s : RunTime:%d ms Time Limit Execced\n",inputfile,time_usage);
			} else {
				printf("testCase %s : RunTime:%d ms Run Time Error\n",inputfile,time_usage);
			}
			return 0;
		}
		char user_output_file[MAXLEN],std_output_file[MAXLEN];
		sprintf(std_output_file,"%s%s",filepath,stdoutputfile);
		sprintf(user_output_file,"%s%s",filepath,outputfile);
		if (access(user_output_file, F_OK)==-1){
			printf("testCase %s : User output file not found\n",inputfile);
			return 0;
		}
		if (access(std_output_file, F_OK)==1){
			printf("testCase %s : Standard output file not found\n",inputfile);
			return 0;
	}
		sprintf(cmd, "diff --strip-trailing-cr -Z -B -w %s %s >/dev/null 2>&1\n", user_output_file, std_output_file);
		status = system(cmd);
		printf("testCase %s : RunTime:%d ms ",inputfile,time_usage);
		if (status == 0) puts("Accepted"); else puts("Wrong Answer");
	}
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

void generate_testcase_info(){
}

void finish_with_error(MYSQL *db){
	syslog(LOG_INFO, mysql_error(db));
	mysql_close(db);
}

int connect_mysql(const string &user, const string &password, const string &db_name){
	db = mysql_init(NULL);
	if (db == NULL){
		finish_with_error(db);
		return -1;
	}

	if (mysql_real_connect(db, "localhost", user.c_str(), password.c_str(), db_name.c_str(), 0, NULL, 0) == NULL){
		printf("%s\n", mysql_error(db));
		finish_with_error(db);
		return -1;
	}

	puts("connect mysql success");
	return 0;
}

void init(){
	read_OJconf();
	generate_testcase_info();
	if (connect_mysql(OJ_conf["OJ_DB_USER"], OJ_conf["OJ_DB_PASSWORD"], OJ_conf["OJ_DB_NAME"]) == -1){
		error_quit("connected mysql failed!");
		exit(1);
	}
}

int main(int argc, char *argv[]){
	if (argc != 2){
		puts("Usage: judge_core RunPath sid");
		exit(1);
	}

	if (chdir(RunPath) < 0){
		printf("change to %s error!", RunPath);
		exit(1);
	}

	init();
	runTestCase();
	return 0;
}
