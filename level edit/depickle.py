import pickle

file = "level7_data"
fileobj = open(file,'rb')
lvl = pickle.load(fileobj)

print(lvl)

