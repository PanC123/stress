#!/bin/sh
#
# 需要2个参数：文件大小，文件数量
# 1. 根据参数和模板，自动生成测试所需的JMX文件（上传/下载/混合），其中的线程数量等于文件数量
# 2. 生成指定数量和大小的文件，并且这些文件的文件名和checksum唯一

export LANG=en_US.utf-8
err() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $@" >&2
}
if [[ ! -n "$1" ]] ;then
    err "You have not input file size"; exit 1
elif [[ ! -n "$2" ]] ;then
    err "You have not input file count"; exit 1
fi


filesize=`echo $1 | tr -d 'a-zA-Z'`
filecount=$2

# 创建对应大小文件夹
fileStr=`echo "${filesize}m-${filecount}"`
mkdir -p test_data/$fileStr
rm -rf test_data/$fileStr/*

#默认生成3种JMX
if [[ ! -f artifactory_temp.jmx ]];then
    err "Not found jmx template"; exit 1
fi
cp artifactory_temp.jmx test_data/$fileStr/artifactory_upload.jmx
cp artifactory_temp.jmx test_data/$fileStr/artifactory_download.jmx
cp artifactory_temp.jmx test_data/$fileStr/artifactory_mix.jmx

# 控制数据文件
sed -i 's/sed_file_size/'"${filesize}m"'/g' test_data/$fileStr/*.jmx
sed -i 's/sed_test_threads/'"${filecount}"'/g' test_data/$fileStr/*.jmx

# 控制上传下载行为
sed -i 's/sed_upload_loop/1/g'   test_data/$fileStr/artifactory_upload.jmx
sed -i 's/sed_download_loop/0/g' test_data/$fileStr/artifactory_upload.jmx
sed -i 's/sed_upload_loop/0/g'   test_data/$fileStr/artifactory_download.jmx
sed -i 's/sed_download_loop/1/g' test_data/$fileStr/artifactory_download.jmx
sed -i 's/sed_upload_loop/1/g'   test_data/$fileStr/artifactory_mix.jmx
sed -i 's/sed_download_loop/1/g' test_data/$fileStr/artifactory_mix.jmx

# 控制上传下载线程
sed -i 's/sed_upload_threads/'"${filecount}"'/g' test_data/$fileStr/artifactory_upload.jmx
sed -i 's/sed_download_threads/0/g' test_data/$fileStr/artifactory_upload.jmx
sed -i 's/sed_upload_threads/0/g' test_data/$fileStr/artifactory_download.jmx
sed -i 's/sed_download_threads/'"${filecount}"'/g' test_data/$fileStr/artifactory_download.jmx

# 控制混合测试线程，上传30%，下载70%
mix_upload=`  awk 'BEGIN { rounded = sprintf("%.0f", '"${filecount}"'*0.3); print rounded }'`
mix_download=`awk 'BEGIN { rounded = sprintf("%.0f", '"${filecount}"'*0.7); print rounded }'`
sed -i 's/sed_upload_threads/'"${mix_upload}"'/g'     test_data/$fileStr/artifactory_mix.jmx
sed -i 's/sed_download_threads/'"${mix_download}"'/g' test_data/$fileStr/artifactory_mix.jmx

# 生成测试数据
let count=${filesize}*1000 # 换算为MB
seq 1 $filecount | while read line;
do
    let counts=${count}+${line}
    # 添加随机数，避免在多Slave时出现重复文件名和数据
    rdnum=$RANDOM
    dd if=/dev/zero of=test_data/$fileStr/test-${line}-${rdnum}.data bs=1024 count=${counts}
    echo $RANDOM >> test_data/$fileStr/test-${line}-${rdnum}.data
    echo "${line}-${rdnum}" >>  test_data/"$fileStr"/file_list.txt
done