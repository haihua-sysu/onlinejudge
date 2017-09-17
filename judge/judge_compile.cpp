#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <string>
#include <fstream>
using std::string;
using std::ofstream;

#define DEBUG

#define CPLUSPLUS 1
#define C 2
#define CPLUSPLUS11 3
#define PYTHON 4
#define PASCAL 5

/*
 * argv[1] for filepath
 * argv[2] for filename
 * argv[3] for compiler
 * argv[4] for compile option
 */

void compile(char *cmd){
    FILE *fp = popen(cmd,"r");
    char temp[256];
    string msg="";
    while (fgets(temp,256,fp)){
        msg += temp;
    }
    if (fclose(fp) > 0){
        ofstream out;
        out.open("CE.ERROR");
        out<<msg;
        out.close();
    }
}

int getLanguageID(const string &language){
    if (language == "C++") return CPLUSPLUS;
    if (language == "C++11") return CPLUSPLUS11;
    if (language == "C") return C;
    if (language == "PYTHON") return PYTHON;
    if (language == "PASCAL") return PASCAL;
    return -1;
}

int main(int argc, char **argv){
    if (argc != 4){
        puts("Useage: ./judge_compile filepath filename language");
        return 1;
    }

    char cmd[256];
    string filepath(argv[1]),filename(argv[2]),language(argv[3]);

    int langID = getLanguageID(language);
    if (langID == -1){
        puts("Unknown language");
        return 1;
    }
    if (langID == CPLUSPLUS){
        sprintf(cmd,"g++ -w -o Main %s 2>&1",filename.c_str());
    } else if (langID == C){
        sprintf(cmd,"gcc -w -o Main %s 2>&1",filename.c_str());
    } else if (langID == CPLUSPLUS11){
        sprintf(cmd,"g++ -w -std=c++11 -o Main %s 2>&1",filename.c_str());
    } else if (langID == PYTHON){
    } else if (langID == PASCAL){
    }

    chdir(filepath.c_str());
    compile(cmd);
    return 0;
}
