#!/bin/sh
#
# Start Jmeter stress test and collect performance report.
export LANG=en_US.utf-8
JMETER_HOME=/opt/jmeter

err() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $@" >&2
}

jmx_file=$1
if [[ ! -f ${jmx_file} ]]; then
    err "Not found JMX file."
    exit "${jmx_file}"
fi

# Start Jmeter.
rm -f ./request.jtl
$JMETER_HOME/bin/jmeter -n -t  "${jmx_file}" -l ./request.jtl -e -o report -r

# Change report name.
# File name: test_data/10m-100/artifactory_upload.jmx
# Report name: 10m-100_upload_19-22-32
test_scene=`echo $jmx_file | awk -F '/' '{print $(NF-1)}'`
test_func=`echo $jmx_file | awk -F '/' '{print $NF}' | awk -F '_' '{print $2}' | awk -F. '{print $1}'`
time_stamp=`date "+%H-%M-%S"`
echo "Moving report to reports/${test_scene}_${test_func}_${time_stamp}"
mv report reports/${test_scene}_${test_func}_${time_stamp}
