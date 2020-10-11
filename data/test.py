from scripts.api.other.gmaputil import GMapsUtil
import time
start_time = time.time()

list = []
for i in range(200000):
    list.append({i*200/3:'hello!'})

    # bad comments:
    # ajsldkfjaldskfja
    # laksdjfklasdjfkl
    # laksfjlkasjdfk
    # alsdkfjalksdfj

print(list)
print("--- %s seconds ---" % (time.time() - start_time))
