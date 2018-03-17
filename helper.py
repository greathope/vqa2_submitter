# -*- coding:utf-8 -*-
import requests,json,os,sys
import random,string,time,config
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

def random_name(n=3):
	name = ''.join(random.sample(string.ascii_letters, n))
	return name


def login(username,password):
	login_url="https://evalapi.cloudcv.org/api/auth/login/"
	login_headers={'Accept': 'application/json, text/plain, */*',
 		'Accept-Encoding': 'gzip, deflate, br',
 		'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7',
 		'Connection': 'keep-alive',
 		'Content-Type': 'application/json;charset=UTF-8',
 		'Host': 'evalapi.cloudcv.org',
 		'Origin': 'https://evalai.cloudcv.org',
 		'Referer': 'https://evalai.cloudcv.org/auth/login',
 		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
	data={"username":username,"password":password}
	try:
		resp=requests.post(login_url,headers=login_headers,data=json.dumps(data),verify=False).json()
	except:
		return False,None
	if 'token' not in resp.keys():
		return False,None
	return True,resp['token']


def submit_file(token,files,filename="vqa_OpenEnded_mscoco_test-dev2015_model_results.json"):
 	submit_url="https://evalapi.cloudcv.org/api/jobs/challenge/1/challenge_phase/3/submission/"
 	submit_headers={'Accept': 'application/json, text/plain, */*',
 		'Accept-Encoding': 'gzip, deflate, br',
 		'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7',
 		'Authorization': "Token "+token,
 		'Connection': 'keep-alive',
 		'Host': 'evalapi.cloudcv.org',
 		'Origin': 'https://evalai.cloudcv.org',
 		'Referer': 'https://evalai.cloudcv.org/web/challenges/challenge-page/1/submission',
 		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
 	submit_files={'input_file':(filename,files)}
 	data={"status":"submitting","method_name": random_name(),"method_description": random_name(),"project_url": "N/A","publication_url": "N/A"}
 	try:
 		resp=requests.post(submit_url,headers=submit_headers,data=data,files=submit_files,verify=False).json()
 	except:
 		return False,None
 	return True,resp


def submitted_results(token):
	result_url="https://evalapi.cloudcv.org/api/jobs/challenge/1/challenge_phase/3/submission/"
	result_headers={'Accept': 'application/json, text/plain, */*',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7',
		'Authorization': "Token "+token,
		'Connection': 'keep-alive',
		'Host': 'evalapi.cloudcv.org',
		'Origin': 'https://evalai.cloudcv.org',
		'Referer': 'https://evalai.cloudcv.org/web/challenges/challenge-page/1/my-submission',
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
	payload={
    	"page":"1"
    	}
	try:
		resp=requests.get(result_url,headers=result_headers,params=payload,verify=False).json()
	except:
		return False,None
	return True,resp['results']

def get_remaining_counts(token):
	remaining_url="https://evalapi.cloudcv.org/api/jobs/1/phases/3/remaining_submissions"
	remaining_headers={'Accept': 'application/json, text/plain, */*',
 		'Accept-Encoding': 'gzip, deflate, br',
 		'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7',
 		'Authorization': 'Token '+token,
 		'Connection': 'keep-alive',
 		'Host': 'evalapi.cloudcv.org',
 		'Origin': 'https://evalai.cloudcv.org',
 		'Referer': 'https://evalai.cloudcv.org/web/challenges/challenge-page/1/submission',
 		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
	try:
		resp=requests.get(remaining_url,headers=remaining_headers,verify=False).json()
	except:
		return False,None
	return True,resp


def text2acc(address):
	print(address)
	try:
		resp=requests.get(address).text
	except:
		print("Make sure you can get access to google website!")
		return False,None
	s=resp.split('test-dev')[1]
	number=s.split("'number':")[1].split(",\n")[0].strip()
	other=s.split("'other':")[1].split(",\n")[0].strip()
	overall=s.split("'overall':")[1].split(",\n")[0].strip()
	yes_no=s.split("'yes/no':")[1].split(",\n")[0].strip().split('}}')[0]
	return True,{'number':float(number),'other':float(other),'overall':float(overall),'yes/no':float(yes_no)}

def time_count_down(text, seconds):
    count = 0
    while (count < seconds):
        count += 1
        n = seconds - count
        time.sleep(1)
        sys.stdout.write("\r" + text % (n))
        sys.stdout.flush()
        if not n:
            print("")
            return 'completed'


def run(filename,vqa_log_dir,name_passwd,json_name):
	finish_flag=False
	epoch_acc={}
	idx=int(input("**Which epoch do you want to start**"))
	max_epoch=int(input("**What is the max epoch?**"))
	for name,password in name_passwd.items():
		success,token=login(name,password)
		if success==False:
			print("Fail to get token")
			return False
		print("Got token,token is",token)

		success,resp=get_remaining_counts(token)
		if success==False:
			print("Fail to get today's remaining submissions")
			return False
		if 'remaining_submissions_today_count' not in resp.keys():
			print("%s cannot submit today"%name)
			continue
		
		remaining_today_count=resp['remaining_submissions_today_count']
		print("%s can submit %d times"%(name,remaining_today_count))
		

		epoch_id={}
		stdout=[]#get stdout
		for i in range(remaining_today_count):
			epoch_dir='epoch_'+str(idx)
			filepath=os.path.join(vqa_log_dir,epoch_dir,filename)
			files=open(filepath,'r')
			print("sucessfuly read the file,ready to submit")
			print("Please wait 30 seconds or so")

			sucess,resp=submit_file(token,files)
			if sucess==False:
				return False

			if 'id' not in resp.keys():
				return False
			print("Submitted sucessfuly")
			epoch_id[idx]=resp['id']
			
			idx+=1
			if idx == max_epoch+1:
				finish_flag=True
				break

			


		###get submitted results and
		##make sure all submissions are finished
		while True:
			sucess,resp=submitted_results(token)
			if success==False:
				print("Fail to get list of submissions!")
				return False		
			flag=True
			for j in resp:
				if j['status']=='running':
					flag=False
					text="Still running,waiting %s seconds more"
					time_count_down(text,30)
			if flag==True:
				break
		
		print("Have submitted %d epochs'test files"%(idx-1))

		for epoch,i in epoch_id.items():
			for j in resp:
				if i==j['id']:
					success=False
					while not success:
						success,test_dev=text2acc(j['stdout_file'])
						print("finding the results...")
						time.sleep(5)
					epoch_acc[epoch]=test_dev

		print("Have got %d epoch's results"%(idx-1))
		print("Write this epochs to json file in advance")
		idx_json_name='./vqa2_'+str(idx-1)+'.json'
		with open(idx_json_name,'w',encoding='utf-8') as json_file:
			json.dump(epoch_acc,json_file,ensure_ascii=False)

		if finish_flag==True:
			break
	
	print("Well done, ready to write final results to json file")
	with open(json_name,'w',encoding='utf-8') as json_file:
		json.dump(epoch_acc,json_file,ensure_ascii=False)

	return True




if __name__=='__main__':
	filename=config.filename
	vqa_log_dir=config.vqa_log_dir
	name_passwd=config.name_passwd
	json_name=config.json_name

	success=run(filename,vqa_log_dir,name_passwd,json_name)
	if success==True:
		print("Well done!")
	else:
		print("Please try again!")

















