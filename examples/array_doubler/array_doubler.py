# really dumb example of using templates w/asp


class ArrayDoubler(object):
    
    def __init__(self):
        self.pure_python = True

    def double_using_template(self, arr):
        from asp.codegen.templating.template import Template
        my_template = Template(filename="templates/double_template.mako", disable_unicode=True)
        rendered = my_template.render(num_items=len(arr))

        from asp.jit.asp_module import ASPModule
        mod = ASPModule()
        # remember, must specify function name when using a string
        mod.add_function("double_in_c", rendered)
        return mod.double_in_c(arr)

    def double(self, arr):
        return map(lambda x: x*2, arr)
