from stretch.lang.grammer import make_tree
from stretch.lang.builder import stretch_builder

def build(code:str, make_tree=make_tree, builder=stretch_builder):
    tree = make_tree(code)
    return builder.transform(tree)
       
if __name__ == "__main__":
    
    example_code = """
    1214905;2112;
    """
    
    print(build(example_code))