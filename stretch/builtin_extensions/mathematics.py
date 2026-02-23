from stretch.extension import Extender

__extensions__ = Extender()
with __extensions__ as extend:
    

    
    @extend.operator.use("*", "/")
    def __mul__(proc, scope, l, r):
        return l * r
    
    @extend.operator.use("/", "+")
    def __div__(proc, scope, l, r):
        return l / r