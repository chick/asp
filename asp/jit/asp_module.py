import codepy, codepy.jit, codepy.toolchain, codepy.bpl, codepy.cuda
import abc
from asp.util import *
import asp.codegen.cpp_ast as cpp_ast
import pickle
from variant_history import *
import sqlite3
import asp
import asp.platform.capability as capability
from asp.platform.ASPBackend import ASPBackend
from asp.platform.cuda_backend import CudaBackend
import scala_module
from specialized_functions import *
import asp.util


class ASPDB(object):
    """
    Manages an sqlite database to keep track of cache of compiled specializers
    """
    def __init__(self, specializer, persistent=False):
        """
        specializer must be specified so we avoid namespace collisions.
        """
        self.specializer = specializer

        if persistent:
            # create db file or load db
            # create a per-user cache directory
            import tempfile
            import os
            if os.name == 'nt':
                username = os.environ['USERNAME']
            else:
                username = os.environ['LOGNAME']

            self.cache_dir = tempfile.gettempdir() + "/asp_cache_" + username

            if not os.access(self.cache_dir, os.F_OK):
                os.mkdir(self.cache_dir)
            self.db_file = self.cache_dir + "/aspdb.sqlite3"
            self.connection = sqlite3.connect(self.db_file)
            self.connection.execute("PRAGMA temp_store = MEMORY;")
            self.connection.execute("PRAGMA synchronous = OFF;")

        else:
            self.db_file = None
            self.connection = sqlite3.connect(":memory:")

    def create_specializer_table(self):
        self.connection.execute('create table '+self.specializer+' (fname text, variant text, key text, perf real)')
        self.connection.commit()

    def close(self):
        self.connection.close()

    def table_exists(self):
        """
        Test if a table corresponding to this specializer exists.
        """
        cursor = self.connection.cursor()
        cursor.execute('select name from sqlite_master where name="%s"' % self.specializer)
        result = cursor.fetchall()
        return len(result) > 0

    def insert(self, fname, variant, key, value):
        if not self.table_exists():
                self.create_specializer_table()
        self.connection.execute('insert into '+self.specializer+' values (?,?,?,?)',
                (fname, variant, key, value))
        self.connection.commit()

    def get(self, fname, variant=None, key=None):
        """
        Return a list of entries.  If key and variant not specified, all entries from
        fname are returned.
        """
        if (not self.table_exists()):
            self.create_specializer_table()
            return []

        cursor = self.connection.cursor()
        query = "select * from %s where fname=?" % (self.specializer,)
        params = (fname,)

        if variant:
            query += " and variant=?"
            params += (variant,)

        if key:
            query += " and key=?"
            params += (key,)

        cursor.execute(query, params)

        return cursor.fetchall()

    def update(self, fname, variant, key, value):
        """
        Updates an entry in the db.  Overwrites the timing information with value.
        If the entry does not exist, does an insert.
        """
        if not self.table_exists():
            self.create_specializer_table()
            self.insert(fname, variant, key, value)
            return

        # check if the entry exists
        query = "select count(*) from "+self.specializer+" where fname=? and variant=? and key=?;"
        cursor = self.connection.cursor()
        cursor.execute(query, (fname, variant, key))
        count = cursor.fetchone()[0]

        # if it exists, do an update, otherwise do an insert
        if count > 0:
            query = "update "+self.specializer+" set perf=? where fname=? and variant=? and key=?"
            self.connection.execute(query, (value, fname, variant, key))
            self.connection.commit()
        else:
            self.insert(fname, variant, key, value)


    def delete(self, fname, variant, key):
        """
        Deletes an entry from the db.
        """
        if (not self.table_exists()):
            return

        query = "delete from "+self.specializer+" where fname=? and variant=? and key=?"
        self.connection.execute(query, (fname, variant, key))
        self.connection.commit()

    def destroy_db(self):
        """
        Delete the database.
        """
        if not self.db_file:
            return True

        import os
        try:
            self.close()
            os.remove(self.db_file)
        except:
            return False
        else:
            return True

class ASPModule(object):
    """Manage a single specializer
    keyword arguments such as use_<x> can be used to override information in
    a .asp_config.yml file in the root directory of the user or specializer

    ASPModule is the main coordination class for examples.  A specializer creates an ASPModule to contain
    all of its specialized functions, and adds functions/libraries/etc to the ASPModule.

    ASPModule uses ASPBackend instances for each backend, ASPDB for its backing db for recording timing info,
    and instances of SpecializedFunction and HelperFunction for specialized and helper functions, respectively.
    """

    legal_flags = ['use_cuda','use_cilk','use_mpp','use_openmp','use_opencl','use_tbb','use_pthreads','use_scala']

    #FIXME: specializer should be required.
    def __init__(self, specializer="default_specializer", cache_dir=None, use_cuda=False, use_cilk=False, use_tbb=False, use_pthreads=False, use_scala=False, use_openmp=False, use_opencl=False):

        self.specialized_functions= {}
        self.helper_method_names = []

        self.db = ASPDB(specializer)

        self.use_cuda = use_cuda
        self.use_opencl = use_opencl

        self.cache_dir = get_cache_dir(cache_dir)

        self.backends = {}
        self.backends["c++"] = ASPBackend(codepy.bpl.BoostPythonModule(),
                                          codepy.toolchain.guess_toolchain(),
                                          self.cache_dir)
        if use_cuda:
            self.backends['cuda'] = CudaBackend(self.backends['c++'],
                self.cache_dir, use_runtime=True, cflags=["-shared"])
        if use_cilk:
            self.backends["cilk"] = self.backends["c++"]
            self.backends["cilk"].toolchain.cc = "icc"
        if use_tbb:
            # Intel Thread Building Blocks
            self.backends["tbb"] = self.backends["c++"]
            self.backends["tbb"].add_cflags("-ltbb")
        if use_pthreads:
            self.backends["pthreads"] = self.backends["c++"]
            self.backends["pthreads"].add_cflags("-pthread")
        if use_openmp:
            self.backends["openmp"] = self.backends["c++"]
            # TODO make this compiler dependent, this should work, but some compilers
            # use other flags see: http://openmp.org/wp/openmp-compilers/
            self.backends["openmp"].add_cflags("-fopenmp")
        if use_opencl:
            self.backends["opencl"] = self.backends["c++"]
        if use_scala:
            self.backends["scala"] = ASPBackend(scala_module.ScalaModule(),
                                                scala_module.ScalaToolchain(),
                                                self.cache_dir)

    def add_library(self, feature, include_dirs, library_dirs=[], libraries=[], backend="c++"):
        self.backends[backend].toolchain.add_library(feature, include_dirs, library_dirs, libraries)

    def add_cuda_arch_spec(self, arch):
        archflag = '-arch='
        if 'sm_' not in arch: archflag += 'sm_'
        archflag += arch
        self.backends["cuda"].add_cflags(archflag)

    def add_header(self, include_file, brackets=False, backend="c++"):
        """
        Add a header (e.g. #include "foo.h") to the module source file.
        With brackets=True, it will be C++-style #include <foo> instead.
        """
        self.backends[backend].module.add_to_preamble([cpp_ast.Include(include_file, brackets)])

    def add_to_preamble(self, pa, backend="c++"):
        if isinstance(pa, basestring):
            pa = [cpp_ast.Line(pa)]
        self.backends[backend].module.add_to_preamble(pa)

    def add_to_init(self, stmt, backend="c++"):
        if isinstance(stmt, str):
            stmt = [cpp_ast.Line(stmt)]
        if backend == "cuda":
            self.backends[backend].module.boost_module.add_to_init(stmt) #HACK because codepy's CudaModule doesn't have add_to_init()
        else:
            self.backends[backend].module.add_to_init(stmt)

    def add_to_module(self, block, backend="c++"):
        if isinstance(block, basestring):
            block = [cpp_ast.Line(block)]
        self.backends[backend].module.add_to_module(block)

    def add_function(self, fname, funcs, variant_names=[], run_check_funcs=[], key_function=None,
                     backend="c++", call_policy=None):
        """
        Add a specialized function to the Asp module.  funcs can be a list of variants, but then
        variant_names is required (also a list).  Each item in funcs should be a string function or
        a cpp_ast FunctionDef.
        """
        if not isinstance(funcs, list):
            funcs = [funcs]
            variant_names = [fname]

        self.specialized_functions[fname] = SpecializedFunction(fname, self.backends[backend], self.db, variant_names,
                                                                variant_funcs=funcs,
                                                                run_check_funcs=run_check_funcs,
                                                                key_function=key_function,
                                                                call_policy=call_policy)

    def add_helper_function(self, fname, func, backend="c++"):
        """
        Add a helper function, which is a specialized function that it not timed and has a single variant.
        """
        self.specialized_functions[fname] = HelperFunction(fname, func, self.backends[backend])


    def expose_class(self, classname, backend="c++"):
        """
        Expose a class or struct from C++ to Python, letting us pass instances back and forth
        between Python and C++.

        TODO: allow exposing *functions* within the class
        """
        self.backends[backend].module.add_to_init([cpp_ast.Line("boost::python::class_<%s>(\"%s\");\n" % (classname, classname))])


    def __getattr__(self, name):
        if name in self.specialized_functions:
            return self.specialized_functions[name]
        else:
            raise AttributeError("No method %s found; did you add it to this ASPModule?" % name)

    def generate(self):
        """
        Utility function for, during development, dumping out the generated
        source from all the underlying backends.
        """
        src = ""
        for x in self.backends.keys():
            src += "\nSource code for backend '" + x + "':\n"
            src += str(self.backends[x].module.generate())

        return src

    def validate(self):
        result = True
        if self.use_cuda and not capability.Cuda.has_cuda():
            print "CudaBackend required, not available"
            result = False
        elif self.use_opencl and not capability.AspOpenCl.has_cuda():
            print "OpenClBackend required, not available"
            result = False

        return result


