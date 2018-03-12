import requests
from bs4 import BeautifulSoup
import time

class SMU:
    username=''
    password=''
    xuankeID=''
    kexuhao=''
    session=requests.session()
    elecSessionTime=''
    login_headers={}
    select_data={}
    select_url=''

    def SMUlogin(self,relogin=False):
        first_url='https://cas.shmtu.edu.cn/cas/login?service=http%3A%2F%2Fjwxt.shmtu.edu.cn%2Fshmtu%2Fhome.action'
        self.login_headers={
        'Host': 'cas.shmtu.edu.cn',
        'Origin': 'https://cas.shmtu.edu.cn',
        'Referer': 'https://cas.shmtu.edu.cn/cas/login?service=http%3A%2F%2Fjwxt.shmtu.edu.cn%2Fshmtu%2Fhome.action',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        }
        # 获取cookie
        r=self.session.get(first_url,headers=self.login_headers)

        while True:
            if(relogin==False):
                self.username=input('输入学号\n')
                self.password=input('输入密码\n')
            #获取表单隐藏数据
            soup=BeautifulSoup(r.content,'lxml')
            lt=soup.find(attrs={'name':'lt'})['value']
            execution=soup.find(attrs={'name':'execution'})['value']
            login_data={
                'username':self.username,
                'password':self.password,
                'lt':lt,
                'execution':execution,
                '_eventId':'submit',
                'signin':'登录',
            }

            # 登录并重定向
            r=self.session.post(first_url,data=login_data,headers=self.login_headers,allow_redirects=False)
            if(r.status_code!=302):
                print('登录失败')
            else:
                self.login_headers['Host'] = 'jwxt.shmtu.edu.cn'
                r = self.session.get(r.next.url, headers=self.login_headers)
                soup = BeautifulSoup(r.content, 'lxml')

                try:
                    if (self.username in soup.find('a', attrs={'title': '查看登录记录'}).text):
                        print(soup.find('a', attrs={'title': '查看登录记录'}).text, ' 登录成功')
                    break
                except Exception as ex:
                    print(ex)
                    print('可能网络原因，再试一次')



    def SMUlesson(self,relogin=False):
        # 获取选课elecSessionTime
        # 779通选  781专业选修  782实践课程
        if(relogin==False):
            while True:
                self.xuankeID=input("正选：输入1通选课 输入2专业课程 输入3实习实践课程\n补选：输入4补选专业课程 输入5单独重修班 输入6补选通选课\n")
                if(self.xuankeID=='1'):
                    self.xuankeID='779'
                    break
                elif(self.xuankeID=='2'):
                    self.xuankeID='781'
                    break
                elif (self.xuankeID== '3'):
                    self.xuankeID = '782'
                    break
                elif (self.xuankeID == '4'):
                    self.xuankeID = '787'
                    break
                elif (self.xuankeID == '5'):
                    self.xuankeID = '793'
                    break
                elif (self.xuankeID == '6'):
                    self.xuankeID = '790'
                    break
        while True:
            try:
                r=self.session.get('http://jwxt.shmtu.edu.cn/shmtu/stdElectCourse!defaultPage.action?electionProfile.id='+self.xuankeID,headers=self.login_headers)
                soup=BeautifulSoup(r.content,'lxml')
                self.elecSessionTime=soup.find('input',{'id':'elecSessionTime'})['value']
                break;
            except Exception as ex:
                print(ex)
                print('正在重试，或者请关闭重来')


        # 课程信息
        r2=self.session.get('http://jwxt.shmtu.edu.cn/shmtu/stdElectCourse!data.action?profileId='+self.xuankeID,headers=self.login_headers)
        if (relogin == False):
            self.kexuhao=input('输入唯一课序号\n')
        # kexuhao='FX197005_001'
        index=r2.text.find(self.kexuhao)
        startindex=r2.text.rfind('id',0,index)+3
        endindex=r2.text.rfind(',no',0,index)
        lessonID=r2.text[startindex:endindex]
        # lessonID='168726'#婚姻法
        self.select_data={
            'operator0':lessonID+':true:0',
        }
        self.select_url = 'http://jwxt.shmtu.edu.cn/shmtu/stdElectCourse!batchOperator.action?profileId=' + self.xuankeID + '&elecSessionTime='
        self.select_url += self.elecSessionTime

    def SMUrelogin(self):
        self.SMUlogin(True)
        self.SMUlesson(True)


    def SMUdo(self):
        # 进行刷课
        while True:
            r=self.session.post(self.select_url,data=self.select_data,headers=self.login_headers)
            soup=BeautifulSoup(r.content,'lxml')
            print(soup.td.text.split())
            code = input('请按回车重试,输入q退出,输入a进入自动模式\n')
            if(code=='q'):
                exit()
            if(code=='a'):
                while True:
                    r=self.session.post(self.select_url, data=self.select_data, headers=self.login_headers)
                    soup = BeautifulSoup(r.content, 'lxml')
                    try:
                        print(soup.td.text.split())
                    except Exception as ex:
                        if('session'in r.text):
                            print(r.text)
                            print('重新登录')
                            self.session=requests.session()
                            self.SMUrelogin()
                    time.sleep(0.5)

csc=SMU()
csc.SMUlogin()
csc.SMUlesson()
csc.SMUdo()
