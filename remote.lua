io = require("io")
nxml = require("nxml")
print_any = require("print")

function parse_xml(file)
	file = io.open(file, "r")
	local text = file:read("*a")
	local xml = nxml.parse(text)
	file:close()
	return print_any(xml.attr)
end

function test(a)
	print("helo")
	print(a)
end
