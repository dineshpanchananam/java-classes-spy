import sys
import os
import re
from table import Table
from collections import defaultdict
import operator as op

def small_case(x):
	return x[0].lower() + x[1:]

def capitalize(x):
	return x[0].upper() + x[1:]

def validate(fields, getters, setters):
	len_fields = len(fields)
	matched_getters = 0
	matched_setters = 0
	for field in fields:
		cap_field = capitalize(field)
		matched_getters += 1 if (cap_field in getters or field in getters) else 0
		matched_setters += 1 if (cap_field in setters or field in setters) else 0
	return len_fields == matched_getters and matched_getters == matched_setters

def compose(f, *g):
	def composition(x):
		for func in reversed(g):
			x = func(x)
		return f(x)
	return composition

print_tables = True

beans = []
count = 0
classnames = []

enums 					=	0
interfaces 			= 0
bean_count 			= 0 
no_const 				= 0
smpl_const 			= 0
pub_const 			=	0
private_const 	= 0
protected_const = 0
non_empty_const = 0
classes 				= 0

type_count = defaultdict(int)

invalid = []
valid = 0


def constructor_test(content, fname):
	global interfaces, enums, classes
	global no_const, smpl_const, pub_const
	global private_const, protected_const, non_empty_const
	# enums are not java beans
	its_an_enum 			= re.search("(private|public|)\s+?(.*)enum\s+{}".format(fname), content) != None
	its_an_interface	= re.search("(private|public|)\s*?(.*)interface\s+{}".format(fname), content) != None
	its_a_class 			= re.search("(private|public|)\s+?(.*)class\s+{}".format(fname), content) != None
	if its_an_enum:
		enums 			+= 1
	if its_an_interface:
		interfaces 	+= 1
	if its_a_class:
		classes 		+= 1

	if its_a_class:
		no_constructor 						= "\s+{}\s*\(".format(fname)
		simple_constructor 				= "[{}]\s*{}\s*\(\s*\)".format("{}", fname)
		public_constructor 				= "public\s+{}\(\s*\)".format(fname)
		private_constructor 			= "private\s+{}\(\s*\)".format(fname)
		protected_constructor 		= "protected\s+{}\(\s*\)".format(fname)
		non_empty_constructor 		= "\s+{}\s*\(\w+\)".format(fname)
		has_no_constructor 				= re.search(no_constructor, content) == None
		has_simple_constructor	 	= re.search(simple_constructor, content) != None
		has_public_constructor 		= re.search(public_constructor, content) != None
		has_private_constructor 	= re.search(private_constructor, content) != None
		has_protected_constructor = re.search(protected_constructor, content) != None
		has_non_empty_constructor = re.search(non_empty_constructor, content) != None
		# for analysis
		if has_simple_constructor: 
			smpl_const 			+= 1
		if has_no_constructor: 
			no_const 				+= 1
		if has_public_constructor: 
			pub_const 			+= 1
		if has_private_constructor:
			private_const 	+= 1
		if has_protected_constructor:
			protected_const += 1
		if has_non_empty_constructor:
			non_empty_const += 1
		return has_no_constructor or has_public_constructor
	return False

def get_fields(content):
	fields_regex = "(private|protected|public)\s+(\w+?)\s+(\w+);"
	fields = re.findall(fields_regex, content)
	for field in fields:
		type_count[field[1]] += 1
	field_accesses = (x[0] == "private" for x in fields)
	return all(field_accesses), fields

def qualify_getters_setters(content, classname, fields):
	global invalid, valid
	getter_regex = "public\s+(\w+?)\s+(get|is)(\w+?)\s*\(\s*\)\s*\{"
	setter_regex = "public\s+(\w+?)\s+(set)(\w+?)\s*\(\s*(\w+?)\s+(\w+?)\s*\)\s*\{"
	all_getters = re.finditer(getter_regex, content)
	all_setters = re.finditer(setter_regex, content)
	getters = [_.groups() for _ in all_getters]
	setters = [_.groups() for _ in all_setters]
	getters_set = set(map(op.itemgetter(2), getters))
	setters_set = set(map(op.itemgetter(2), setters))
	return validate(fields, getters_set, setters_set)


def is_a_bean(path):
	filename = path.split(os.sep)[-1][:-5]
	global bean_count
	global valid, invalid
	with open(path) as bean:
		content = bean.read()
		its_a_bean = constructor_test(content, filename)
		if its_a_bean:
			all_fields_private, fields = get_fields(content)
			if all_fields_private:
				field_names = map(op.itemgetter(2), fields)
				it_is_a_bean = qualify_getters_setters(content, filename, field_names)
				if it_is_a_bean:
					bean_count += 1
				return it_is_a_bean
		return False
	return False

def locate_beans(src):
	global count
	src_folder = os.listdir(src)
	for item in src_folder:
		abs_path = os.sep.join((src, item))
		if os.path.isfile(abs_path):
			if ".java" in item:
				count += 1
				if is_a_bean(abs_path):
					beans.append(abs_path)
		else:
			locate_beans(abs_path)

def main():
	with open("source.txt") as f:
		folder = f.read().strip() 

	locate_beans(folder)
	if print_tables:
		Table.print_table([
		["Constructor Type", 			"Count"],
		["No Constructor", 				`no_const`],
		["No access modifier", 		`smpl_const`],
		["Public Constructor", 		`pub_const`],
		["Private Constructor", 	`private_const`],
		["Protected Constructor", `protected_const`],
		["Non empty Constructor", `non_empty_const`]])

	if print_tables:
		Table.print_table([
		["Classes", 		"Count"],
		["Total", 			`count`],
		["Beans", 			`bean_count`],
		["Enums", 			`enums`],
		["Interfaces", 	`interfaces`],
		["Regular", 		`classes`]])
"""
(private|public|protected|)\s*(\w+)\s+(\w+)\s*\((\s*\w+\s+\w+?)*\)\s*\{
"""

if __name__ == "__main__":
	# You should have a source.txt
	# which contains absolute url of 
	# the java source folder
	main()
	assert interfaces + classes + enums == count
	print "Valid beans:", valid
	print  "\n".join(invalid)

print "Distinct Types found:", len(type_count)
top_types = sorted(type_count.items(), key=lambda x: -x[1])[:25]
if print_tables:
	Table.print_table([["Type", "Count"]] +  map(lambda x: map(str, x), top_types))
	
print "\n".join(beans)

#########################
#  # # #  ##    ###    ##
#    #   #  #   #  #  #  #
#    #    ##    ###    ##
# classes are 162, but sum of all constructor types != 162
# 
#
#
#
#
#