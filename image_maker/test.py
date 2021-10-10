from joblib import Parallel, delayed


def carre(i):
  print (i[1]**2)
Parallel(n_jobs=1)(delayed(carre)((i,2)) for i in  range(10))