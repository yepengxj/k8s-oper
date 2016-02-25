#!/usr/bin/python
# -*- coding: UTF-8 -*-

import httplib, urllib, ssl,socket
import json,base64
import os
import pandas as pd
import time
from flask import Flask, jsonify
from flask import send_from_directory
from flask import request
from urlparse import urlparse

class switch(object):
    def __init__(self, value):      # 初始化需要匹配的值value
        self.value = value
        self.fall = False           # 如果匹配到的case语句中没有break，则fall为true。
 
    def __iter__(self):
        yield self.match            # 调用match方法 返回一个生成器
        raise StopIteration         # StopIteration 异常来判断for循环是否结束
 
    def match(self, *args):         # 模拟case子句的方法
        if self.fall or not args:   # 如果fall为true，则继续执行下面的case子句
                                    # 或case子句没有匹配项，则流转到默认分支。
            return True
        elif self.value in args:    # 匹配成功
            self.fall = True
            return True
        else:                       # 匹配失败
            return False


app = Flask(__name__)

@app.route('/')
def index():
    return app.send_static_file("index.html")

@app.route('/codebase/<path:path>')
def send_codebase(path):
    print 'request_path:'+path
    root_dir = os.path.dirname(os.getcwd())
    pwd_root_dir = os.getcwd()
    print 'pwd:'+os.getcwd()
    print 'root_dir:'+root_dir
    return send_from_directory(os.path.join(pwd_root_dir, 'static', 'codebase'), path)

base_url = "console.alauda.cn"
api_url  = "api.alauda.cn"

alauda_console_head = {
    "X-CSRFToken":"xHoQLM8FK5oqb4Um5x6zU2cOng4l2pZ7",
    "X-REQUESTED-WITH":"XMLHttpRequest",
    "Cookie":'7940c0775f=".eJxVi8EOgjAQRP-lZ0Nay-623vRHyNLdBqICETgYwr9bEg96mUxm3ttMw-vSNeusr6bjuTMXE0iIInlsLfjolNQFVKuq4AjsmTzY7BXM6VduOd11kOInnqZ3dTzVtcTte_zRfQE3c9SBn1oknnvuhzw-ZCrkMhalrNnVkR3GyAlCsoKtYAiuJsLsQEi8hBoJzb5_AKhbP-g:1aXjEW:lP65rVfXIvjmJz8Ke3E2pnj1XA0"; region=BEIJING2; isin=1; 294f62ecd0=xHoQLM8FK5oqb4Um5x6zU2cOng4l2pZ7'
}

alauda_api_head = {
   "Authorization":"Token f149a1699ac58c0d6bd68814776f15d7d3d84676"
}

@app.route('/alauda/api/v1.0/new_repo', methods=['POST'])
def new_repo():
    print request.form['git_url']
    body = {"namespace":"asiainfoldp",
            "repo_name":request.form['repo_name'],
	    "code_repo_clone_url":request.form['git_url'],
	    "repo_ns":"asiainfoldp"}
    conn1 = httplib.HTTPSConnection( base_url )
    sock = socket.create_connection((conn1.host, conn1.port))
    conn1.sock = ssl.wrap_socket(sock, conn1.key_file, conn1.cert_file) ###, ssl_version=ssl.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256)
    conn1.request('POST', '/ajax/repo/simple-repo-create', json.dumps( body ), alauda_console_head)
    resp=conn1.getresponse()
    print resp.status
    ret_json = resp.read().decode('utf-8')
    conn1.close() 
    return ret_json

@app.route('/alauda/api/v1.0/list_repo', methods=['GET'])
def list_repo():
    conn1 = httplib.HTTPSConnection( api_url )
    sock = socket.create_connection((conn1.host, conn1.port))
    conn1.sock = ssl.wrap_socket(sock, conn1.key_file, conn1.cert_file) ###, ssl_version=ssl.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256)
    conn1.request('GET', '/v1/repositories/asiainfoldp/', '', alauda_api_head)
    resp=conn1.getresponse()
    print 'list_repo:resp.status:'
    print resp.status
    ret_str = resp.read().decode('utf-8')
    ret_json = json.loads( ret_str )
    pddata = pd.read_json(json.dumps(ret_json['results']),orient="records")
    pddata = pddata.sort_values(by='created_at',ascending=False)
    conn1.close() 
    return json.dumps( {'data':json.loads(pddata.to_json(date_format='iso',orient='records'))} )

@app.route('/alauda/api/v1.0/start_build', methods=['POST'])
def start_build():
    print "start_build" + request.form['repo_name']

    body = {"namespace":"asiainfoldp",
            "repo_name":request.form['repo_name'],
	    "tag":"latest"}
    print body 

    conn1 = httplib.HTTPSConnection( base_url )
    sock = socket.create_connection((conn1.host, conn1.port))
    conn1.sock = ssl.wrap_socket(sock, conn1.key_file, conn1.cert_file) ###, ssl_version=ssl.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256)
    conn1.request('POST', '/ajax/build/trigger', json.dumps( body ), alauda_console_head)
    resp=conn1.getresponse()
    print resp.status
    ret_json = resp.read().decode('utf-8')
    print ret_json
    conn1.close() 
    return ret_json

@app.route('/alauda/api/v1.0/list_build', methods=['GET'])
def list_build():
    conn1 = httplib.HTTPSConnection( api_url )
    sock = socket.create_connection((conn1.host, conn1.port))
    conn1.sock = ssl.wrap_socket(sock, conn1.key_file, conn1.cert_file) ###, ssl_version=ssl.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256)
    if(request.args.get('repo_name')):
        print '/v1/builds?namespace=asiainfoldp&repo_name='+request.args.get('repo_name')
        conn1.request('GET', '/v1/builds?namespace=asiainfoldp&repo_name='+request.args.get('repo_name'), '', alauda_api_head)
    else:
       conn1.request('GET', '/v1/builds?namespace=asiainfoldp', '', alauda_api_head)
       
    resp=conn1.getresponse()

    print resp.status
    if(resp.status == 200):
        resp_json = json.loads(resp.read().decode('utf-8'))
        pddata = pd.read_json(json.dumps(resp_json['results']),orient="records")
	pddata.ix[pddata.status == 'I','status'] = 'Inprogress' 
	pddata.ix[pddata.status == 'S','status'] = 'Success' 
	pddata.ix[pddata.status == 'W','status'] = 'Waiting' 
	pddata.ix[pddata.status == 'F','status'] = 'Fail' 
	ret_json = json.loads(pddata.to_json(orient="records",date_format='iso'))
    else:
        ret_json = {"results":""}

    conn1.close() 
    return json.dumps( {'data':ret_json} )

@app.route('/alauda/api/v1.0/get_build_status', methods=['GET'])
def get_build_status():
    return json.dumps( {'data':'true'} )

k8s_url = "ec2-54-222-140-132.cn-north-1.compute.amazonaws.com.cn:8443"

@app.route('/k8s/api/v1.0/deploy', methods=['POST'])
def image_deploy():
    dc_temp='{"kind":"DeploymentConfig","apiVersion":"v1","metadata":{"name":"docker-2048","labels":{"run":"docker-2048"}},"spec":{"strategy":{"type":"Rolling","rollingParams":{"updatePeriodSeconds":1,"intervalSeconds":1,"timeoutSeconds":600,"maxUnavailable":"25%","maxSurge":"25%"},"resources":{}},"triggers":[{"type":"ConfigChange"}],"replicas":1,"selector":{"run":"docker-2048"},"template":{"metadata":{"labels":{"run":"docker-2048"}},"spec":{"containers":[{"name":"docker-2048","image":"index.alauda.cn/asiainfoldp/docker-2048","resources":{},"terminationMessagePath":"/dev/termination-log","imagePullPolicy":"Always"}],"restartPolicy":"Always","terminationGracePeriodSeconds":30,"dnsPolicy":"ClusterFirst","securityContext":{}}}},"status":{}}'
    dc_inst =  json.loads(dc_temp)
    print dc_inst

    repo_name = request.form['repo_name']
    project_name = request.form['project_name']

    print "start_build" + request.form['repo_name']
    print "start_build" + request.form['project_name']

    dc_inst['metadata']['name']= repo_name
    dc_inst['metadata']['labels']['run']= repo_name
    dc_inst['spec']['selector']['run']= repo_name
    dc_inst['spec']['template']['metadata']['labels']['run']= repo_name
    dc_inst['spec']['template']['spec']['containers'][0]['name']= repo_name
    dc_inst['spec']['template']['spec']['containers'][0]['image']= 'index.alauda.cn/asiainfoldp/' + repo_name

    print dc_inst
    conn1 = httplib.HTTPSConnection( k8s_url )
    sock = socket.create_connection((conn1.host, conn1.port))
    conn1.sock = ssl.wrap_socket(sock, conn1.key_file, conn1.cert_file) ###, ssl_version=ssl.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256)
    auth = base64.b64encode('admin'+ ':'+ 'admin') 
    headers = {"Authorization": "Basic "+ auth,"X-CSRF-Token":1}
    conn1.request('POST',
          '/oauth/authorize?response_type=token&client_id=openshift-challenging-client', 
	  "", headers)
    resp=conn1.getresponse()
    print resp.status
    location =  resp.getheader("location")
    userl_parse = urlparse(location)
    fragment =  userl_parse.fragment

    token = ""
    for frag_split in fragment.split('&'):
       key = frag_split.split('=')
       if(key[0] == "access_token"):
           token = key[1]
	   print token
    conn1 = httplib.HTTPSConnection( k8s_url )
    sock = socket.create_connection((conn1.host, conn1.port))
    conn1.sock = ssl.wrap_socket(sock, conn1.key_file, conn1.cert_file) ###, ssl_version=ssl.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256)
    headers = {"Authorization": "Bearer "+ token}
    print headers
    conn1.request('POST',
             '/oapi/v1/namespaces/'+ project_name +'/deploymentconfigs',
	     json.dumps(dc_inst), headers)
    resp=conn1.getresponse()
    print resp.status
    ret_json = resp.read().decode('utf-8')
    print ret_json
    conn1.close()
    return json.dumps( {'data':'true'} )

@app.route('/k8s/api/v1.0/list_deploy', methods=['GET'])
def list_deploy():

    repo_name = request.args.get('repo_name')
    project_name = "paas-trainning"


    print "start_build" , request.args.get('repo_name')

    conn1 = httplib.HTTPSConnection( k8s_url )
    sock = socket.create_connection((conn1.host, conn1.port))
    conn1.sock = ssl.wrap_socket(sock, conn1.key_file, conn1.cert_file) ###, ssl_version=ssl.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256)
    auth = base64.b64encode('admin'+ ':'+ 'admin') 
    headers = {"Authorization": "Basic "+ auth,"X-CSRF-Token":1}
    conn1.request('POST',
          '/oauth/authorize?response_type=token&client_id=openshift-challenging-client', 
	  "", headers)
    resp=conn1.getresponse()
    print resp.status
    location =  resp.getheader("location")
    userl_parse = urlparse(location)
    fragment =  userl_parse.fragment

    token = ""
    for frag_split in fragment.split('&'):
       key = frag_split.split('=')
       if(key[0] == "access_token"):
           token = key[1]
	   print token
    conn1 = httplib.HTTPSConnection( k8s_url )
    sock = socket.create_connection((conn1.host, conn1.port))
    conn1.sock = ssl.wrap_socket(sock, conn1.key_file, conn1.cert_file) ###, ssl_version=ssl.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256)
    headers = {"Authorization": "Bearer "+ token}
    print headers
    conn1.request('GET',
             '/oapi/v1/namespaces/'+ project_name +'/deploymentconfigs/' + repo_name,
	     '', headers)
    resp=conn1.getresponse()
    print resp.status
    if( resp.status  == 200 ):
        resp_json = json.loads(resp.read().decode('utf-8'))
        ret_json = {'triggers': resp_json['spec']['triggers'][0]['type'],'image':resp_json['spec']['template']['spec']['containers'][0]['image'] }
    else:
        ret_json = {}
    print ret_json
    conn1.close()
    return json.dumps( {'data':[ret_json]} )


@app.route('/k8s/api/v1.0/svc', methods=['POST'])
def create_svc():

    svc_temp = '{"kind":"Service","apiVersion":"v1","metadata":{"name":"docker-2048","labels":{"run":"docker-2048"}},"spec":{"ports":[{"protocol":"TCP","port":80,"targetPort":80}],"selector":{"run":"docker-2048"},"type":"ClusterIP","sessionAffinity":"None"},"status":{"loadBalancer":{}}}'
    svc_inst =  json.loads(svc_temp)
    print svc_inst

    repo_name = request.form['repo_name']
    print "start_build" + request.form['repo_name']
    project_name = request.form['project_name']
    print "start_build" + request.form['project_name']
    port = int (request.form['port'])

    print "start_build" + request.form['port']

    svc_inst['metadata']['name']= repo_name
    svc_inst['metadata']['labels']['run']= repo_name
    svc_inst['spec']['ports'][0]['port']= port
    svc_inst['spec']['ports'][0]['targetPort']= port
    svc_inst['spec']['selector']['run']=repo_name

    print svc_inst
    conn1 = httplib.HTTPSConnection( k8s_url )
    sock = socket.create_connection((conn1.host, conn1.port))
    conn1.sock = ssl.wrap_socket(sock, conn1.key_file, conn1.cert_file) ###, ssl_version=ssl.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256)
    auth = base64.b64encode('admin'+ ':'+ 'admin') 
    headers = {"Authorization": "Basic "+ auth,"X-CSRF-Token":1}
    conn1.request('POST',
          '/oauth/authorize?response_type=token&client_id=openshift-challenging-client', 
	  "", headers)
    resp=conn1.getresponse()
    print resp.status
    location =  resp.getheader("location")
    userl_parse = urlparse(location)
    fragment =  userl_parse.fragment

    token = ""
    for frag_split in fragment.split('&'):
       key = frag_split.split('=')
       if(key[0] == "access_token"):
           token = key[1]
	   print token
    conn1 = httplib.HTTPSConnection( k8s_url )
    sock = socket.create_connection((conn1.host, conn1.port))
    conn1.sock = ssl.wrap_socket(sock, conn1.key_file, conn1.cert_file) ###, ssl_version=ssl.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256)
    headers = {"Authorization": "Bearer "+ token}
    print json.dumps(svc_inst)
    conn1.request('POST',
             '/api/v1/namespaces/'+ project_name +'/services',
	     json.dumps(svc_inst), headers)
    resp=conn1.getresponse()
    print resp.status
    ret_json = resp.read().decode('utf-8')
    print ret_json
    conn1.close()
    return json.dumps( {'data':'true'} )

@app.route('/k8s/api/v1.0/list_svc', methods=['GET'])
def list_svc():

    repo_name = request.args.get('repo_name')
    project_name = "paas-trainning"


    print "start_build" , request.args.get('repo_name')

    conn1 = httplib.HTTPSConnection( k8s_url )
    sock = socket.create_connection((conn1.host, conn1.port))
    conn1.sock = ssl.wrap_socket(sock, conn1.key_file, conn1.cert_file) ###, ssl_version=ssl.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256)
    auth = base64.b64encode('admin'+ ':'+ 'admin') 
    headers = {"Authorization": "Basic "+ auth,"X-CSRF-Token":1}
    conn1.request('POST',
          '/oauth/authorize?response_type=token&client_id=openshift-challenging-client', 
	  "", headers)
    resp=conn1.getresponse()
    print resp.status
    location =  resp.getheader("location")
    userl_parse = urlparse(location)
    fragment =  userl_parse.fragment

    token = ""
    for frag_split in fragment.split('&'):
       key = frag_split.split('=')
       if(key[0] == "access_token"):
           token = key[1]
	   print token
    conn1 = httplib.HTTPSConnection( k8s_url )
    sock = socket.create_connection((conn1.host, conn1.port))
    conn1.sock = ssl.wrap_socket(sock, conn1.key_file, conn1.cert_file) ###, ssl_version=ssl.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256)
    headers = {"Authorization": "Bearer "+ token}
    print headers
    conn1.request('GET',
             '/api/v1/namespaces/'+ project_name +'/services/' + repo_name,
	     '', headers)
    resp=conn1.getresponse()
    print resp.status
    if( resp.status  == 200 ):
        resp_json = json.loads(resp.read().decode('utf-8'))
        ret_json = {'selector': json.dumps(resp_json['spec']['selector']) ,'port':resp_json['spec']['ports'][0]['port'],'targetPort':resp_json['spec']['ports'][0]['targetPort'] }
    else:
        ret_json = {}
    print ret_json
    conn1.close()
    return json.dumps( {'data':[ret_json]} )

@app.route('/k8s/api/v1.0/router', methods=['POST'])
def create_route():

    temp = '{"kind":"Route","apiVersion":"v1","metadata":{"name":"grafana-docker","labels":{"run":"grafana-docker"}},"spec":{"host":"testst","to":{"kind":"Service","name":"grafana-docker"}},"status":{}}'
    inst =  json.loads(temp)
    print inst

    repo_name = request.form['repo_name']
    project_name = request.form['project_name']
    print "start_build" + request.form['repo_name']
    host_name = request.form['hostname']
    print "start_build" + request.form['project_name']

    inst['metadata']['name']= repo_name
    inst['metadata']['labels']['run']= repo_name
    inst['spec']['host']= host_name
    inst['spec']['to']['name']= repo_name

    print inst
    conn1 = httplib.HTTPSConnection( k8s_url )
    sock = socket.create_connection((conn1.host, conn1.port))
    conn1.sock = ssl.wrap_socket(sock, conn1.key_file, conn1.cert_file) ###, ssl_version=ssl.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256)
    auth = base64.b64encode('admin'+ ':'+ 'admin') 
    headers = {"Authorization": "Basic "+ auth,"X-CSRF-Token":1}
    conn1.request('POST',
          '/oauth/authorize?response_type=token&client_id=openshift-challenging-client', 
	  "", headers)
    resp=conn1.getresponse()
    print resp.status
    location =  resp.getheader("location")
    userl_parse = urlparse(location)
    fragment =  userl_parse.fragment

    token = ""
    for frag_split in fragment.split('&'):
       key = frag_split.split('=')
       if(key[0] == "access_token"):
           token = key[1]
	   print token
    conn1 = httplib.HTTPSConnection( k8s_url )
    sock = socket.create_connection((conn1.host, conn1.port))
    conn1.sock = ssl.wrap_socket(sock, conn1.key_file, conn1.cert_file) ###, ssl_version=ssl.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256)
    headers = {"Authorization": "Bearer "+ token}
    print "route inst:",json.dumps(inst)
    conn1.request('POST',
             '/oapi/v1/namespaces/'+ project_name +'/routes',
	     json.dumps(inst), headers)
    resp=conn1.getresponse()
    print resp.status
    ret_json = resp.read().decode('utf-8')
    print ret_json
    conn1.close()
    return json.dumps( {'data':'true'} )

@app.route('/k8s/api/v1.0/list_router', methods=['GET'])
def list_router():

    repo_name = request.args.get('repo_name')
    project_name = "paas-trainning"


    print "start_build:::::" , request.args.get('repo_name')

    conn1 = httplib.HTTPSConnection( k8s_url )
    sock = socket.create_connection((conn1.host, conn1.port))
    conn1.sock = ssl.wrap_socket(sock, conn1.key_file, conn1.cert_file) ###, ssl_version=ssl.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256)
    auth = base64.b64encode('admin'+ ':'+ 'admin') 
    headers = {"Authorization": "Basic "+ auth,"X-CSRF-Token":1}
    conn1.request('POST',
          '/oauth/authorize?response_type=token&client_id=openshift-challenging-client', 
	  "", headers)
    resp=conn1.getresponse()
    print resp.status
    location =  resp.getheader("location")
    userl_parse = urlparse(location)
    fragment =  userl_parse.fragment

    token = ""
    for frag_split in fragment.split('&'):
       key = frag_split.split('=')
       if(key[0] == "access_token"):
           token = key[1]
	   print token
    conn1 = httplib.HTTPSConnection( k8s_url )
    sock = socket.create_connection((conn1.host, conn1.port))
    conn1.sock = ssl.wrap_socket(sock, conn1.key_file, conn1.cert_file) ###, ssl_version=ssl.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256)
    headers = {"Authorization": "Bearer "+ token}
    print headers
    conn1.request('GET',
             '/oapi/v1/namespaces/'+ project_name +'/routes/' + repo_name,
	     '', headers)
    resp=conn1.getresponse()
    print resp.status
    if( resp.status  == 200 ):
        resp_json = json.loads(resp.read().decode('utf-8'))
        ret_json = {'hostname': resp_json['spec']['host'] ,'to_service':resp_json['spec']['to']['name'] }
    else:
        ret_json = {}
    print ret_json
    conn1.close()
    return json.dumps( {'data':[ret_json]} )


if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)


