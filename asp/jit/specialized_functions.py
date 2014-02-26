import scala_module
import codepy
import asp.codegen.cpp_ast as cpp_ast

class SpecializedFunction(object):
    """
    Class that encapsulates a function that is specialized.  It keeps track of variants,
    their timing information, which backend, functions to determine if a variant
    can run, as well as a function to generate keys from parameters.

    The signature for any run_check function is run(*args, **kwargs).
    The signature for the key function is key(self, *args, **kwargs), where the args/kwargs are
    what are passed to the specialized function.

    """

    def __init__(self, name, backend, db, variant_names=[], variant_funcs=[], run_check_funcs=[],
                 key_function=None, call_policy=None):
        self.name = name
        self.backend = backend
        self.db = db
        self.variant_names = []
        self.variant_funcs = []
        self.run_check_funcs = []
        self.call_policy = call_policy

        if variant_names != [] and run_check_funcs == []:
            run_check_funcs = [lambda *args,**kwargs: True]*len(variant_names)

        for x in xrange(len(variant_names)):
            self.add_variant(variant_names[x], variant_funcs[x], run_check_funcs[x])

        if key_function:
            self.key = key_function

    def key(self, *args, **kwargs):
        """
        Function to generate keys.  This should almost always be overridden by a specializer, to make
        sure the information stored in the key is actually useful.
        """
        import hashlib
        return hashlib.md5(str(args)+str(kwargs)).hexdigest()


    def add_variant(self, variant_name, variant_func, run_check_func=lambda *args,**kwargs: True):
        """
        Add a variant of this function.  Must have same call signature.  Variant names must be unique.
        The variant_func parameter should be a CodePy Function object or a string defining the function.
        The run_check_func parameter should be a lambda function with signature run(*args,**kwargs).
        """
        if variant_name in self.variant_names:
            raise Exception("Attempting to add a variant with an already existing name %s to %s" %
                            (variant_name, self.name))
        self.variant_names.append(variant_name)
        self.variant_funcs.append(variant_func)
        self.run_check_funcs.append(run_check_func)

        # TODO: Move all this logic to backends, and do it with one function
        # call.
        if isinstance(self.backend.module, scala_module.ScalaModule):
            self.backend.module.add_to_module(variant_func)
            self.backend.module.add_to_init(variant_name)
        elif isinstance(variant_func, basestring):
            self.backend.add_variant_func(variant_func, variant_name,
                                          self.call_policy)
        else:
            self.backend.module.add_function(variant_func)

        self.backend.dirty = True

    def pick_next_variant(self, *args, **kwargs):
        """
        Logic to pick the next variant to run.  If all variants have been run, then this should return the
        fastest variant.
        """
        # get variants that have run
        already_run = self.db.get(self.name, key=self.key(*args, **kwargs))


        if already_run == []:
            already_run_variant_names = []
        else:
            already_run_variant_names = map(lambda x: x[1], already_run)

        # which variants haven't yet run
        candidates = set(self.variant_names) - set(already_run_variant_names)

        # of these candidates, which variants *can* run
        for x in candidates:
            if self.run_check_funcs[self.variant_names.index(x)](*args, **kwargs):
                return x

        # if none left, pick fastest from those that have already run
        return sorted(already_run, lambda x,y: cmp(x[3],y[3]))[0][1]

    def __call__(self, *args, **kwargs):
        """
        Calling an instance of SpecializedFunction will actually call either the next variant to test,
        or the already-determined best variant.
        """
        if self.backend.dirty:
            self.backend.compile()

        which = self.pick_next_variant(*args, **kwargs)

        import time
        start = time.time()
        ret_val = self.backend.get_compiled_function(which).__call__(*args, **kwargs)
        elapsed = time.time() - start
        #FIXME: where should key function live?
        #print "doing update with %s, %s, %s, %s" % (self.name, which, self.key(args, kwargs), elapsed)
        self.db.update(self.name, which, self.key(*args, **kwargs), elapsed)
        #TODO: Should we use db.update instead of db.insert to avoid O(N) ops on already_run_variant_names = map(lambda x: x[1], already_run)?

        return ret_val

class HelperFunction(SpecializedFunction):
    """
    HelperFunction defines a SpecializedFunction that is not timed, and usually not called directly
    (although it can be).
    """
    def __init__(self, name, func, backend):
        self.name = name
        self.backend = backend
        self.variant_names, self.variant_funcs, self.run_check_funcs = [], [], []
        self.call_policy = None
        self.add_variant(name, func)


    def __call__(self, *args, **kwargs):
        if self.backend.dirty:
            self.backend.compile()
        return self.backend.get_compiled_function(self.name).__call__(*args, **kwargs)
