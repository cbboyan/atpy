import os
from . import enigmap, pretrains, trains, liblinear

ENIGMA_ROOT = os.getenv("ENIGMA_ROOT", "./Enigma")

def path(name, filename=None):
   if filename:
      return os.path.join(ENIGMA_ROOT, name, filename)
   else:
      return os.path.join(ENIGMA_ROOT, name)

def collect(name, rkeys):
   f_pre = path(name, "train.pre")
   pretrains.prepare(rkeys)
   pretrains.make(rkeys, out=file(f_pre, "w"))

def setup(name, rkeys):
   os.system("mkdir -p %s" % path(name))
   if rkeys:
      collect(name, rkeys)

   f_pre = path(name, "train.pre")
   f_map = path(name, "enigma.map")
   f_log = path(name, "train.log")
   if os.path.isfile(f_log):
      os.system("rm -f %s" % f_log)

   emap = enigmap.create(file(f_pre))
   enigmap.save(emap, f_map)
   return emap

def standard(name, rkeys=None):
   f_pre = path(name, "train.pre")
   f_in  = path(name, "train.in")
   f_mod = path(name, "model.lin")
   f_out = path(name, "train.out")
   f_log = path(name, "train.log")

   emap = setup(name, rkeys)
   trains.make(file(f_pre), emap, out=file(f_in, "w"))
   liblinear.train(f_in, f_mod, f_out, f_log)

def smartboost(name, rkeys=None):
   it = 0
   f_pre = path(name, "train.pre")
   f_log = path(name, "train.log")
   f_in  = path(name, "%02dtrain.in" % it)
   
   emap = setup(name, rkeys)
   trains.make(file(f_pre), emap, out=file(f_in, "w"))

   log = file(f_log, "a")
   while True:
      log.write("\n--- ITER %d ---\n\n" % it)
      f_in  = path(name, "%02dtrain.in" % it)
      f_in2 = path(name, "%02dtrain.in" % (it+1))
      f_out = path(name, "%02dtrain.out" % it)
      f_mod = path(name, "%02dmodel.lin" % it)
      log.flush()
      liblinear.train(f_in, f_mod, f_out, f_log)
      stat = liblinear.stats(f_in, f_out)
      log.write("\n".join(["%s = %s"%(x,stat[x]) for x in sorted(stat)]))
      log.write("\n")
      if stat["ACC:POS"] >= stat["ACC:NEG"]:
      #if stat["WRONG:POS"] == 0:
         os.system("cp %s %s" % (f_mod, path(name, "model.lin")))
         break
      trains.boost(f_in, f_out, out=file(f_in2,"w"), method="WRONG:POS")
      it += 1
   log.close()

def join(name, models):
   pass

