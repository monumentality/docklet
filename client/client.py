import click
import os
import requests
import json

@click.group()
@click.option('--verbose',is_flag=True,help="flag, to run in verbose mode")
@click.pass_context
def main(ctx,verbose):
    '''
    docklet command line client
    '''
    ctx.obj={}
    ctx.obj['verbose']=verbose
    if os.path.exists(os.environ['HOME']+"/.docklet"):
        docklet_file = open(os.environ['HOME']+"/.docklet","r")
        ctx.obj= json.loads(docklet_file.read())
#        print(ctx.obj)
    if verbose:
        print('running in verbose mode')

@main.command()
@click.option('--server',help='the ip address of the docklet httprest server', default='0.0.0.0')
@click.option('--port',help='the port of the docklet httprest server',default='9000')
@click.option('--username',help="the username on this server you specified", prompt=True)
@click.option('--password',help="the password on this server you specified",prompt=True, hide_input=True)
@click.pass_context
def login(ctx,server,port,username,password):
    '''
    login your docklet instance
    '''
    if(server != "iwork.pku.edu.cn"):
        data = {"user": username, "key": password}
        url = 'http://'+server+':'+port+'/login/'
        result = requests.post(url, data = data).json()
#        click.echo(result)
        if result.get('success')=='false':
            click.echo('The password doesn\'t match the user! Failed to login!')
            return
        else:
            click.echo('Login already!')
        token= result.get('data').get('token')
#        print(token)
        docklet_file = open(os.environ['HOME']+"/.docklet","w")
        docklet_data={'server':server,'port':port,'token':token}
        docklet_file.write(json.dumps(docklet_data))
    else:
        loginpku(ctx,server,port,username,password)


    
def loginpku(ctx,server,port,username,password):
    session = requests.Session()

    # HEAD requests ask for *just* the headers, which is all you need to grab the
    # session cookie
    session.head('https://iaaa.pku.edu.cn/iaaa/oauth.jsp')

    response = session.post(
            url='https://iaaa.pku.edu.cn/iaaa/oauthlogin.do',
            data={
                        'appid': 'iwork',
                        'userName': username,
                        'password': password,
                        'randCode': "验证码",
                        'smsCode': "短信验证码",
                        'redirUrl':"http://iwork.pku.edu.cn/pkulogin"
                    },
            headers={
                        'Referer': 'https://iaaa.pku.edu.cn/iaaa/oauth.jsp'
                    }
        )
    token=response.json().get('token')
    print(token)
    token_file = open(os.environ['HOME']+"/.docklet","w")
    token_file.write(token)
    

@main.group()
@click.pass_context
def workspace(ctx):
    '''
    manage your workspaces
    '''
#    click.echo(ctx.obj['token'])

@workspace.command("create")
@click.pass_context
@click.option('--cluster_name',help="set the name of the cluster to be created",prompt=True)
@click.option('--cluster_size',help="set the cluster size",prompt=True)
@click.option('--container_size',help="set the container size",prompt=True)
@click.option('--bidprice',help="set bidprice",prompt=True)
def workspace_create(ctx, cluster_name, cluster_size, container_size, bidprice):
    '''
    create a workspace
    '''
    url = 'http://'+ctx.obj['server']+':'+ctx.obj['port']+'/cluster/create/'
    data = {'token': ctx.obj['token'], 'clustername': cluster_name, 
            'cluster_size': cluster_size, 'container_size': container_size, 'bidprice': bidprice,
            'imagename': 'base', 'imagetype': 'base', 'imageowner': 'base'}
    result = requests.post(url, data = data).json()
#    print(result)
    if(result.get('success') == 'false'):
        click.echo('\nFailed! ' + result.get('message'))
        return
    click.echo('\nSucceed to create cluster ' + cluster_name +'!')
    msg = result.get('message')
#    print(msg)
    click.echo('--Cluster Id: ' + str(msg.get('clusterid')))
    click.echo('--Create Time: ' + str(msg.get('create_time')))
    click.echo('--Status: ' + str(msg.get('status')))


@workspace.command("delete")
@click.pass_context
@click.option('--cluster_name',help="the name of the cluster to be deleted",prompt=True)
def workspace_delete(ctx, cluster_name):
    '''
    delete a workspace
    '''
    url = 'http://'+ctx.obj['server']+':'+ctx.obj['port']+'/cluster/delete/'
    data = {'token': ctx.obj['token'], 'clustername': cluster_name}
    result = requests.post(url, data = data).json()
#    print(result)
    if(result.get('success') == 'false'):
        click.echo('\nFailed! ' + result.get('message'))
        return
    click.echo('\nSucceed to delete cluster ' + cluster_name +'!')


@workspace.command("start")
@click.pass_context
@click.option('--cluster_name',help="the name of the cluster to be started",prompt=True)
def workspace_start(ctx, cluster_name):
    '''
    start a workspace
    '''
    url = 'http://'+ctx.obj['server']+':'+ctx.obj['port']+'/cluster/start/'
    data = {'token': ctx.obj['token'], 'clustername': cluster_name}
    result = requests.post(url, data = data).json()
#    print(result)
    if(result.get('success') == 'false'):
        click.echo('\nFailed! ' + result.get('message'))
        return
    click.echo('\nSucceed to start cluster ' + cluster_name +'!')


@workspace.command("stop")
@click.pass_context
@click.option('--cluster_name',help="the name of the cluster to be stopped",prompt=True)
def workspace_stop(ctx, cluster_name):
    '''
    stop a workspace
    '''
    url = 'http://'+ctx.obj['server']+':'+ctx.obj['port']+'/cluster/stop/'
    data = {'token': ctx.obj['token'], 'clustername': cluster_name}
    result = requests.post(url, data = data).json()
#    print(result)
    if(result.get('success') == 'false'):
        click.echo('\nFailed! ' + result.get('message'))
        return
    click.echo('\nSucceed to stop cluster ' + cluster_name +'!')


@workspace.command("scalein")
@click.pass_context
@click.option('--cluster_name',help="#--?",prompt=True)
@click.option('--container_name',help="#--?",prompt=True)
def workspace_scalein(ctx, cluster_name, container_name):
    '''
    Release node from a certain cluster
    '''
    url = 'http://'+ctx.obj['server']+':'+ctx.obj['port']+'/cluster/scalein/'
    data = {'token': ctx.obj['token'], 'clustername': cluster_name, 'containername': container_name}
    result = requests.post(url, data = data).json()
#    print(result)
    if(result.get('success') == 'false'):
        click.echo('\nFailed! ' + result.get('message'))
        return
    click.echo('\nSucceed!')


@workspace.command("scaleout")
@click.pass_context
@click.option('--cluster_name',help="#--?",prompt=True)
def workspace_scaleout(ctx, cluster_name):
    '''
    Add node to a certain cluster
    '''
    url = 'http://'+ctx.obj['server']+':'+ctx.obj['port']+'/cluster/scaleout/'
    data = {'token': ctx.obj['token'], 'clustername': cluster_name, 'imagetype': 'base', 'imagename': 'base', 'imageowner': 'base'}
    result = requests.post(url, data = data).json()
#    print(result)
    if(result.get('success') == 'false'):
        click.echo('\nFailed! ' + result.get('message'))
        return
    click.echo('\nSucceed!')  

@workspace.command("list")
@click.pass_context
def workspace_list(ctx):
    '''
    list all the workspaces you created
    '''
    url = 'http://'+ctx.obj['server']+':'+ctx.obj['port']+'/cluster/list/'
    data = {'token': ctx.obj['token']}
    result = requests.post(url, data = data).json()
#    print(result)
    if(result.get('success') == 'false'):
        click.echo('You haven\'t login! Please login first')
        return
    wkspaces = result.get('clusters')
    for wkspace in wkspaces:
        click.echo(wkspace)

@workspace.command("info")
@click.pass_context
@click.option('--clustername',help="the name of the cluster to see its info",prompt=True)
def workspace_info(ctx, clustername):
    '''
    show the infomation of workspaces
    '''
    url = 'http://'+ctx.obj['server']+':'+ctx.obj['port']+'/cluster/info/'
    data = {'token': ctx.obj['token'], 'clustername': clustername}
    result = requests.post(url, data = data).json()
#    print(result)
    if(result.get('success') == 'false'):
        click.echo('No such cluster, please check.')
        return
    click.echo('Information of vluster ' + clustername)
    msg = result.get('message')
#    print(msg)
    click.echo('Cluster Id: ' + str(msg.get('clusterid')))
    click.echo('Create Time: ' + str(msg.get('create_time')))
    click.echo('Size: ' + str(msg.get('size')))
    click.echo('Status: ' + str(msg.get('status')))
    if (msg.get('status')=='running'):
        click.echo('Start Time: ' + str(msg.get('start_time')))

    click.echo('Container information: ')
    conmsgs = msg.get('containers')
    concnt = 1
    for conmsg in conmsgs:   
        click.echo('--Container '+ str(concnt) + '--')
        click.echo('IP: ' + str(conmsg.get('ip')))
        click.echo('Image: ' + str(conmsg.get('image')))
        click.echo('Host: ' + str(conmsg.get('host')))
        click.echo('Lastsave: ' + str(msg.get('lastsave')))
        concnt += 1

@main.group()
@click.pass_context
def user(ctx):
    '''
    manage users
    '''

@user.command("modify")
@click.argument("userid")
@click.argument("field")
@click.option('--newvalue',help="new value of the field",prompt=True)
@click.pass_context
def user_modify(ctx, userid, field, newvalue):
    '''
    Modify value of FIELD of user (with USERID)
    '''
    if field not in ['department', 'tel', 'e_mail', 'truename', 'status', 'student_number', 'group']:
        click.echo('Failed! The FIELD you name do not exist or is not allowde to modify!')
        return
    url = 'http://'+ctx.obj['server']+':'+ctx.obj['port']+'/user/query/'
    data = {'token': ctx.obj['token'], 'ID': userid}
    result = requests.post(url, data = data).json()
#    print(result)
    if(result.get('success') == 'false'):
        click.echo('\nFailed! ' + result.get('message'))
        return
#    click.echo('Succeed!')
    data = result.get('data')
    
    url = 'http://'+ctx.obj['server']+':'+ctx.obj['port']+'/user/modify/'
    data['token'] = ctx.obj['token']
    data[field] = newvalue
#    print (data)
    result = requests.post(url, data = data).json()
    print(result)
    if(result.get('success') == 'false'):
        click.echo('Failed! '+result.get('message'))
        return
    click.echo('Succeed to modify!')

#@user.command("groupmodify")
#@click.pass_context
#def user_group_modify(ctx):
    
@user.command("add")
@click.pass_context
@click.option('--user_name',help="set the name of the user to be added",prompt=True)
@click.option('--password',help="set the password",prompt=True, hide_input=True)
@click.option('--email',help="set the Email",prompt=True)
def user_add(ctx, user_name, password, email):
    '''
    add a user
    '''
    url = 'http://'+ctx.obj['server']+':'+ctx.obj['port']+'/user/add/'
    data = {'token': ctx.obj['token'], 'username': user_name, 
            'password': password, 'ID':1, 'e_mail': email}
    result = requests.post(url, data = data).json()
#    print(result)
    if(result.get('success') == 'false'):
        click.echo('\nFailed! ' + result.get('message'))
        return
    else:
        click.echo('Succeed to add user '+ user_name + '!')

@user.command("query")
@click.option('--id',help="to query the information of the user with given ID",prompt=True)
@click.pass_context
def user_query(ctx, id):
    '''
    query all the users
    '''
    url = 'http://'+ctx.obj['server']+':'+ctx.obj['port']+'/user/query/'
    data = {'token': ctx.obj['token'], 'ID': id}
    result = requests.post(url, data = data).json()
#    print(result)
    if(result.get('success') == 'false'):
        click.echo('\nFailed! ' + result.get('message'))
        return
    msg = result.get('data')
    click.echo('Succeed!')
    click.echo('Username: ' + str(msg.get('username')))
    click.echo('Nickname: ' + str(msg.get('nickname')))
    click.echo('Truename: ' + str(msg.get('truename')))
    click.echo('Department: ' + str(msg.get('department')))
    click.echo('Student Id: ' + str(msg.get('student_number')))
    click.echo('Email: ' + str(msg.get('e_mail')))
    click.echo('Telephone: ' + str(msg.get('tel')))
    click.echo('Description: ' + str(msg.get('description')))
    click.echo('Register Date: ' + str(msg.get('register_date')))
    click.echo('Status: ' + str(msg.get('status')))
    click.echo('Group: ' + str(msg.get('group')))
    click.echo('Auth method: ' + str(msg.get('auth_method')))
    
@user.command("data")
@click.pass_context
def user_data(ctx):
    '''
    show brief information of all the users
    '''
    url = 'http://'+ctx.obj['server']+':'+ctx.obj['port']+'/user/data/'
    data = {'token': ctx.obj['token']}
    result = requests.post(url, data = data).json()
#    print(result)
    if(result.get('success') == 'false'):
        click.echo('\nFailed! ' + result.get('message'))
        return
    click.echo('Succeed!')
    info = result.get('data')
    for msg in info:
        click.echo('------------------------')
        click.echo('User ID: ' + str(msg[0]))
        click.echo('Username: ' + str(msg[1]))
        click.echo('?: ' + str(msg[2]))
        click.echo('Email: ' + str(msg[3]))
        click.echo('?: ' + str(msg[4]))
        click.echo('Register Date: ' + str(msg[5]))
        click.echo('Status: ' + str(msg[6]))
        click.echo('Group: ' + str(msg[7]))
        click.echo('?: ' + str(msg[8]))

@user.command("allgroups")
@click.pass_context
def user_allgroups(ctx):
    '''
    show information of all the groups
    '''
    url = 'http://'+ctx.obj['server']+':'+ctx.obj['port']+'/user/groupList/'
    data = {'token': ctx.obj['token']}
    result = requests.post(url, data = data).json()
#    print(result)
    if(result.get('success') == 'false'):
        click.echo('\nFailed! ' + result.get('message'))
        return
#    click.echo('Succeed!')
    gps = result.get('groups')
    for gp in gps:
        click.echo('---------Group Name: '+gp.get('name')+'---------')
        info = gp.get('quotas')
        for item in info:
            click.echo(item+': '+info[item])

@user.command("groupquery")
@click.option('--group_name',help="the name of the group you want to query",prompt=True)
@click.pass_context
def user_gquery(ctx, group_name):
    '''
    get information of a certain group
    '''
    url = 'http://'+ctx.obj['server']+':'+ctx.obj['port']+'/user/groupQuery/'
    data = {'token': ctx.obj['token'], 'name': group_name}
    result = requests.post(url, data = data).json()
#    print(result)
    if(result.get('success') == 'false'):
        click.echo('\nFailed! ' + result.get('message'))
        return
    if(result.get('success') == False):
        click.echo('\nFailed! ' + result.get('reason'))
        return
#    click.echo('Succeed!')
    info = result.get('data')
    for item in info:
        click.echo(item+': '+info[item])

@user.command("selfquery")
@click.pass_context
def user_gquery(ctx):
    '''
    get information of current user
    '''
    url = 'http://'+ctx.obj['server']+':'+ctx.obj['port']+'/user/selfQuery/'
    data = {'token': ctx.obj['token']}
    result = requests.post(url, data = data).json()
#    print(result)
    if(result.get('success') == 'false'):
        click.echo('\nFailed! ' + result.get('message'))
        return
#    click.echo('Succeed!')
    info = result.get('data')
    for item in info:
        if item == 'password':
            continue
        if item == 'groupinfo':
            ginfo = info[item]
            click.echo('group information:')
            for gitem in ginfo:
                click.echo('  '+gitem+': '+ginfo[gitem])
        else:
            click.echo(item+': '+info[item])

@user.command("selfmodify")
@click.argument("field")
@click.option('--newvalue',help="new value of the field",prompt=True)
@click.pass_context
def user_smodify(ctx, field, newvalue):
    '''
    Modify value of FIELD of current user
    '''
    if field not in ['department', 'tel', 'e_mail', 'truename', 'status', 'student_number', 'group']:
        click.echo('Failed! The FIELD you name do not exist or is not allowde to modify!')
        return
    url = 'http://'+ctx.obj['server']+':'+ctx.obj['port']+'/user/selfQuery/'
    data = {'token': ctx.obj['token']}
    result = requests.post(url, data = data).json()
#    print(result)
    if(result.get('success') == 'false'):
        click.echo('\nFailed! ' + result.get('message'))
        return
#    click.echo('Succeed!')
    data = result.get('data')
    
    url = 'http://'+ctx.obj['server']+':'+ctx.obj['port']+'/user/modify/'
    data['token'] = ctx.obj['token']
    data[field] = newvalue
#    print (data)
    result = requests.post(url, data = data).json()
    print(result)
    if(result.get('success') == 'false'):
        click.echo('Failed! '+result.get('message'))
        return
    click.echo('Succeed to modify!')

@main.group()
@click.pass_context
def monitor(ctx):
    '''
    get information recorded by monitor
    '''

@monitor.command("hostquery")
@click.option('--host',help="the name of the host you want to query",prompt=True)
@click.option('--issue',help="which issue to query",prompt=True)
@click.pass_context
def monitor_hquery(ctx, host, issue):
    '''
    query the given issue of a certain host
    '''
    url = 'http://'+ctx.obj['server']+':'+ctx.obj['port']+'/monitor/hosts/'+host+'/'+issue+'/'
    data = {'token': ctx.obj['token']}
    result = requests.post(url, data = data).json()
#    print(result)
    if(result.get('success') == 'false'):
        click.echo('\nFailed! ' + result.get('message'))
        return
#    click.echo('Succeed!')
    info = result.get('monitor').get(issue)
    if issue == 'cpuconfig' or issue == 'diskinfo'or issue == 'containerinfo':
        for iinfo in info:
            click.echo('--------')
            for item in iinfo:
                click.echo(item + ': ' + str(iinfo[item]))
        return
    if  issue == 'status':
        click.echo(info)
        return
    if issue == 'containerslist':
        for item in info:
            click.echo(item)
        return
    for item in info:
        click.echo(item + ': ' + str(info[item]))

@monitor.command("vnodequery")
@click.option('--container_name',help="the name of the container you want to query",prompt=True)
@click.option('--issue',help="which issue to query",prompt=True)
@click.pass_context
def monitor_nquery(ctx, container_name, issue):
    '''
    query the given issue of a certain container
    '''
    url = 'http://'+ctx.obj['server']+':'+ctx.obj['port']+'/monitor/vnodes/'+container_name+'/'+issue+'/'
    data = {'token': ctx.obj['token']}
    result = requests.post(url, data = data).json()
#    print(result)
    if result.get('success') == 'false':
        click.echo('\nFailed! ' + result.get('message'))
        return
    if result.get('monitor') == 'Unspported Method!':
        click.echo('\nFailed! ' + result.get('monitor'))
        return
#    click.echo('Succeed!')
    if issue == 'owner':
        click.echo('Username: ' + result.get('monitor').get('username'))
        click.echo('Truename: ' + result.get('monitor').get('truename'))
        return
    info = result.get('monitor').get(issue)
    for item in info:
        click.echo(item + ': ' + str(info[item]))

@monitor.command("quotainfo")
@click.pass_context
def monitor_qinfo(ctx):
    '''
    show quota information
    '''
    url = 'http://'+ctx.obj['server']+':'+ctx.obj['port']+'/monitor/user/quotainfo/'
    data = {'token': ctx.obj['token']}
    result = requests.post(url, data = data).json()
#    print(result)
    if(result.get('success') == 'false'):
        click.echo('\nFailed! ' + result.get('message'))
        return
    info = result.get('quotainfo')
    for item in info:
        click.echo(item + ': ' + info[item])

@monitor.command("list")
@click.pass_context
def monitor_list(ctx):
    '''
    list all physical nodes
    '''
    url = 'http://'+ctx.obj['server']+':'+ctx.obj['port']+'/monitor/listphynodes/'
    data = {'token': ctx.obj['token']}
    result = requests.post(url, data = data).json()
#    print(result)
    if(result.get('success') == 'false'):
        click.echo('\nFailed! ' + result.get('message'))
        return
    info = result.get('monitor').get('allnodes')
    for item in info:
        click.echo(item)

if __name__=="__main__":
    main()
