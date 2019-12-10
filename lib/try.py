import matplotlib
import matplotlib.pyplot as plt
import numpy as np

max_values = np.array((34, 29, 20, 5))
cur_values = np.array((33, 14, 15, 1))
result = (cur_values/max_values)*100

items = ['Biologisk mångfald', 'Sociala värden', 'Klimatanpassning', 'Ljudkvalitet']
cmap = [
    [0.36, 0.97, 0.41, 0.8], # green
    [1, 0.8, 0, 0.8], # orange
    [0.6, 0.8, 1, 0.8], # blue
    [0.5, 0, 0, 0.8], # maroon
]
x = np.arange(len(items))
for i in x:
    plt.bar(x[i], result[i], align='center', alpha=0.5, color=cmap[i], label=items[i])
plt.xticks(x, items)
plt.title('Balancering av möjliga faktorer')
#plt.legend()
#plt.tight_layout()
plt.show()