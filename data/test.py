from scripts.api.other.gmaputil import GMapsUtil
import time
start_time = time.time()

list = []
for i in range(200000):
    list.append({i*200/3:'hello!'})

print(list)
print("--- %s seconds ---" % (time.time() - start_time))
