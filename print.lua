function print_any(object)
	local build = ""
	if type(object) == "table" then
		build = build .. "{"
		for k, v in pairs(object) do
			build = build .. "\"" .. k .. "\":" .. print_any(v) .. ","
		end
		build = build:sub(1, -2)
		build = build .. "}"
	else
		if object == nil then
			build = build .. '""'
		else
			build = '"' .. tostring(object) .. '"'
		end
	end
	return build
end

return print_any
