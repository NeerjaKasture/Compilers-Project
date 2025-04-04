from parser import parse
from errors import handle_error

def compile_file(filename):
    """Compile a YAP source file"""
    try:
        with open(filename, 'r') as f:
            source = f.read()
        
        # Parse the source code
        ast = parse(source)
        if ast is None:
            # Parse returned None, which means an error occurred
            return False
            
        # Continue with other compilation phases...
        return True
        
    except Exception as e:
        handle_error(e)
        return False

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python main.py <filename.yap>")
        return
    
    filename = sys.argv[1]
    success = compile_file(filename)
    
    if success:
        print("Compilation successful!")

if __name__ == "__main__":
    main()
