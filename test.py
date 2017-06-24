from math import sqrt
from ftpdownload import FtpDownload

ftpdown = FtpDownload()
ftpdown.download("172.25.105.226", "UniversalTest/performance_ScenarioTest/", "20170605171800")

# for n in range(3):
#     # root = sqrt(n)
#     if n == -1:
#         print n
#         break
# else:
#     print "ssss"
#
# y = zip(range(10),range(5))
# print y
#
# for x1,x2 in y:
#     print x1,x2
# l  = tuple([1,1,1])

# print l
# print "hhhh"

# l = list('perl')
# l[1:2] = 'o'
# l.insert(3,3)
# y = l[:]
# print l
# l.sort(reverse=True)
# print l,y
# print sum([1,2])
#
# d1 = {'name':'zxw','address':'sz',}
#
# l = d1.keys()
# print [x for x in l if x == 'name']


# print [range(10)]
#
# for k,v in d1.iteritems():
#     print k,v
#
# print d1.values()
#
#
# for i,value in enumerate(l):
#     print i ,value
#
# s = ''' ss
# sssssd hah '''
# print s
#
# seq = ['1','2']
# sep = '+'
#
# print sep.join(seq)
#
# print "My name is %s and weight is %10.1f kg!" % ('Zara', 21.88)
# def method():
#     dirs = []
#     for (dirpath, dirnames, filenames) in walk("log/"):
#         dirs.extend(dirnames)
#         break
#     print dirs
#     D = {}
#     for dir in dirs:
#
#         f = []
#         for (dirpath, dirnames, filenames) in walk("log/" + dir):
#             f.extend(filenames)
#             break
#         print f
#         pkgs = []
#         cases = []
#         for k in f:
#             readfile = open("log/" + dir + "/" + k)
#             while True:
#                 line = readfile.readline()
#                 if line.find("bugreport") != -1:
#                     # print line
#                     length = len(line)
#                     pkg = line[length - 9:length - 7]
#                     case = line[length - 9:length - 5]
#                     if len(pkg) != 0 or len(case) != 0:
#                         pkgs.append(pkg)
#                         cases.append(case)
#                     print pkg, case
#                 if not line: break
#
#             readfile.close()
#
#         dpkgs = dict(Counter(pkgs))
#         dcases = dict(Counter(cases))
#         print dpkgs
#         print dcases
#         D[dir] = [dpkgs, dcases]
#         print dir, D[dir]
#     print D
#
#     size = len(dirs)
#
#     d1 = D.get("PD1610")
#     d2 = D.get("PD1619")
#
#     print d1[0],d1[1]
#     keys1 = []
#     for key in d1[0].keys:
#          if(d2[0].get(key) != None):
#              keys1.append(key)
#
#     print keys1
# keys2 = []
#
# for key in d2[1].keys:
#     if(d2[1].get(key) != None):
#         keys2.append(key)

# print keys2


# method()