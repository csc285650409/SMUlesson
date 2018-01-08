import requests
from bs4 import BeautifulSoup
import time

first_url='https://cas.shmtu.edu.cn/cas/login?service=http%3A%2F%2Fjwxt.shmtu.edu.cn%2Fshmtu%2Fhome.action'
login_headers={
'Host': 'cas.shmtu.edu.cn',
'Origin': 'https://cas.shmtu.edu.cn',
'Referer': 'https://cas.shmtu.edu.cn/cas/login?service=http%3A%2F%2Fjwxt.shmtu.edu.cn%2Fshmtu%2Fhome.action',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
}
# 获取cookie
session=requests.session()
r=session.get(first_url,headers=login_headers)

username=input('输入学号\n')
password=input('输入密码\n')
#获取表单隐藏数据
soup=BeautifulSoup(r.content,'lxml')
lt=soup.find(attrs={'name':'lt'})['value']
execution=soup.find(attrs={'name':'execution'})['value']
login_data={
    'username':username,
    'password':password,
    'lt':lt,
    'execution':execution,
    '_eventId':'submit',
    'signin':'登录',
}

# 登录并重定向
r=session.post(first_url,data=login_data,headers=login_headers,allow_redirects=False)
if(r.status_code!=302):
    print('登录失败')
    exit()
login_headers['Host']='jwxt.shmtu.edu.cn'
r=session.get(r.next.url,headers=login_headers)
soup=BeautifulSoup(r.content,'lxml')

if(username in soup.find('a',attrs={'title':'查看登录记录'}).text):
    print(soup.find('a',attrs={'title':'查看登录记录'}).text,' 登录成功')
else:
    print('登录失败')
    exit()

# 获取选课elecSessionTime
r=session.get('http://jwxt.shmtu.edu.cn/shmtu/stdElectCourse!defaultPage.action?electionProfile.id=779',headers=login_headers)
soup=BeautifulSoup(r.content,'lxml')
elecSessionTime=soup.find('input',{'id':'elecSessionTime'})['value']

# 课程信息
r2=session.get('http://jwxt.shmtu.edu.cn/shmtu/stdElectCourse!data.action?profileId=779',headers=login_headers)

kexuhao=input('输入唯一课序号\n')
# kexuhao='FX197005_001'
index=r2.text.find(kexuhao)
startindex=r2.text.rfind('id',0,index)+3
endindex=r2.text.rfind(',no',0,index)
lessonID=r2.text[startindex:endindex]
# lessonID='168726'#婚姻法
select_data={
    'operator0':lessonID+':true:0',
}

# 进行刷课
select_url='http://jwxt.shmtu.edu.cn/shmtu/stdElectCourse!batchOperator.action?profileId=779&elecSessionTime='
select_url+=elecSessionTime
while True:
    r=session.post(select_url,data=select_data,headers=login_headers)
    soup=BeautifulSoup(r.content,'lxml')
    print(soup.td.text.split())
    code = input('请按回车重试,输入q退出,输入a进入自动模式\n')
    if(code=='q'):
        exit()
    if(code=='a'):
        while True:
            r=session.post(select_url, data=select_data, headers=login_headers)
            soup = BeautifulSoup(r.content, 'lxml')
            print(soup.td.text.split())
            time.sleep(0.5)
