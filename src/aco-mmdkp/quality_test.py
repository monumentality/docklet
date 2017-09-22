import os
import sys

if __name__ == '__main__':
    os.system('rm -rf /home/augustin/docklet/test_result/quality_uniform_opt1.txt')
    dis = sys.argv[1]
    corr = sys.argv[2]
    for i in range(1,21):
        print("compute relax_opt when %d machines\n" % (i,))
        cmd = 'gcc -o relax_opt -DMACHINES='+str(i)+ ' -DDIS=\"\\\"'+dis+'\"\\\" -DCORR=\"\\\"'+corr+ '\"\\\" /home/augustin/docklet/src/aco-mmdkp/relax_opt.c'
        print(cmd)
        os.system(cmd)
        os.system('./relax_opt')
    for i in [60,100]:
        cmd = 'gcc -o relax_opt -DMACHINES='+str(i)+ ' -DDIS=\"\\\"'+dis+'\"\\\" -DCORR=\"\\\"'+corr+ '\"\\\" /home/augustin/docklet/src/aco-mmdkp/relax_opt.c'
        print(cmd)
        os.system(cmd)
        os.system('./relax_opt')
        
