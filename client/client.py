import click
import os

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
        token_file = open(os.environ['HOME']+"/.docklet","r")
        ctx.obj['token']=token_file.read()
    
    if verbose:
        print('running in verbose mode')

@main.command()
@click.option('--username',help="this is your pku id")
@click.option('--password',help="this is the password for you pku id")
@click.pass_context
def login(ctx,username,password):
    '''
    login using your pku id and password
    '''
    from requests import Session

    session = Session()

    # HEAD requests ask for *just* the headers, which is all you need to grab the
    # session cookie
    session.head('https://iaaa.pku.edu.cn/iaaa/oauth.jsp')

    response = session.post(
            url='https://iaaa.pku.edu.cn/iaaa/oauthlogin.do',
            data={
                        'appid': 'iwork',
                        'userName': '1401214302',
                        'password': 'fabrega4',
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
    click.echo(ctx.obj['token'])

@workspace.command("create")
@click.pass_context
def workspace_create(ctx):
    '''
    create a workspace
    '''

if __name__=="__main__":
    main()
