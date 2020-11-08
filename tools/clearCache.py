import os
import glob

tools = os.path.dirname(__file__)
root = os.path.dirname(tools)

if __name__ == '__main__':
    mapFilesCacheDir = os.path.join(root, 'data', 'state', 'maps.open', '*', '*')
    cacheFiles = glob.glob(mapFilesCacheDir)
    removed = 0
    for cache in cacheFiles:
        try:
            os.remove(cache)
            removed = removed + 1
        except Exception as e:
            print(e)
    print("{0}/{1} map's files was removed.".format(removed, len(cacheFiles)))

    mapCacheDir = os.path.join(root, 'data', 'state', 'maps.open', '*')
    cacheFolders = glob.glob(mapCacheDir)
    removed = 0
    for cache in cacheFolders:
        try:
            os.removedirs(cache)
            os.remove(cache)
            removed = removed + 1
        except Exception as e:
            print(e)
    print("{0}/{1} map's folders was removed.".format(removed, len(cacheFolders)))
