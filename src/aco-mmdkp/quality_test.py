import os
import sys

if __name__ == '__main__':
#    os.system('rm -rf ../../test_result/quality_uniform_opt1.txt')
    dis = sys.argv[1]
    corr = sys.argv[2]
    os.system('rm -rf ../../test_result/quality_opt_'+dis+'_'+corr+'_100.txt')
    for i in range(1,21):
        print("compute relax_opt when %d machines\n" % (i,))
        cmd = 'gcc -o relax_opt -DMACHINES='+str(i)+ ' -DDIS=\"\\\"'+dis+'\"\\\" -DCORR=\"\\\"'+corr+ '\"\\\" relax_opt.c'
        print(cmd)
        os.system(cmd)
        os.system('./relax_opt')
    for i in [30,40,50,60,70,80,90,100]:
        cmd = 'gcc -o relax_opt -DMACHINES='+str(i)+ ' -DDIS=\"\\\"'+dis+'\"\\\" -DCORR=\"\\\"'+corr+ '\"\\\" relax_opt.c'
        print(cmd)
        os.system(cmd)
        os.system('./relax_opt')
        
