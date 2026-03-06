"""
启动前端静态服务（前后端分离开发用）
默认端口 3000，可通过 --port 指定
"""
import argparse
import http.server
import socketserver
import os

def main():
    parser = argparse.ArgumentParser(description="启动前端静态服务")
    parser.add_argument("-p", "--port", type=int, default=3000, help="端口号")
    args = parser.parse_args()

    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
    os.chdir(frontend_dir)

    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", args.port), Handler) as httpd:
        print(f"前端服务: http://localhost:{args.port}/")
        print("按 Ctrl+C 停止")
        httpd.serve_forever()

if __name__ == "__main__":
    main()
