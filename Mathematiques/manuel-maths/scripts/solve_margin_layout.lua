local function fail(message)
  error("margin-layout-cli: " .. message, 0)
end

local function script_directory()
  local path = arg[0] or ""
  local directory = path:match("^(.*)/[^/]+$")
  if directory and directory ~= "" then
    return directory
  end
  return "."
end

local function load_module(path, label)
  local chunk, load_error = loadfile(path)
  if not chunk then
    fail("cannot load " .. label .. ": " .. tostring(load_error))
  end
  local ok, module = pcall(chunk)
  if not ok then
    fail("cannot initialize " .. label .. ": " .. tostring(module))
  end
  return module
end

local function parse_options(arguments)
  local options = {}
  local index = 1
  while index <= #arguments do
    local option = arguments[index]
    if option ~= "--solve" and option ~= "--output" and option ~= "--previous" then
      fail("unknown option " .. tostring(option))
    end
    if options[option] then
      fail("duplicate option " .. option)
    end
    local value = arguments[index + 1]
    if not value or value:sub(1, 2) == "--" then
      fail("missing value for " .. option)
    end
    options[option] = value
    index = index + 2
  end
  if not options["--solve"] then
    fail("missing required option --solve")
  end
  if not options["--output"] then
    fail("missing required option --output")
  end
  return options
end

local function normalized_absolute(path)
  local lfs = require("lfs")
  local absolute = path:sub(1, 1) == "/" and path or (lfs.currentdir() .. "/" .. path)
  local parts = {}
  for part in absolute:gmatch("[^/]+") do
    if part == ".." then
      if #parts > 0 then
        parts[#parts] = nil
      end
    elseif part ~= "." and part ~= "" then
      parts[#parts + 1] = part
    end
  end
  return "/" .. table.concat(parts, "/")
end

local function paths_alias(first, second)
  if normalized_absolute(first) == normalized_absolute(second) then
    return true
  end
  local lfs = require("lfs")
  local first_attributes = lfs.attributes(first)
  local second_attributes = lfs.attributes(second)
  return first_attributes ~= nil
    and second_attributes ~= nil
    and first_attributes.dev ~= nil
    and first_attributes.ino ~= nil
    and first_attributes.dev == second_attributes.dev
    and first_attributes.ino == second_attributes.ino
end

local function read_file(path)
  local handle, open_error = io.open(path, "rb")
  if not handle then
    fail("cannot read " .. path .. ": " .. tostring(open_error))
  end
  local content = handle:read("*a")
  local ok, close_error = handle:close()
  if not ok then
    fail("cannot close " .. path .. ": " .. tostring(close_error))
  end
  return content
end

local function write_file(path, content)
  local handle, open_error = io.open(path, "wb")
  if not handle then
    fail("cannot write " .. path .. ": " .. tostring(open_error))
  end
  local ok, write_error = handle:write(content)
  if not ok then
    handle:close()
    fail("cannot write " .. path .. ": " .. tostring(write_error))
  end
  local close_ok, close_error = handle:close()
  if not close_ok then
    fail("cannot close " .. path .. ": " .. tostring(close_error))
  end
end

local function main()
  local options = parse_options(arg)
  local input_path = options["--solve"]
  local output_path = options["--output"]
  local previous_path = options["--previous"]
  if paths_alias(output_path, input_path)
      or (previous_path and paths_alias(output_path, previous_path)) then
    fail("output must differ from every input")
  end

  local root = script_directory() .. "/.."
  local json = load_module(root .. "/gabarits/nexus-margin-json.lua", "JSON codec")
  local layout = load_module(root .. "/gabarits/nexus-margin-layout.lua", "layout solver")
  local current = json.decode(read_file(input_path))
  local previous = previous_path and json.decode(read_file(previous_path)) or nil
  local solved = layout.solve(current, previous)
  local encoded = json.encode(solved)
  write_file(output_path, encoded)
end

local ok, message = pcall(main)
if not ok then
  local rendered = tostring(message)
  if not rendered:match("^margin%-layout%-cli:") then
    rendered = "margin-layout-cli: " .. rendered
  end
  io.stderr:write(rendered, "\n")
  os.exit(1)
end
