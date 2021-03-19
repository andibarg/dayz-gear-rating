import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

####################################
# User input
cloths = ['headgear',
          'masks',
          'shirts and jackets',
          'hands and arms', 
          'vests',
          'backpacks',
          'pants',
          'shoes']

#####################################
# Functions

# Get slots for 3x3:
def get_slots(string):
        strx =  re.findall('\d+x\d+',string)
        if not len(strx) == 0:
            x,y = strx[0].split('x')
            return int(x)*int(y)
        else:
            return 0

##########################
# Plot colors
prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']

# Initiate plot
subs = int(np.ceil(np.sqrt(len(cloths))))
fig, ax = plt.subplots(subs,subs,sharex = True)
plt.subplots_adjust(wspace=0.7, hspace=0.2)
plt.suptitle('DayZ, Top10 clothing')
ax = ax.reshape(-1)
        
# Loop through types of clothing
for jj, cloth in enumerate(cloths):         
    # Get weights
    weights = pd.read_csv(os.path.join(os.getcwd(),'tables','weights.csv'))
    weights[weights['Name'] == cloth]
    w = np.array(weights[weights['Name'] == cloth])[0][1:]

    # File path
    fpath = os.path.join(os.getcwd(),'tables',cloth + '.txt')

    # Read file
    with open(fpath) as f:
        lines = f.readlines()

    # Select columns
    strdata = lines[3:-1]

    df = pd.DataFrame()

    for ii in range(len(strdata)):
        # Extract data
        row = strdata[ii].split('|')

        # Get name
        name = row[1].replace('[','').replace(']]','')
        name = ' '.join(re.findall('[a-zA-Z]+',name))

        # Size
        size = get_slots(row[2])

        # Capacity
        capa = get_slots(row[3])

        # Weight
        weigh = int(re.findall('\d+',row[4])[0])

        # Absorbance
        absorb = float(re.findall('\d+\.\d+|\d+',row[7])[0])

        # Insulation
        insul = float(re.findall('\d+\.\d+|\d+',row[8])[0])

        # Average protection
        protec = [float(re.findall('\d+\.\d+|\d+',x)[0]) for x in row[9:]]
        avgprotec = np.mean(protec)

        # Make dictionary
        rowdict = {'Name':name,
                   'Size':size,
                   'Capacity':capa,
                   'Weight':weigh,
                   'Absorbancy':absorb,
                   'Insulation':insul,
                   'Protection':avgprotec}

        # Append to dataframe
        df = df.append(rowdict, ignore_index=True)

    # Calculate rating
    df['Rating'] = w[0]*df['Insulation']
    df['Rating'] += w[1]*(1-df['Absorbancy']/100)
    df['Rating'] += w[2]*(1-df['Protection'])
    df['Rating'] += w[3]*(1-df['Weight']/max(df['Weight']))
    df['Rating'] += w[4]*(1-df['Size']/max(df['Size']))
    if max(df['Capacity']) != 0:
        df['Rating'] += w[5]*df['Capacity']/max(df['Capacity'])

    # Normalize rating
    df['Rating'] *= 100/sum(w)

    # Sort by rating
    df = df.sort_values('Rating',ascending=False)
    df = df.reset_index(drop=True)

    # Change column order
    df = df.reindex(columns=list(rowdict.keys()) + ['Rating'])

    # Print all results
    print(cloth)
    print(df)

    # Plot
    df.set_index('Name')['Rating'][:10].plot.barh(subplots=True, ax=ax[jj],color=colors[jj])
    ax[jj].invert_yaxis()
    ax[jj].set_title('%s' % cloth)
    ax[jj].set_ylabel('')
ax[jj].set_xlabel('Rating (%)')
ax[-1].set_axis_off()
plt.show()
