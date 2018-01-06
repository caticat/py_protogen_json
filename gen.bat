@echo off

::@param json 输入文件
::@param out 生成输出文件目录
::@param proto protobuf文件目录
::@param v 是否显示过程输出
::@param check 是否做反转文件校验

python.exe gen.py -json=in.json -out=out -proto=proto -v
