local M = {}

local GAP_SP = 6 * 65536

local function fail(path, message)
  error(string.format("invalid margin layout at %s: %s", path, message), 0)
end

local function json_container_type(value)
  local metatable = type(value) == "table" and getmetatable(value) or nil
  return metatable and metatable.__nexus_json_type or nil
end

local function deep_copy(value, copies)
  if type(value) ~= "table" then
    return value
  end
  if json_container_type(value) == "null" then
    return value
  end
  copies = copies or {}
  if copies[value] then
    return copies[value]
  end
  local result = setmetatable({}, getmetatable(value))
  copies[value] = result
  for key, item in next, value do
    result[deep_copy(key, copies)] = deep_copy(item, copies)
  end
  return result
end

local function require_table(value, path)
  if type(value) ~= "table" or json_container_type(value) == "null" then
    fail(path, "expected a table")
  end
end

local function require_object(value, path)
  require_table(value, path)
  local tag = json_container_type(value)
  if tag and tag ~= "object" then
    fail(path, "expected an object")
  end
end

local function require_array(value, path)
  require_table(value, path)
  local tag = json_container_type(value)
  if tag and tag ~= "array" then
    fail(path, "expected an array")
  end
  local count = 0
  local maximum = 0
  for key in next, value do
    if type(key) ~= "number" or math.type(key) ~= "integer" or key < 1 then
      fail(path, "array key must be a positive integer")
    end
    count = count + 1
    maximum = math.max(maximum, key)
  end
  if count ~= maximum then
    fail(path, "array must not contain holes")
  end
end

local function require_string(value, path)
  if type(value) ~= "string" or value == "" then
    fail(path, "expected a non-empty string")
  end
end

local function require_boolean(value, path)
  if type(value) ~= "boolean" then
    fail(path, "expected a boolean")
  end
end

local function require_integer(value, path, minimum)
  if type(value) ~= "number" or math.type(value) ~= "integer"
      or (minimum and value < minimum) then
    fail(path, "expected an integer" .. (minimum and " >= " .. minimum or ""))
  end
end

local function require_nullable_integer(value, path, minimum)
  if json_container_type(value) == "null" then
    return
  end
  require_integer(value, path, minimum)
end

local function require_sha256(value, path)
  if type(value) ~= "string" or #value ~= 71
      or value:sub(1, 7) ~= "sha256:"
      or not value:sub(8):match("^[0-9a-f]+$") then
    fail(path, "expected a lowercase sha256 digest")
  end
end

local function require_enum(value, path, allowed)
  if not allowed[value] then
    fail(path, "unexpected value " .. tostring(value))
  end
end

local function validate_id_array(ids, path, notes_by_id)
  require_array(ids, path)
  local seen = {}
  for index, note_id in ipairs(ids) do
    require_string(note_id, string.format("%s[%d]", path, index))
    if seen[note_id] then
      fail(path, "duplicate note id " .. note_id)
    end
    if not notes_by_id[note_id] then
      fail(path, "unknown note id " .. note_id)
    end
    seen[note_id] = true
  end
end

local function validate_layout(layout, label)
  require_object(layout, label)
  require_integer(layout.schema_version, label .. ".schema_version", 1)
  if layout.schema_version ~= 1 then
    fail(label .. ".schema_version", "expected 1")
  end
  require_string(layout.run_nonce, label .. ".run_nonce")
  if #layout.run_nonce ~= 32 or not layout.run_nonce:match("^[0-9a-f]+$") then
    fail(label .. ".run_nonce", "expected 32 lowercase hexadecimal digits")
  end
  require_enum(layout.variant, label .. ".variant", {
    eleve = true,
    professeur = true,
  })
  require_sha256(layout.geometry_digest, label .. ".geometry_digest")
  require_sha256(layout.semantic_digest, label .. ".semantic_digest")
  require_enum(layout.state, label .. ".state", {
    collecting = true,
    changed = true,
    stable = true,
    failed = true,
  })
  require_integer(layout.pass_number, label .. ".pass_number", 1)
  if layout.pass_number > 6 then
    fail(label .. ".pass_number", "expected an integer <= 6")
  end
  require_integer(layout.max_passes, label .. ".max_passes", 1)
  if layout.max_passes ~= 6 then
    fail(label .. ".max_passes", "expected 6")
  end
  if json_container_type(layout.read_digest) ~= "null" then
    require_sha256(layout.read_digest, label .. ".read_digest")
  end
  require_sha256(layout.computed_digest, label .. ".computed_digest")
  if json_container_type(layout.error_code) ~= "null" then
    require_enum(layout.error_code, label .. ".error_code", {
      ["margin-note-too-tall"] = true,
      ["margin-note-too-wide"] = true,
      ["margin-report-impossible"] = true,
      ["margin-layout-oscillation"] = true,
      ["foreign-margin-layout"] = true,
      ["malformed-margin-layout"] = true,
      ["unsupported-margin-mode"] = true,
    })
  end
  require_array(layout.notes, label .. ".notes")
  require_array(layout.pages, label .. ".pages")

  local notes_by_id = {}
  local orders = {}
  for index, note in ipairs(layout.notes) do
    local path = string.format("%s.notes[%d]", label, index)
    require_object(note, path)
    require_string(note.id, path .. ".id")
    if notes_by_id[note.id] then
      fail(path .. ".id", "duplicate note id " .. note.id)
    end
    require_string(note.role, path .. ".role")
    require_integer(note.global_order, path .. ".global_order", 1)
    if orders[note.global_order] then
      fail(path .. ".global_order", "duplicate global_order")
    end
    require_integer(note.origin_shipout_index, path .. ".origin_shipout_index", 1)
    require_string(note.origin_folio, path .. ".origin_folio")
    require_integer(note.origin_y_sp, path .. ".origin_y_sp", 0)
    require_nullable_integer(note.target_shipout_index, path .. ".target_shipout_index", 1)
    require_nullable_integer(note.target_y_sp, path .. ".target_y_sp", 0)
    require_integer(note.width_sp, path .. ".width_sp", 1)
    require_integer(note.base_height_sp, path .. ".base_height_sp", 1)
    require_integer(
      note.report_decoration_height_sp,
      path .. ".report_decoration_height_sp",
      0
    )
    require_integer(note.effective_height_sp, path .. ".effective_height_sp", 1)
    require_integer(note.report_depth, path .. ".report_depth", 0)
    require_boolean(note.requires_marker, path .. ".requires_marker")
    require_sha256(note.semantic_digest, path .. ".semantic_digest")
    notes_by_id[note.id] = note
    orders[note.global_order] = true
  end

  local pages_by_index = {}
  local native_memberships = {}
  for index, page in ipairs(layout.pages) do
    local path = string.format("%s.pages[%d]", label, index)
    require_object(page, path)
    require_integer(page.shipout_index, path .. ".shipout_index", 1)
    if pages_by_index[page.shipout_index] then
      fail(path .. ".shipout_index", "duplicate shipout_index")
    end
    require_string(page.folio, path .. ".folio")
    require_integer(page.page_width_sp, path .. ".page_width_sp", 1)
    require_integer(page.page_height_sp, path .. ".page_height_sp", 1)
    require_enum(page.rail_side, path .. ".rail_side", { left = true, right = true })
    require_object(page.safe_rect, path .. ".safe_rect")
    require_integer(page.safe_rect.left_sp, path .. ".safe_rect.left_sp", 0)
    require_integer(page.safe_rect.top_sp, path .. ".safe_rect.top_sp", 0)
    require_integer(page.safe_rect.right_sp, path .. ".safe_rect.right_sp", 0)
    require_integer(page.safe_rect.bottom_sp, path .. ".safe_rect.bottom_sp", 0)
    validate_id_array(page.native_note_ids, path .. ".native_note_ids", notes_by_id)
    validate_id_array(page.carry_in_note_ids, path .. ".carry_in_note_ids", notes_by_id)
    validate_id_array(page.placed_note_ids, path .. ".placed_note_ids", notes_by_id)
    validate_id_array(page.reported_note_ids, path .. ".reported_note_ids", notes_by_id)
    require_array(page.obstacles, path .. ".obstacles")
    for obstacle_index, obstacle in ipairs(page.obstacles) do
      local obstacle_path = string.format("%s.obstacles[%d]", path, obstacle_index)
      require_object(obstacle, obstacle_path)
      require_string(obstacle.id, obstacle_path .. ".id")
      require_integer(obstacle.left_sp, obstacle_path .. ".left_sp", 0)
      require_integer(obstacle.top_sp, obstacle_path .. ".top_sp", 0)
      require_integer(obstacle.right_sp, obstacle_path .. ".right_sp", 0)
      require_integer(obstacle.bottom_sp, obstacle_path .. ".bottom_sp", 0)
    end
    local local_membership = {}
    for _, note_id in ipairs(page.native_note_ids) do
      if local_membership[note_id] then
        fail(path, "note id occurs in multiple page input lists: " .. note_id)
      end
      local_membership[note_id] = true
      if native_memberships[note_id] then
        fail(path .. ".native_note_ids", "note id occurs natively on multiple pages: " .. note_id)
      end
      native_memberships[note_id] = page.shipout_index
    end
    for _, note_id in ipairs(page.carry_in_note_ids) do
      if local_membership[note_id] then
        fail(path, "note id occurs in native and carry-in lists: " .. note_id)
      end
    end
    pages_by_index[page.shipout_index] = page
  end

  for note_id, note in next, notes_by_id do
    if not native_memberships[note_id] then
      fail(label .. ".pages", "note id is absent from native_note_ids: " .. note_id)
    end
    if native_memberships[note_id] ~= note.origin_shipout_index then
      fail(label .. ".pages", "native page disagrees with origin for note " .. note_id)
    end
  end
end

local function bytewise_less(first, second)
  local shared_length = math.min(#first, #second)
  for index = 1, shared_length do
    local first_byte = first:byte(index)
    local second_byte = second:byte(index)
    if first_byte ~= second_byte then
      return first_byte < second_byte
    end
  end
  return #first < #second
end

local function note_less(first, second)
  if first.origin_y_sp ~= second.origin_y_sp then
    return first.origin_y_sp < second.origin_y_sp
  end
  if first.global_order ~= second.global_order then
    return first.global_order < second.global_order
  end
  return bytewise_less(first.id, second.id)
end

local function order_less(first, second)
  if first.global_order ~= second.global_order then
    return first.global_order < second.global_order
  end
  return bytewise_less(first.id, second.id)
end

local function new_array_like(array)
  return setmetatable({}, getmetatable(array))
end

function M.solve(current_layout, previous_layout_or_nil)
  validate_layout(current_layout, "current")
  if previous_layout_or_nil ~= nil then
    validate_layout(previous_layout_or_nil, "previous")
  end

  local result = deep_copy(current_layout)
  table.sort(result.notes, order_less)
  table.sort(result.pages, function(first, second)
    return first.shipout_index < second.shipout_index
  end)

  local notes_by_id = {}
  for _, note in ipairs(result.notes) do
    notes_by_id[note.id] = note
  end
  local carry_target = {}
  for _, page in ipairs(result.pages) do
    for _, note_id in ipairs(page.carry_in_note_ids) do
      carry_target[note_id] = page.shipout_index
    end
  end

  for _, page in ipairs(result.pages) do
    local cursor = page.safe_rect.top_sp
    local placed_ids = new_array_like(page.placed_note_ids)
    local carry = {}
    for _, note_id in ipairs(page.carry_in_note_ids) do
      carry[#carry + 1] = notes_by_id[note_id]
    end
    table.sort(carry, order_less)
    page.carry_in_note_ids = new_array_like(page.carry_in_note_ids)
    for _, note in ipairs(carry) do
      page.carry_in_note_ids[#page.carry_in_note_ids + 1] = note.id
      note.target_shipout_index = page.shipout_index
      note.target_y_sp = cursor
      cursor = cursor + note.effective_height_sp + GAP_SP
      placed_ids[#placed_ids + 1] = note.id
    end

    local native = {}
    for _, note_id in ipairs(page.native_note_ids) do
      native[#native + 1] = notes_by_id[note_id]
    end
    table.sort(native, note_less)
    page.native_note_ids = new_array_like(page.native_note_ids)
    for _, note in ipairs(native) do
      page.native_note_ids[#page.native_note_ids + 1] = note.id
      if not carry_target[note.id] then
        note.target_shipout_index = page.shipout_index
        note.target_y_sp = math.max(note.origin_y_sp, cursor)
        cursor = note.target_y_sp + note.effective_height_sp + GAP_SP
        placed_ids[#placed_ids + 1] = note.id
      end
    end
    page.placed_note_ids = placed_ids
  end
  return result
end

return M
