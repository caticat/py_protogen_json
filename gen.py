# -*- coding: utf-8 -*-

import argparse
import json
import os
from pprint import pprint
from proto import test_pb2

if __name__ == "__main__":
	# 初始化
	pb = test_pb2

	# 参数解析
	argParse = argparse.ArgumentParser()
	argParse.add_argument("-json", type=str, default="in.json")
	argParse.add_argument("-out", type=str, default="out")
	argParse.add_argument("-proto", type=str, default="proto")
	argParse.add_argument("-index", type=str, default="index.txt")
	argParse.add_argument("-v", action="store_true")
	argParse.add_argument("-check", action="store_true")
	args = argParse.parse_args()

	# 解析json文件
	with open(args.json, "r", encoding="utf-8") as f:
		data = json.load(f)
		del data[0]

	# 组织数据(和proto文件相比较)
	g = []
	for index, d in enumerate(data):
		# 校验
		if "proto" not in d:
			raise Exception("没有协议,数组索引[%s]" % d)
		if not hasattr(pb, d["proto"]):
			raise Exception("没有协议[%s]" % d["proto"])
		ptl = getattr(pb, d["proto"])
		if "msg" not in d:
			prifix = "MSG_"
			i = d["proto"].find(prifix)
			if i >= 0:
				d["msg"] = d["proto"][len(prifix):]
			else:
				d["msg"] = d["proto"]
		t = d["msg"]
		if not hasattr(pb, t):
			raise Exception("没有类型[%s]" % t)

		# 写数据
		msg = getattr(pb, t)()
		for a, b in d["data"].items():
			if isinstance(b, (list, tuple)):
				setattr(msg, a, [dict(x) if isinstance(x, dict) else x for x in b])
			else:
				setattr(msg, a, dict(b) if isinstance(b, dict) else b)
		g.append({ptl:msg.SerializeToString()})

		# 日志
		if (args.v):
			print("处理编号[%s]完成" % index)

	# 创建输出目录
	if not os.path.exists(args.out):
		os.mkdir(args.out)

	# 清空上次的数据
	for root, dirs, files in os.walk(args.out, False):
		for name in files:
			os.remove(os.path.join(root, name))
		for name in dirs:
			os.rmdir(os.path.join(root, name))

	# 输出
	# 数据
	arr = []
	for idx, d in enumerate(g):
		for ptl, binary in d.items():
			name = "%03d_%d.ptl" % (idx, ptl)
			path = os.path.join(args.out, name)
			arr.append(name+"\n")
			with open(path, "bw") as f:
				f.write(binary)
	# 索引
	if len(arr) > 0:
		arr[len(arr) - 1] = arr[len(arr) - 1][:-1]
	with open(os.path.join(args.out, args.index), "w") as f:
		f.writelines(arr)

	# 检测是否转化成功
	if args.check:
		print("检测转换文件")
		for root, _, files in os.walk(args.out, False):
			for name in files:
				head = os.path.splitext(name)[0].split("_")
				print("序号[%s]协议[%s]" % (head[0], head[1]))
				with open(os.path.join(root, name), "rb") as f:
					print(data[int(head[0])]["msg"])
					msg = getattr(pb, data[int(head[0])]["msg"])()
					msg.ParseFromString(f.read())
					pprint(msg)
					print("_________________")

	print("转换完成")
	input("按回车退出")

