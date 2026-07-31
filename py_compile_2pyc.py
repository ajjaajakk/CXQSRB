import os
import py_compile

def compile_py_files(source_dir, target_dir):
    # 确保目标目录存在
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    # 遍历源目录中的所有文件
    for subdir, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.py'):
                # 构建完整的文件路径
                src_file = os.path.join(subdir, file)
                # 由于我们想要将所有.pyc文件放在一个目录下，我们不需要relpath
                dst_file = os.path.join(target_dir, os.path.splitext(file)[0] + '.pyc')
                
                # 编译 .py 文件并保存 .pyc 文件
                try:
                    py_compile.compile(src_file, cfile=dst_file)
                    print(f"Compiled {src_file} to {dst_file}")
                except py_compile.PyCompileError as e:
                    print(f"Failed to compile {src_file}: {e}")

# 设置源目录和目标目录
# 使用'.'表示当前目录
source_directory = '.'  # 当前目录
target_directory = 'pyc'  # 目标目录，用于存放 .pyc 文件

# 调用函数
compile_py_files(source_directory, target_directory)