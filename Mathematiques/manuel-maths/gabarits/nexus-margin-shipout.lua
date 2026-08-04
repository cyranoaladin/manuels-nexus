local M = {}

local source = debug.getinfo(1, "S").source:gsub("^@", "")
local module_directory = source:match("^(.*)/[^/]+$") or "."

local function load_sibling(name)
  local chunk, load_error = loadfile(module_directory .. "/" .. name)
  if not chunk then
    error("nexus-margin: cannot load " .. name .. ": " .. tostring(load_error), 0)
  end
  return chunk()
end

local json = load_sibling("nexus-margin-json.lua")
local layout_solver = load_sibling("nexus-margin-layout.lua")
local ZERO_DIGEST = "sha256:" .. string.rep("0", 64)
local ANCHOR_WHATSIT_ID = luatexbase.newuserwhatsitid(
  "anchor", "nexus-margin-compositor"
)
local OBSTACLE_WHATSIT_ID = luatexbase.newuserwhatsitid(
  "obstacle", "nexus-margin-compositor"
)
local MARKER_METADATA_WHATSIT_ID = luatexbase.newuserwhatsitid(
  "marker-metadata", "nexus-margin-compositor"
)
local WHATSIT_SUBTYPE_NAMES = {}
for _, name in ipairs({
  "user_defined",
  "pdf_colorstack",
  "pdf_literal",
  "special",
  "late_lua",
  "pdf_start_link",
  "pdf_end_link",
  "pdf_dest",
  "pdf_action",
}) do
  local ok, subtype = pcall(node.subtype, name)
  if ok and type(subtype) == "number" then
    WHATSIT_SUBTYPE_NAMES[subtype] = name
  end
end

local captures = {}
local capture_order = {}
local anchors = {}
local pages = {}
local configured = false
local finalized = false
local shipout_index = 0
local configuration = nil

local function json_object(fields)
  local result = json.new_object()
  for key, value in pairs(fields or {}) do
    result[key] = value
  end
  return result
end

local function json_array(values)
  local result = json.new_array()
  for index, value in ipairs(values or {}) do
    result[index] = value
  end
  return result
end

local function fail(message)
  error("NEXUS-MARGIN-ERROR:capture:" .. message, 0)
end

local function margin_error(code, identifier)
  local message = "NEXUS-MARGIN-ERROR:" .. code .. ":" .. identifier
  texio.write_nl("term and log", message)
  error(message, 0)
end

local function require_ascii_fragment(value, label)
  if type(value) ~= "string" or not value:match("^[%w%-]+$") then
    fail(label .. " must contain ASCII letters, digits or hyphens only")
  end
end

local SHA256_CONSTANTS = {
  0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
  0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
  0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
  0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
  0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
  0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
  0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
  0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
  0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
  0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
  0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
  0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
  0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
  0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
  0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
  0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
}

local function uint32(value)
  return value & 0xffffffff
end

local function rotate_right(value, count)
  return uint32((value >> count) | (value << (32 - count)))
end

local function sha256_hex(message)
  local bit_length = #message * 8
  local high_length = math.floor(bit_length / 0x100000000)
  local low_length = bit_length % 0x100000000
  local padding_length = (56 - (#message + 1) % 64) % 64
  local padded = message .. string.char(0x80) .. string.rep("\0", padding_length)
    .. string.char(
      (high_length >> 24) & 0xff,
      (high_length >> 16) & 0xff,
      (high_length >> 8) & 0xff,
      high_length & 0xff,
      (low_length >> 24) & 0xff,
      (low_length >> 16) & 0xff,
      (low_length >> 8) & 0xff,
      low_length & 0xff
    )
  local hash = {
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
  }

  for offset = 1, #padded, 64 do
    local words = {}
    for index = 1, 16 do
      local word_offset = offset + (index - 1) * 4
      local first, second, third, fourth = padded:byte(word_offset, word_offset + 3)
      words[index] = uint32(
        (first << 24) | (second << 16) | (third << 8) | fourth
      )
    end
    for index = 17, 64 do
      local earlier = words[index - 15]
      local later = words[index - 2]
      local sigma_zero = rotate_right(earlier, 7)
        ~ rotate_right(earlier, 18) ~ (earlier >> 3)
      local sigma_one = rotate_right(later, 17)
        ~ rotate_right(later, 19) ~ (later >> 10)
      words[index] = uint32(
        words[index - 16] + sigma_zero + words[index - 7] + sigma_one
      )
    end

    local a, b, c, d, e, f, g, h = table.unpack(hash)
    for index = 1, 64 do
      local capital_sigma_one = rotate_right(e, 6)
        ~ rotate_right(e, 11) ~ rotate_right(e, 25)
      local choice = (e & f) ~ ((~e) & g)
      local temporary_one = uint32(
        h + capital_sigma_one + choice + SHA256_CONSTANTS[index] + words[index]
      )
      local capital_sigma_zero = rotate_right(a, 2)
        ~ rotate_right(a, 13) ~ rotate_right(a, 22)
      local majority = (a & b) ~ (a & c) ~ (b & c)
      local temporary_two = uint32(capital_sigma_zero + majority)
      h = g
      g = f
      f = e
      e = uint32(d + temporary_one)
      d = c
      c = b
      b = a
      a = uint32(temporary_one + temporary_two)
    end
    hash[1] = uint32(hash[1] + a)
    hash[2] = uint32(hash[2] + b)
    hash[3] = uint32(hash[3] + c)
    hash[4] = uint32(hash[4] + d)
    hash[5] = uint32(hash[5] + e)
    hash[6] = uint32(hash[6] + f)
    hash[7] = uint32(hash[7] + g)
    hash[8] = uint32(hash[8] + h)
  end

  local pieces = {}
  for index, word in ipairs(hash) do
    pieces[index] = string.format("%08x", word)
  end
  return table.concat(pieces)
end

local function digest(message)
  return "sha256:" .. sha256_hex(message)
end

local function append_scalar(pieces, label, value)
  local rendered = tostring(value or "")
  pieces[#pieces + 1] = label .. "=" .. #rendered .. ":" .. rendered .. ";"
end

local function safe_node_field(value, field)
  local ok, result = pcall(function()
    return value[field]
  end)
  if not ok then
    return nil
  end
  local result_type = type(result)
  if result_type == "string" or result_type == "number"
      or result_type == "boolean" then
    return result
  end
  return nil
end

local CONTROLLED_LINK_ACTION_FIELDS = {
  "action_type",
  "named_id",
  "file",
  "data",
  "new_window",
  "struct_id",
}

local function append_controlled_link_action(pieces, current)
  local ok, action = pcall(function()
    return current.action
  end)
  if not ok or not action then
    return
  end
  for _, field in ipairs(CONTROLLED_LINK_ACTION_FIELDS) do
    local value = safe_node_field(action, field)
    if value ~= nil then
      append_scalar(pieces, "link_" .. field, value)
    end
  end
end

local function walk_normalized(head, pieces)
  for current in node.traverse(head) do
    local kind = node.type(current.id)
    append_scalar(pieces, "node", kind)
    append_scalar(pieces, "subtype", current.subtype or 0)
    if kind == "glyph" then
      append_scalar(pieces, "font", current.font)
      append_scalar(pieces, "char", current.char)
      append_scalar(pieces, "width", current.width)
      append_scalar(pieces, "height", current.height)
      append_scalar(pieces, "depth", current.depth)
      append_scalar(pieces, "xoffset", current.xoffset)
      append_scalar(pieces, "yoffset", current.yoffset)
    elseif kind == "glue" then
      append_scalar(pieces, "width", current.width)
      append_scalar(pieces, "stretch", current.stretch)
      append_scalar(pieces, "shrink", current.shrink)
      append_scalar(pieces, "stretch_order", current.stretch_order)
      append_scalar(pieces, "shrink_order", current.shrink_order)
    elseif kind == "kern" then
      append_scalar(pieces, "kern", current.kern or current.width)
    elseif kind == "rule" then
      append_scalar(pieces, "width", current.width)
      append_scalar(pieces, "height", current.height)
      append_scalar(pieces, "depth", current.depth)
    elseif kind == "hlist" or kind == "vlist" then
      append_scalar(pieces, "width", current.width)
      append_scalar(pieces, "height", current.height)
      append_scalar(pieces, "depth", current.depth)
      append_scalar(pieces, "shift", current.shift)
      append_scalar(pieces, "dir", current.dir)
      pieces[#pieces + 1] = "list["
      if current.list then
        walk_normalized(current.list, pieces)
      end
      pieces[#pieces + 1] = "]"
    elseif kind == "disc" then
      for _, field in ipairs({ "pre", "post", "replace" }) do
        pieces[#pieces + 1] = field .. "["
        if current[field] then
          walk_normalized(current[field], pieces)
        end
        pieces[#pieces + 1] = "]"
      end
    elseif kind == "whatsit" then
      local subtype_name = WHATSIT_SUBTYPE_NAMES[current.subtype]
        or tostring(current.subtype)
      append_scalar(pieces, "whatsit", subtype_name)
      if subtype_name == "pdf_colorstack" then
        append_scalar(pieces, "command", current.command)
        append_scalar(pieces, "stack", current.stack)
        append_scalar(pieces, "data", current.data)
      elseif subtype_name == "pdf_literal" or subtype_name == "special" then
        append_scalar(pieces, "mode", current.mode)
        append_scalar(pieces, "data", current.data or current.token)
      elseif subtype_name == "user_defined" then
        append_scalar(pieces, "user_id", current.user_id)
        append_scalar(pieces, "user_type", current.type)
        append_scalar(pieces, "value", current.value)
      elseif subtype_name == "late_lua" then
        append_scalar(pieces, "data", current.data or current.token)
      elseif subtype_name == "pdf_start_link" then
        append_controlled_link_action(pieces, current)
      end
    end
  end
end

local function collect_link_metadata(head, records)
  for current in node.traverse(head) do
    local kind = node.type(current.id)
    if kind == "whatsit" then
      local subtype_name = WHATSIT_SUBTYPE_NAMES[current.subtype]
        or tostring(current.subtype)
      if subtype_name == "pdf_start_link" then
        local fields = {}
        append_controlled_link_action(fields, current)
        records[#records + 1] = table.concat(fields)
      end
    end
    if (kind == "hlist" or kind == "vlist") and current.list then
      collect_link_metadata(current.list, records)
    end
  end
end

local horizontal_list_extent
local vertical_list_extent

local function materialized_advance(current, parent)
  local glue_set = parent and parent.glue_set or 0
  local glue_sign = parent and parent.glue_sign or 0
  local glue_order = parent and parent.glue_order or 0
  local width = node.dimensions(
    glue_set,
    glue_sign,
    glue_order,
    current,
    current.next
  )
  if type(width) ~= "number" then
    fail("cannot measure horizontal node advance")
  end
  return width
end

local function box_horizontal_extent(box)
  local left_sp = 0
  local right_sp = math.max(0, box.width or 0)
  if not box.list then
    return left_sp, right_sp
  end
  local content_left_sp, content_right_sp
  if node.type(box.id) == "hlist" then
    content_left_sp, content_right_sp = horizontal_list_extent(box.list, box)
  else
    content_left_sp, content_right_sp = vertical_list_extent(box.list)
  end
  return math.min(left_sp, content_left_sp), math.max(right_sp, content_right_sp)
end

horizontal_list_extent = function(head, parent)
  local cursor_sp = 0
  local left_sp = 0
  local right_sp = 0
  local leading_protrusion_sp = 0
  local trailing_protrusion_sp = 0
  for current in node.traverse(head) do
    local kind = node.type(current.id)
    if kind == "hlist" or kind == "vlist" then
      local child_left_sp, child_right_sp = box_horizontal_extent(current)
      left_sp = math.min(left_sp, cursor_sp + child_left_sp)
      right_sp = math.max(right_sp, cursor_sp + child_right_sp)
    elseif kind == "disc" and current.replace then
      local child_left_sp, child_right_sp = horizontal_list_extent(
        current.replace,
        nil
      )
      left_sp = math.min(left_sp, cursor_sp + child_left_sp)
      right_sp = math.max(right_sp, cursor_sp + child_right_sp)
    end
    local advance_sp = materialized_advance(current, parent)
    if kind == "margin_kern" and advance_sp < 0 then
      if current.subtype == 0 and cursor_sp == 0 then
        leading_protrusion_sp = math.max(
          leading_protrusion_sp,
          -advance_sp
        )
      elseif current.subtype == 1 then
        trailing_protrusion_sp = math.max(
          trailing_protrusion_sp,
          -advance_sp
        )
      end
    end
    cursor_sp = cursor_sp + advance_sp
    left_sp = math.min(left_sp, cursor_sp)
    right_sp = math.max(right_sp, cursor_sp)
  end
  -- Microtype uses boundary margin_kern nodes for optical protrusion.  Their
  -- allowances belong to the adjacent glyph/box, not to a true overfull run.
  left_sp = math.min(0, left_sp + leading_protrusion_sp)
  right_sp = math.max(cursor_sp, right_sp - trailing_protrusion_sp)
  return left_sp, right_sp
end

vertical_list_extent = function(head)
  local left_sp = 0
  local right_sp = 0
  for current in node.traverse(head) do
    local kind = node.type(current.id)
    if kind == "hlist" or kind == "vlist" then
      local child_left_sp, child_right_sp = box_horizontal_extent(current)
      local horizontal_shift_sp = current.shift or 0
      left_sp = math.min(left_sp, horizontal_shift_sp + child_left_sp)
      right_sp = math.max(right_sp, horizontal_shift_sp + child_right_sp)
    elseif kind == "rule" then
      left_sp = math.min(left_sp, 0)
      right_sp = math.max(right_sp, current.width or 0)
    elseif kind == "whatsit" then
      local width_sp = safe_node_field(current, "width")
      if type(width_sp) == "number" and width_sp > 0
          and width_sp < 0x3fffffff then
        right_sp = math.max(right_sp, width_sp)
      end
    end
  end
  return left_sp, right_sp
end

local function find_oversized_horizontal(head, limit_sp)
  local left_sp, right_sp = vertical_list_extent(head)
  if left_sp < -1 or right_sp > limit_sp + 1 then
    return math.ceil(right_sp - left_sp)
  end
  return nil
end

local function semantic_digest(head)
  local pieces = { "nexus-margin-node-list-v1[" }
  if head then
    walk_normalized(head, pieces)
  end
  pieces[#pieces + 1] = "]"
  return digest(table.concat(pieces))
end

function M.configure(values)
  if configured then
    fail("configuration repeated")
  end
  if type(values) ~= "table" then
    fail("configuration must be a table")
  end
  local environment_variant = os.getenv("NEXUS_MARGIN_VARIANT")
  local variant = values.variant
  require_ascii_fragment(variant, "variant")
  if environment_variant and environment_variant ~= ""
      and environment_variant ~= variant then
    fail("variant does not match NEXUS_MARGIN_VARIANT")
  end
  local pass_number = tonumber(os.getenv("NEXUS_MARGIN_PASS_NUMBER") or "1")
  if not pass_number or math.type(pass_number) ~= "integer"
      or pass_number < 1 or pass_number > 6 then
    fail("invalid NEXUS_MARGIN_PASS_NUMBER")
  end
  local run_nonce = os.getenv("NEXUS_MARGIN_RUN_NONCE")
    or "00000000000000000000000000000000"
  if not run_nonce:match("^[0-9a-f]+$") or #run_nonce ~= 32 then
    fail("invalid NEXUS_MARGIN_RUN_NONCE")
  end
  for _, field in ipairs({
    "page_width_sp",
    "page_height_sp",
    "rail_width_sp",
    "odd_rail_left_sp",
    "even_rail_left_sp",
    "rail_top_sp",
    "rail_bottom_sp",
    "report_decoration_height_sp",
  }) do
    local value = values[field]
    if type(value) ~= "number" or math.type(value) ~= "integer" or value < 0 then
      fail(field .. " must be a non-negative integer")
    end
  end
  if values.page_width_sp < 1 or values.page_height_sp < 1
      or values.rail_width_sp < 1 or values.report_decoration_height_sp < 1 then
    fail("page, rail and report dimensions must be positive")
  end
  if values.rail_top_sp >= values.rail_bottom_sp
      or values.rail_bottom_sp > values.page_height_sp then
    fail("invalid vertical rail geometry")
  end
  for _, left_sp in ipairs({ values.odd_rail_left_sp, values.even_rail_left_sp }) do
    if left_sp < 0 or left_sp + values.rail_width_sp > values.page_width_sp then
      fail("invalid horizontal rail geometry")
    end
  end
  local marker_metadata_value = os.getenv("NEXUS_MARGIN_MARKER_METADATA") or "1"
  if marker_metadata_value ~= "0" and marker_metadata_value ~= "1" then
    fail("invalid NEXUS_MARGIN_MARKER_METADATA")
  end
  configuration = {
    variant = variant,
    pass_number = pass_number,
    run_nonce = run_nonce,
    next_path = os.getenv("NEXUS_MARGIN_LAYOUT_NEXT"),
    previous_path = os.getenv("NEXUS_MARGIN_LAYOUT_PREVIOUS"),
    page_width_sp = values.page_width_sp,
    page_height_sp = values.page_height_sp,
    rail_width_sp = values.rail_width_sp,
    odd_rail_left_sp = values.odd_rail_left_sp,
    even_rail_left_sp = values.even_rail_left_sp,
    rail_top_sp = values.rail_top_sp,
    rail_bottom_sp = values.rail_bottom_sp,
    report_decoration_height_sp = values.report_decoration_height_sp,
    marker_metadata = marker_metadata_value == "1",
  }
  configured = true
end

function M.capture_box(identifier, role, global_order, box_number)
  if not configured then
    fail("capture before configuration")
  end
  require_ascii_fragment(role, "role")
  local expected = string.format(
    "nxm:%s:%s:%08d", configuration.variant, role, global_order
  )
  if identifier ~= expected then
    fail("noncanonical identifier " .. tostring(identifier))
  end
  if captures[identifier] then
    fail("duplicate capture " .. identifier)
  end
  local box = tex.box[box_number]
  if not box then
    fail("missing TeX capture box for " .. identifier)
  end
  local copied_list = box.list and node.copy_list(box.list) or nil
  local width_sp = math.tointeger(box.width)
  local base_height_sp = math.tointeger(box.height + box.depth)
  if not width_sp or width_sp < 1 or not base_height_sp or base_height_sp < 1 then
    fail("invalid captured dimensions for " .. identifier)
  end
  if find_oversized_horizontal(copied_list, configuration.rail_width_sp) then
    margin_error("width", identifier)
  end
  if base_height_sp > configuration.rail_bottom_sp - configuration.rail_top_sp then
    margin_error("height", identifier)
  end
  local links = {}
  if copied_list then
    collect_link_metadata(copied_list, links)
  end
  captures[identifier] = {
    id = identifier,
    role = role,
    global_order = global_order,
    list = copied_list,
    width_sp = width_sp,
    base_height_sp = base_height_sp,
    semantic_digest = semantic_digest(copied_list),
    links = links,
    capture_count = 1,
  }
  capture_order[#capture_order + 1] = identifier
  texio.write_nl("term and log", "NEXUS-MARGIN-CAPTURE:" .. identifier)
  if #links > 0 then
    texio.write_nl(
      "term and log",
      "NEXUS-MARGIN-LINKS:" .. identifier .. ":" .. #links
    )
  end
end

function M.write_anchor_whatsit(identifier)
  local marker = node.new("whatsit", "user_defined")
  marker.user_id = ANCHOR_WHATSIT_ID
  marker.type = 115
  marker.value = identifier
  node.write(marker)
  if configuration.marker_metadata then
    local metadata = node.new("whatsit", "user_defined")
    metadata.user_id = MARKER_METADATA_WHATSIT_ID
    metadata.type = 115
    metadata.value = identifier
    node.write(metadata)
    texio.write_nl(
      "term and log", "NEXUS-MARGIN-MARKER-METADATA:" .. identifier
    )
  end
end

function M.write_obstacle_whatsit(identifier, left_sp, top_sp, right_sp, bottom_sp)
  require_ascii_fragment(identifier, "obstacle id")
  for _, value in ipairs({ left_sp, top_sp, right_sp, bottom_sp }) do
    if type(value) ~= "number" or math.type(value) ~= "integer" or value < 0 then
      margin_error("placement", identifier)
    end
  end
  if left_sp >= right_sp or top_sp >= bottom_sp
      or right_sp > configuration.page_width_sp
      or bottom_sp > configuration.page_height_sp then
    margin_error("placement", identifier)
  end
  local marker = node.new("whatsit", "user_defined")
  marker.user_id = OBSTACLE_WHATSIT_ID
  marker.type = 115
  marker.value = table.concat({
    identifier,
    string.format("%d", left_sp),
    string.format("%d", top_sp),
    string.format("%d", right_sp),
    string.format("%d", bottom_sp),
  }, "|")
  node.write(marker)
end

local function decode_obstacle(value)
  if type(value) ~= "string" then
    return nil
  end
  local identifier, left, top, right, bottom = value:match(
    "^([^|]+)|(%d+)|(%d+)|(%d+)|(%d+)$"
  )
  if not identifier then
    return nil
  end
  return {
    id = identifier,
    left_sp = math.tointeger(left),
    top_sp = math.tointeger(top),
    right_sp = math.tointeger(right),
    bottom_sp = math.tointeger(bottom),
  }
end

local function visit_page_whatsits(
  head,
  page_index,
  folio,
  page_obstacles,
  page_obstacle_ids
)
  for current in node.traverse(head) do
    local kind = node.type(current.id)
    if kind == "whatsit" and current.subtype == node.subtype("user_defined")
        and current.user_id == ANCHOR_WHATSIT_ID then
      local identifier = current.value
      if type(identifier) ~= "string" or not captures[identifier] then
        fail("anchor whatsit references an unknown capture")
      end
      local anchor = anchors[identifier] or {
        id = identifier,
        whatsit_count = 0,
        resolve_count = 0,
      }
      anchor.whatsit_count = anchor.whatsit_count + 1
      anchor.shipout_index = page_index
      anchor.folio = folio
      anchors[identifier] = anchor
    elseif kind == "whatsit" and current.subtype == node.subtype("user_defined")
        and current.user_id == OBSTACLE_WHATSIT_ID then
      local obstacle = decode_obstacle(current.value)
      local base_identifier = obstacle and obstacle.id or "invalid-obstacle"
      local qualified_identifier = string.format(
        "%s-p%08d", base_identifier, page_index
      )
      if not obstacle or page_obstacle_ids[base_identifier] then
        margin_error("placement", qualified_identifier)
      end
      page_obstacle_ids[base_identifier] = true
      obstacle.id = qualified_identifier
      page_obstacles[#page_obstacles + 1] = obstacle
    end
    if (kind == "hlist" or kind == "vlist") and current.list then
      visit_page_whatsits(
        current.list,
        page_index,
        folio,
        page_obstacles,
        page_obstacle_ids
      )
    end
  end
end

local function pre_shipout(head)
  if not configured then
    return head
  end
  shipout_index = shipout_index + 1
  local folio = tostring(tex.count["c@page"] or tex.count[0] or shipout_index)
  local rail_side = shipout_index % 2 == 1 and "right" or "left"
  local rail_left = rail_side == "right"
      and configuration.odd_rail_left_sp or configuration.even_rail_left_sp
  local page_obstacles = {}
  local page_obstacle_ids = {}
  pages[shipout_index] = {
    shipout_index = shipout_index,
    folio = folio,
    page_width_sp = configuration.page_width_sp,
    page_height_sp = configuration.page_height_sp,
    rail_side = rail_side,
    rail_left_sp = rail_left,
    obstacles = page_obstacles,
  }
  visit_page_whatsits(
    head,
    shipout_index,
    folio,
    page_obstacles,
    page_obstacle_ids
  )
  table.sort(page_obstacles, function(first, second)
    if first.top_sp ~= second.top_sp then
      return first.top_sp < second.top_sp
    end
    if first.bottom_sp ~= second.bottom_sp then
      return first.bottom_sp < second.bottom_sp
    end
    if first.left_sp ~= second.left_sp then
      return first.left_sp < second.left_sp
    end
    if first.right_sp ~= second.right_sp then
      return first.right_sp < second.right_sp
    end
    return first.id < second.id
  end)
  return head
end

function M.resolve_anchor(identifier)
  local anchor = anchors[identifier]
  if not anchor then
    fail("shipout resolution lacks anchor whatsit for " .. tostring(identifier))
  end
  local x_sp, y_sp = pdf.getpos()
  if type(x_sp) ~= "number" or type(y_sp) ~= "number" then
    fail("shipout did not resolve coordinates for " .. identifier)
  end
  anchor.resolve_count = anchor.resolve_count + 1
  anchor.x_sp = math.floor(x_sp + 0.5)
  local page = pages[anchor.shipout_index]
  anchor.y_sp = math.max(
    0,
    math.min(page.page_height_sp, page.page_height_sp - math.floor(y_sp + 0.5))
  )
  texio.write_nl("term and log", "NEXUS-MARGIN-ANCHOR:" .. identifier)
end

local function read_previous()
  local path = configuration.previous_path
  if not path or path == "" then
    return nil
  end
  local handle = io.open(path, "rb")
  if not handle then
    return nil
  end
  local bytes = handle:read("*a")
  local closed, close_error = handle:close()
  if not closed then
    fail("cannot close previous layout: " .. tostring(close_error))
  end
  return json.decode(bytes)
end

local function current_envelope()
  if #capture_order == 0 then
    fail("zero annotations captured")
  end
  local note_records = json_array()
  local page_records = json_array()
  local semantic_parts = {}
  for index, identifier in ipairs(capture_order) do
    local capture = captures[identifier]
    local anchor = anchors[identifier]
    if capture.capture_count ~= 1 then
      fail("capture count is not one for " .. identifier)
    end
    if not anchor or anchor.whatsit_count ~= 1 or anchor.resolve_count ~= 1 then
      fail("anchor count is not one for " .. identifier)
    end
    note_records[index] = json_object({
      id = identifier,
      role = capture.role,
      global_order = capture.global_order,
      origin_shipout_index = anchor.shipout_index,
      origin_folio = anchor.folio,
      origin_y_sp = anchor.y_sp,
      target_shipout_index = json.JSON_NULL,
      target_y_sp = json.JSON_NULL,
      width_sp = capture.width_sp,
      base_height_sp = capture.base_height_sp,
      report_decoration_height_sp = configuration.report_decoration_height_sp,
      effective_height_sp = capture.base_height_sp,
      report_depth = 0,
      requires_marker = false,
      semantic_digest = capture.semantic_digest,
    })
    semantic_parts[#semantic_parts + 1] = identifier .. "=" .. capture.semantic_digest
  end

  local native_by_page = {}
  for _, note in ipairs(note_records) do
    local native = native_by_page[note.origin_shipout_index] or {}
    native[#native + 1] = note
    native_by_page[note.origin_shipout_index] = native
  end
  for index, page in ipairs(pages) do
    local native_notes = native_by_page[index] or {}
    table.sort(native_notes, function(first, second)
      if first.origin_y_sp ~= second.origin_y_sp then
        return first.origin_y_sp < second.origin_y_sp
      end
      if first.global_order ~= second.global_order then
        return first.global_order < second.global_order
      end
      return first.id < second.id
    end)
    local native_ids = json_array()
    for native_index, note in ipairs(native_notes) do
      native_ids[native_index] = note.id
    end
    local obstacle_records = json_array()
    for obstacle_index, obstacle in ipairs(page.obstacles) do
      obstacle_records[obstacle_index] = json_object({
        id = obstacle.id,
        left_sp = obstacle.left_sp,
        top_sp = obstacle.top_sp,
        right_sp = obstacle.right_sp,
        bottom_sp = obstacle.bottom_sp,
      })
    end
    page_records[index] = json_object({
      shipout_index = page.shipout_index,
      folio = page.folio,
      page_width_sp = page.page_width_sp,
      page_height_sp = page.page_height_sp,
      rail_side = page.rail_side,
      safe_rect = json_object({
        left_sp = page.rail_left_sp,
        top_sp = configuration.rail_top_sp,
        right_sp = page.rail_left_sp + configuration.rail_width_sp,
        bottom_sp = configuration.rail_bottom_sp,
      }),
      native_note_ids = native_ids,
      carry_in_note_ids = json_array(),
      placed_note_ids = json_array(),
      reported_note_ids = json_array(),
      obstacles = obstacle_records,
    })
  end

  local geometry_parts = {}
  for _, page in ipairs(page_records) do
    geometry_parts[#geometry_parts + 1] = table.concat({
      page.shipout_index,
      page.page_width_sp,
      page.page_height_sp,
      page.rail_side,
      page.safe_rect.left_sp,
      page.safe_rect.top_sp,
      page.safe_rect.right_sp,
      page.safe_rect.bottom_sp,
    }, ":")
    for _, obstacle in ipairs(page.obstacles) do
      geometry_parts[#geometry_parts + 1] = table.concat({
        obstacle.id,
        obstacle.left_sp,
        obstacle.top_sp,
        obstacle.right_sp,
        obstacle.bottom_sp,
      }, ":")
    end
  end
  return json_object({
    schema_version = 1,
    run_nonce = configuration.run_nonce,
    variant = configuration.variant,
    geometry_digest = digest(table.concat(geometry_parts, "|")),
    semantic_digest = digest(table.concat(semantic_parts, "|")),
    state = "collecting",
    pass_number = configuration.pass_number,
    max_passes = 6,
    read_digest = json.JSON_NULL,
    computed_digest = ZERO_DIGEST,
    error_code = json.JSON_NULL,
    notes = note_records,
    pages = page_records,
  })
end

local function write_next(layout)
  local path = configuration.next_path
  if not path or path == "" then
    return
  end
  local handle, open_error = io.open(path, "wb")
  if not handle then
    fail("cannot open next layout: " .. tostring(open_error))
  end
  local ok, write_error = handle:write(json.encode(layout))
  if not ok then
    handle:close()
    fail("cannot write next layout: " .. tostring(write_error))
  end
  local closed, close_error = handle:close()
  if not closed then
    fail("cannot close next layout: " .. tostring(close_error))
  end
end

function M.finalize()
  if finalized then
    return
  end
  finalized = true
  if not configured or not configuration.next_path
      or configuration.next_path == "" then
    return
  end
  local ok, solved = pcall(layout_solver.solve, current_envelope(), read_previous())
  if not ok then
    local message = tostring(solved)
    local identifier = message:match("result%.notes%[([^%]]+)%]")
    if identifier and message:find("margin%-report%-impossible") then
      margin_error("placement", identifier)
    end
    error(message, 0)
  end
  write_next(solved)
end

luatexbase.add_to_callback(
  "pre_shipout_filter", pre_shipout, "nexus-margin-compositor.capture-anchors"
)

return M
