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
#        print(result)
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
def workspace_create(ctx):
    '''
    create a workspace
    '''

@workspace.command("list")
@click.pass_context
def workspace_list(ctx):
    '''
    list all the workspaces you created
    '''
    url = 'http://'+ctx.obj['server']+':'+ctx.obj['port']+'/cluster/list/'
    data = {'token': ctx.obj['token']}
    result = requests.post(url, data = data).json()
    print(result)

if __name__=="__main__":
    main()
