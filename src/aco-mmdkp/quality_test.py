import os

if __name__ == '__main__':
    os.system('rm -rf /home/augustin/docklet/test_result/quality_uniform_opt1.txt')
    for i in range(1,21):
        print("compute relax_opt when %d machines\n" % (i,))
        os.system('gcc -o relax_opt -DMACHINES='+str(i)+' relax_opt.c')
        os.system('./relax_opt')
    for i in [30,40,50,100]:
        os.system('gcc -o relax_opt -DMACHINES='+str(i)+' relax_opt.c')
        os.system('./relax_opt')
