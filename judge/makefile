TARGET = judge_core 

judge_core : judge_core.o jsoncpp.o
	g++ -o judge_core judge_core.o jsoncpp.o -I/usr/include/mysql -L/usr/bin/mysql -lmysqlclient

judge_core.o : judge_core.cpp
	g++ -c judge_core.cpp

jsoncpp.o : 
	g++ -c jsoncpp.cpp
