knap_count = 1
dem_count  = 2
ct_count = 0
knaps = {}


def mkp_read_dataset():
    with open('mknap1.txt') as f:
        lines = f.readlines()

    ct_count = int(lines[2].strip().split(' ')[0])
    dem_count = int(lines[2].strip().split(' ')[1])
    knap_count = 1

    cts = [[0 for col in range(dem_count+1)] for row in range(ct_count)] 
    for i in range(0,dem_count):
        line_per_demension = lines[i+4].strip().split(' ')
        for j in range(0,ct_count):
            cts[j][i]= line_per_demension[j]
    values = lines[3].strip().split(' ')
    for i in range(0,ct_count):
        cts[i][dem_count] = values[i]


    print(cts)
    
    knaps = [[0 for col in range(dem_count)] for row in range(knap_count)]

    for i in range(0, knap_count):
        constraints = lines[4+dem_count+i].strip().split(' ')
        for j in range(dem_count):
            knaps[i][j] = constraints[j]

    print(knaps)

ant_counts = 10

alpha = 0.5
beta = 0.5
delta = 0.5
damma = 0.5

pheromone = [[0.01 for col in range(ct_count)] for row in range(knap_count)]
optimal = [[0 for col in range(ct_count)] for row in range(knap_count)]
optimal_value = 0

# total resource vector
trv = [ 0 for row in range(dem_count)]
for i in 


if __name__ == '__main__':
    mkp_read_dataset()
        
