import sys
import os
import re
from table import Table

beans = []
count = 0

enums = 0
bean_count = 0 
no_const = 0
smpl_const = 0
pub_const = 0

def check_empty_constructor(content, fname):
	global no_const, smpl_const, pub_const, enums
	# enums are not java beans
	if re.search("public\s+enum", content):
		enums += 1
	no_constructor = "\s+{}\s*\(".format(fname)
	simple_constructor = "[{}]\s*{}\s*\(\s*\)".format("{}", fname)
	public_constructor = "public\s+{}\(\s*\)".format(fname)
	has_no_constructor = re.search(no_constructor, content) == None
	has_simple_constructor = re.search(simple_constructor, content) != None
	has_public_constructor = re.search(public_constructor, content) != None
	# for analysis
	if has_simple_constructor: 
		smpl_const += 1
	if has_no_constructor: 
		no_const += 1
	if has_public_constructor: 
		pub_const += 1
	return has_simple_constructor or has_no_constructor or has_public_constructor


def get_fields(content):
	pass

def get_methods(content):
	pass

def is_bean(path):
	filename = path.split(os.sep)[-1][:-5]
	global bean_count
	with open(path) as bean:
		content = bean.read()
		its_a_bean = check_empty_constructor(content, filename)
		if its_a_bean:
			bean_count += 1
			fields = get_fields(content)
			methods = get_methods(content)
			# all fields should private
			# all getter, setter should methods be private
		return its_a_bean
	return False

def locate_beans(src):
	global count
	src_folder = os.listdir(src)
	for item in src_folder:
		abs_path = os.sep.join((src, item))
		if os.path.isfile(abs_path):
			if ".java" in item:
				count += 1
				if is_bean(abs_path):
					beans.append(abs_path)
		else:
			locate_beans(abs_path)

def main():
	with open("source.txt") as f:
		folder = f.read().strip() 

	locate_beans(folder)
	Table.print_table([
		["Constructor Type", "Count"],
		["No Access modifier", `smpl_const`],
		["Public Constructor", `pub_const`],
		["No Constructor", `no_const`]])

	Table.print_table([
		["Classes", "Count"],
		["Total", `count`],
		["Beans", `bean_count`],
		["Enums", `enums`],
		["Regular", `count - enums`]])

if __name__ == "__main__":
	# You should have a source.txt
	# which contains absolute url of 
	# the java sources
	main()