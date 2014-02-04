# really dumb example of using tree transformations w/asp

import abc
import asp.codegen.ast_tools as AstTools
from asp.jit.asp_module import ASPModule


class Converter(AstTools.ConvertAST):
    pass


class ArrayMap(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.pure_python = True

    @abc.abstractmethod
    def operation(self, a):
        """operation must define some operation on the array a"""
        return

    def map_using_trees(self, arr):
        operation_ast = AstTools.parse_method(self.operation)
        expr_ast = operation_ast.body[0].body[0].value
        converter = Converter()
        expr_cpp = converter.visit(expr_ast)

        import asp.codegen.templating.template as Template
        my_template = Template.Template(filename="templates/map_template.mako", disable_unicode=True)
        rendered = my_template.render(num_items=len(arr), expr=expr_cpp)

        mod = ASPModule()
        mod.add_function("map_in_c", rendered)
        return mod.map_in_c(arr)

    def map(self, arr):
        for i in range(0, len(arr)):
            arr[i] = self.operation(arr[i])
