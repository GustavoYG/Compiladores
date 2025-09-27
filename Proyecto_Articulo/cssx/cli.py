import argparse
import sys
from .parser import parse
from .codegen.css_writer import generate_css
from .server.hot_reload import run_server

def main():
    parser = argparse.ArgumentParser("cssx")
    sub = parser.add_subparsers(dest="cmd")

    build = sub.add_parser("build")
    build.add_argument("input")
    build.add_argument("-o", "--output", default="style.css")

    serve = sub.add_parser("serve")
    serve.add_argument("input")

    args = parser.parse_args()

    if args.cmd == "build":
        with open(args.input, encoding="utf-8") as f:
            src = f.read()
        ast = parse(src)
        css = generate_css(ast)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(css)
        print(f"Compilado {args.input} -> {args.output}")
    elif args.cmd == "serve":
        # Compila primero
        with open(args.input, encoding="utf-8") as f:
            src = f.read()
        ast = parse(src)
        css = generate_css(ast)
        with open("style.css", "w", encoding="utf-8") as f:
            f.write(css)
        # Servidor
        run_server()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()