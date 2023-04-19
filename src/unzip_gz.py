import os
import gzip

def gzs_to_xmls(src_dir):
    print("Unzipping all GZ files...")

    result=[]
    # 遍历 src_dir 下的所有文件和子目录
    for root, dirs, files in os.walk(src_dir):
        # 遍历当前目录下的所有文件
        for filename in files:
            # 如果文件扩展名是 .gz，说明是 gzip 压缩文件
            if filename.endswith('.GZ') or filename.endswith('.gz'):
                # 构造源文件路径和目标文件路径
                gz_file = os.path.join(root, filename)
                #dst_file = os.path.join(dst_dir, os.path.relpath(gz_file, src_dir)[:-3]+'.html')
                # 创建目标文件的目录（如果不存在）
                #os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                # 解压缩文件并将结果保存到目标文件中
                print("Unzipping file: " + gz_file + " ...")

                with gzip.open(gz_file, 'rt', encoding='utf-8',errors='ignore') as file:
                    xml_content = file.read()
                    result.append(xml_content)
    
    return result

                
