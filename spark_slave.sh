#!/bin/bash
wget https://apache.mediamirrors.org/spark/spark-3.0.1/spark-3.0.1-bin-hadoop2.7.tgz
tar -xvzf spark-3.0.1-bin-hadoop2.7.tgz
sudo apt-get install -y openjdk-8-jdk scala git
echo "JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/" >> ~/.profile && source ~/.profile
export PATH=$JAVA_HOME/bin:$PATH
export SPARK_HOME=/home/ubuntu/spark-3.0.1-bin-hadoop2.7
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
wget http://sd-127206.dedibox.fr/hagimont/software/hadoop-2.7.1.tar.gz
tar -xvzf hadoop-2.7.1.tar.gz
export HADOOP_HOME=/home/ubuntu/hadoop-2.7.1 
export PATH=$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH
javac -cp ".:$HADOOP_HOME/share/hadoop/common/hadoop-common-2.7.1.jar:$HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-client-common-2.7.1.jar:$HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-client-core-2.7.1.jar:$SPARK_HOME/jars/spark-core_2.12-3.0.1.jar:$SPARK_HOME/jars/scala-library-2.12.10.jar:$SPARK_HOME/jars/hadoop-common-2.7.4.jar" WordCount.java

jar cf wc.jar *.class
rm *.class
mv filesample.txt spark-3.0.1-bin-hadoop2.7/data
mv wc.jar spark-3.0.1-bin-hadoop2.7/jars
cd spark-3.0.1-bin-hadoop2.7
sudo ./bin/docker-image-tool.sh -t spark build

