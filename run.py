import sys
import os

def merge_files(file1, file2, output_file, frames):
    with open(file1, 'r') as f1, open(file2, 'r') as f2, open(output_file, 'w') as output:
        content1 = f1.read()
        content2 = f2.read()

        # 合并内容并写入到输出文件中
        output.write(content1)
        output.write(content2)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python run.py <file1> <file2> <output> <frames>")
        sys.exit(1)

    file1 = sys.argv[1]
    file2 = sys.argv[2]
    output_file = sys.argv[3]
    frames = sys.argv[4]

    merge_files(file1, file2, output_file, frames)
