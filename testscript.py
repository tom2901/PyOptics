#%%
import cairo
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import math
import opticaltable as ot

# %%
WIDTH, HEIGHT = 512, 256

test = ot.OpticalTable(WIDTH, HEIGHT, 'example.svg', border=True)
obj1 = test.mirror(100, 100, 135, label='', label_pos='inside', scale=3)
obj2 = test.mirror(200, 100, 45, label='', label_pos='right', scale=3)
obj3 = test.mirror(100,200, 45, label='', label_pos='below', scale=3)
obj4 = test.genericBox(200,200,50,20,0, fill=True, fillcolor=(0,1,0), label='', label_pos='inside', labelsize=5)
point1 = test.pathObject(300,50)
path = [obj1, obj2, obj3, obj4,point1]
beam1 = test.beam(path, (0,0,0), arrows=True, fiber=True)
test.draw_elements()
# %%
