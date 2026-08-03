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

local function split_path(path)
  local parent, basename = path:match("^(.*)/([^/]*)$")
  if not parent then
    return ".", path
  end
  if parent == "" then
    parent = "/"
  end
  return parent, basename
end

local function output_snapshot(path)
  local lfs = require("lfs")
  local attributes = lfs.symlinkattributes(path)
  if not attributes then
    return { exists = false }
  end
  if attributes.mode == "link" then
    fail("output must not be a symbolic link: " .. path)
  end
  if attributes.mode ~= "file" then
    fail("output must be a regular file: " .. path)
  end
  if attributes.dev == nil or attributes.ino == nil then
    fail("cannot identify output file: " .. path)
  end
  return {
    exists = true,
    dev = attributes.dev,
    ino = attributes.ino,
  }
end


local function validate_output_parent(path)
  local lfs = require("lfs")
  local parent, basename = split_path(path)
  if basename == "" or basename == "." or basename == ".." then
    fail("output path must name a regular file")
  end
  local attributes = lfs.attributes(parent)
  if not attributes or attributes.mode ~= "directory" then
    fail("output parent must be an existing directory: " .. parent)
  end
  return parent, basename
end

local function acquire_output_lock(parent, basename)
  local lfs = require("lfs")
  local path = parent .. "/." .. basename .. ".nexus-margin-lock"
  local previous_attributes = lfs.symlinkattributes(path)
  if previous_attributes and previous_attributes.mode ~= "file" then
    fail("output publication lock must be a regular file: " .. path)
  end
  local handle, open_error = io.open(path, "a+b")
  if not handle then
    fail("cannot open output publication lock: " .. tostring(open_error))
  end
  local attributes = lfs.symlinkattributes(path)
  if not attributes or attributes.mode ~= "file"
      or attributes.dev == nil or attributes.ino == nil then
    handle:close()
    fail("cannot identify output publication lock: " .. path)
  end
  if previous_attributes
      and (attributes.dev ~= previous_attributes.dev
        or attributes.ino ~= previous_attributes.ino) then
    handle:close()
    fail("output publication lock changed while opening: " .. path)
  end
  local locked, lock_error = lfs.lock(handle, "w", 0, 0)
  if not locked then
    handle:close()
    fail("output publication is locked: " .. path .. ": " .. tostring(lock_error))
  end
  return {
    path = path,
    dev = attributes.dev,
    ino = attributes.ino,
    handle = handle,
  }
end

local function require_owned_output_lock(lock)
  local lfs = require("lfs")
  local attributes = lfs.symlinkattributes(lock.path)
  if not lock.handle or not attributes or attributes.mode ~= "file"
      or attributes.dev ~= lock.dev or attributes.ino ~= lock.ino then
    fail("output publication lock changed: " .. lock.path)
  end
end

local function release_output_lock(lock)
  local lfs = require("lfs")
  local ownership_ok, ownership_error = pcall(require_owned_output_lock, lock)
  local unlocked, unlock_error = lfs.unlock(lock.handle, 0, 0)
  local closed, close_error = lock.handle:close()
  lock.handle = nil
  if not ownership_ok then
    error(ownership_error, 0)
  end
  if not unlocked then
    fail("cannot unlock output publication lock: " .. tostring(unlock_error))
  end
  if not closed then
    fail("cannot close output publication lock: " .. tostring(close_error))
  end
end


local function output_is_unchanged(path, expected)
  local current = output_snapshot(path)
  if current.exists ~= expected.exists then
    fail("output changed before publication: " .. path)
  end
  if current.exists
      and (current.dev ~= expected.dev or current.ino ~= expected.ino) then
    fail("output changed before publication: " .. path)
  end
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

local function publish_output(path, content, run_nonce, initial_snapshot, lock)
  local lfs = require("lfs")
  local parent, basename = validate_output_parent(path)
  local temporary_directory = nil
  local temporary_payload = nil
  local last_mkdir_error = nil

  for attempt = 1, 64 do
    local candidate = string.format(
      "%s/.%s.nexus-margin-tmp-%s-%02d",
      parent,
      basename,
      run_nonce,
      attempt
    )
    local ok, mkdir_error = lfs.mkdir(candidate)
    if ok then
      temporary_directory = candidate
      temporary_payload = candidate .. "/payload"
      break
    end
    last_mkdir_error = mkdir_error
  end
  if not temporary_directory then
    fail("cannot create sibling temporary directory: " .. tostring(last_mkdir_error))
  end

  local function cleanup()
    if temporary_payload then
      os.remove(temporary_payload)
    end
    if temporary_directory then
      lfs.rmdir(temporary_directory)
    end
  end

  local ok, publication_error = pcall(function()
    write_file(temporary_payload, content)
    require_owned_output_lock(lock)
    output_is_unchanged(path, initial_snapshot)
    require_owned_output_lock(lock)
    local renamed, rename_error = os.rename(temporary_payload, path)
    if not renamed then
      fail("cannot publish output: " .. tostring(rename_error))
    end
  end)
  cleanup()
  if not ok then
    error(publication_error, 0)
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
  local parent, basename = validate_output_parent(output_path)
  local lock = acquire_output_lock(parent, basename)
  local operation_ok, operation_error = pcall(function()
    local initial_output = output_snapshot(output_path)
    local root = script_directory() .. "/.."
    local json = load_module(root .. "/gabarits/nexus-margin-json.lua", "JSON codec")
    local layout = load_module(root .. "/gabarits/nexus-margin-layout.lua", "layout solver")
    local current = json.decode(read_file(input_path))
    local previous = previous_path and json.decode(read_file(previous_path)) or nil
    local solved = layout.solve(current, previous)
    local encoded = json.encode(solved)
    publish_output(output_path, encoded, current.run_nonce, initial_output, lock)
  end)
  local release_ok, release_error = pcall(release_output_lock, lock)
  if not operation_ok then
    if not release_ok then
      error(tostring(operation_error) .. "; " .. tostring(release_error), 0)
    end
    error(operation_error, 0)
  end
  if not release_ok then
    error(release_error, 0)
  end
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
