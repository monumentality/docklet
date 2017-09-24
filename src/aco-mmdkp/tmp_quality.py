import os
import sys

if __name__ == '__main__':
#    os.system('rm -rf ../../test_result/quality_uniform_opt1.txt')
    dis = sys.argv[1]
    corr = sys.argv[2]


    for i in [90,100]:
        cmd = 'gcc -o relax_opt -DMACHINES='+str(i)+ ' -DDIS=\"\\\"'+dis+'\"\\\" -DCORR=\"\\\"'+corr+ '\"\\\" relax_opt.c'
        print(cmd)
        os.system(cmd)
        os.system('./relax_opt')
        
