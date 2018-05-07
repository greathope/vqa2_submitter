# vqa2_submitter
Automatically VQA v2 submitter

#### First:
  Make sure you have installed ssdb, then go to /usr/local/ssb, type ./ssdb-server ssdb.conf [Details](https://www.cnblogs.com/chenny7/p/4569837.html)
  
#### Second:
 clone this [repo](https://github.com/jhao104/proxy_pool)

#### Finally:
  You have to change your setup in config.py, including filename,vqa_log_dir,name_passwd,and json_name,
  then run helper.py,it will automatically submit these test files to server, and you will get all test results
  in your json files.
