rm judged judge_run judge_core
g++ -c jsoncpp.cpp
g++ -c judge_core.cpp
g++ -c base64.cpp
g++ -o judge_core base64.o judge_core.o jsoncpp.o -I ./include -I/usr/include/mysql -L/usr/bin/mysql -lmysqlclient
g++ -o judge_run judge_run.cpp
g++ -o judged judged.cpp -I ./include -I/usr/include/mysql -L/usr/bin/mysql -lmysqlclient
