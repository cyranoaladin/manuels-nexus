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
  copies = copies or {}
  if copies[value] then
    return copies[value]
  end
  local container_type = json_container_type(value)
  local result = setmetatable({}, { __nexus_json_type = container_type })
  copies[value] = result
  if container_type == "null" then
    return result
  end
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
  if tag ~= "object" then
    fail(path, "expected an object")
  end
end

local function require_array(value, path)
  require_table(value, path)
  local tag = json_container_type(value)
  if tag ~= "array" then
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

local function require_closed_object(value, path, allowed)
  require_object(value, path)
  for key in next, value do
    if type(key) ~= "string" or not allowed[key] then
      fail(path, "unexpected property " .. tostring(key))
    end
  end
end

local ROOT_FIELDS = {
  schema_version = true,
  run_nonce = true,
  variant = true,
  geometry_digest = true,
  semantic_digest = true,
  state = true,
  pass_number = true,
  max_passes = true,
  read_digest = true,
  computed_digest = true,
  error_code = true,
  notes = true,
  pages = true,
}

local NOTE_FIELDS = {
  id = true,
  role = true,
  global_order = true,
  origin_shipout_index = true,
  origin_folio = true,
  origin_y_sp = true,
  target_shipout_index = true,
  target_y_sp = true,
  width_sp = true,
  base_height_sp = true,
  report_decoration_height_sp = true,
  effective_height_sp = true,
  report_depth = true,
  requires_marker = true,
  semantic_digest = true,
}

local PAGE_FIELDS = {
  shipout_index = true,
  folio = true,
  page_width_sp = true,
  page_height_sp = true,
  rail_side = true,
  safe_rect = true,
  native_note_ids = true,
  carry_in_note_ids = true,
  placed_note_ids = true,
  reported_note_ids = true,
  obstacles = true,
}

local RECT_FIELDS = {
  left_sp = true,
  top_sp = true,
  right_sp = true,
  bottom_sp = true,
}

local OBSTACLE_FIELDS = {
  id = true,
  left_sp = true,
  top_sp = true,
  right_sp = true,
  bottom_sp = true,
}

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

local function tuple_less(first, second)
  for index = 1, math.max(#first, #second) do
    local first_value = first[index]
    local second_value = second[index]
    if first_value ~= second_value then
      if type(first_value) == "string" and type(second_value) == "string" then
        return bytewise_less(first_value, second_value)
      end
      return first_value < second_value
    end
  end
  return false
end

local function require_canonical_order(keys, path)
  for index = 2, #keys do
    if not tuple_less(keys[index - 1], keys[index]) then
      fail(path, "noncanonical order")
    end
  end
end

local function validate_rect(rect, page, path, allowed_fields)
  require_closed_object(rect, path, allowed_fields)
  require_integer(rect.left_sp, path .. ".left_sp", 0)
  require_integer(rect.top_sp, path .. ".top_sp", 0)
  require_integer(rect.right_sp, path .. ".right_sp", 0)
  require_integer(rect.bottom_sp, path .. ".bottom_sp", 0)
  if rect.left_sp >= rect.right_sp or rect.top_sp >= rect.bottom_sp then
    fail(path, "rectangle must have positive width and height")
  end
  if rect.right_sp > page.page_width_sp or rect.bottom_sp > page.page_height_sp then
    fail(path, "rectangle lies outside its page")
  end
end

local function rectangles_intersect(first, second)
  return math.max(first[1], second[1]) < math.min(first[3], second[3])
    and math.max(first[2], second[2]) < math.min(first[4], second[4])
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

local function sets_equal(first, second)
  for key in next, first do
    if not second[key] then
      return false
    end
  end
  for key in next, second do
    if not first[key] then
      return false
    end
  end
  return true
end

local function expected_memberships(note)
  local native = { [note.origin_shipout_index] = true }
  local carry = {}
  local placed = {}
  local reported = {}
  if json_container_type(note.target_shipout_index) == "null" then
    return native, carry, placed, reported
  end
  if note.target_shipout_index < note.origin_shipout_index then
    fail("note " .. note.id, "target precedes origin")
  end
  local expected_depth = note.target_shipout_index - note.origin_shipout_index
  if note.report_depth ~= expected_depth then
    fail("note " .. note.id, "incoherent report_depth")
  end
  placed[note.target_shipout_index] = true
  if expected_depth > 0 then
    for index = note.origin_shipout_index + 1, note.target_shipout_index do
      carry[index] = true
    end
    for index = note.origin_shipout_index, note.target_shipout_index - 1 do
      reported[index] = true
    end
  end
  return native, carry, placed, reported
end

local function validate_stable_geometry(pages, notes_by_id)
  for _, page in ipairs(pages) do
    local safe_rect = page.safe_rect
    local obstacle_rectangles = {}
    for _, obstacle in ipairs(page.obstacles) do
      obstacle_rectangles[#obstacle_rectangles + 1] = {
        id = obstacle.id,
        rectangle = {
          obstacle.left_sp,
          obstacle.top_sp,
          obstacle.right_sp,
          obstacle.bottom_sp,
        },
      }
    end
    local placed_rectangles = {}
    for _, note_id in ipairs(page.placed_note_ids) do
      local note = notes_by_id[note_id]
      if note.target_shipout_index ~= page.shipout_index
          or json_container_type(note.target_y_sp) == "null" then
        fail("placed note " .. note_id, "does not target its page")
      end
      local rectangle = {
        safe_rect.left_sp,
        note.target_y_sp,
        safe_rect.left_sp + note.width_sp,
        note.target_y_sp + note.effective_height_sp,
      }
      for _, obstacle_entry in ipairs(obstacle_rectangles) do
        if rectangles_intersect(rectangle, obstacle_entry.rectangle) then
          fail("placed note " .. note_id, "intersects obstacle " .. obstacle_entry.id)
        end
      end
      for _, placed_entry in ipairs(placed_rectangles) do
        if rectangles_intersect(rectangle, placed_entry.rectangle) then
          fail("placed notes", placed_entry.id .. " and " .. note_id .. " intersect")
        end
      end
      if #placed_rectangles > 0 then
        local previous = placed_rectangles[#placed_rectangles]
        if rectangle[2] - previous.rectangle[4] < GAP_SP then
          fail("placed notes", previous.id .. " and " .. note_id .. " have less than 6pt gap")
        end
      end
      placed_rectangles[#placed_rectangles + 1] = {
        id = note_id,
        rectangle = rectangle,
      }
    end
  end
end

local function validate_layout(layout, label)
  require_closed_object(layout, label, ROOT_FIELDS)
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
  if layout.state == "collecting" then
    if json_container_type(layout.read_digest) ~= "null" then
      fail(label .. ".read_digest", "collecting state requires JSON null")
    end
    if json_container_type(layout.error_code) ~= "null" then
      fail(label .. ".error_code", "collecting state requires JSON null")
    end
  elseif layout.state == "changed" or layout.state == "stable" then
    require_sha256(layout.read_digest, label .. ".read_digest")
    if json_container_type(layout.error_code) ~= "null" then
      fail(label .. ".error_code", "successful state requires JSON null")
    end
  elseif layout.state == "failed" and json_container_type(layout.error_code) == "null" then
    fail(label .. ".error_code", "failed state requires an error code")
  end
  if layout.state == "changed" and layout.read_digest == layout.computed_digest then
    fail(label, "changed state requires different digests")
  end
  if layout.state == "stable" and layout.read_digest ~= layout.computed_digest then
    fail(label, "stable state requires equal digests")
  end
  require_array(layout.notes, label .. ".notes")
  require_array(layout.pages, label .. ".pages")

  local notes_by_id = {}
  local orders = {}
  for index, note in ipairs(layout.notes) do
    local path = string.format("%s.notes[%d]", label, index)
    require_closed_object(note, path, NOTE_FIELDS)
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
  local note_order = {}
  for _, note in ipairs(layout.notes) do
    note_order[#note_order + 1] = { note.global_order, note.id }
  end
  require_canonical_order(note_order, label .. ".notes")

  local pages_by_index = {}
  local memberships = {
    native_note_ids = {},
    carry_in_note_ids = {},
    placed_note_ids = {},
    reported_note_ids = {},
  }
  for field, by_note in next, memberships do
    for note_id in next, notes_by_id do
      by_note[note_id] = {}
    end
  end
  local obstacle_ids = {}
  for index, page in ipairs(layout.pages) do
    local path = string.format("%s.pages[%d]", label, index)
    require_closed_object(page, path, PAGE_FIELDS)
    require_integer(page.shipout_index, path .. ".shipout_index", 1)
    if pages_by_index[page.shipout_index] then
      fail(path .. ".shipout_index", "duplicate shipout_index")
    end
    if page.shipout_index ~= index then
      fail(label .. ".pages", "pages must be contiguous from shipout_index 1")
    end
    require_string(page.folio, path .. ".folio")
    require_integer(page.page_width_sp, path .. ".page_width_sp", 1)
    require_integer(page.page_height_sp, path .. ".page_height_sp", 1)
    require_enum(page.rail_side, path .. ".rail_side", { left = true, right = true })
    local expected_side = page.shipout_index % 2 == 1 and "right" or "left"
    if page.rail_side ~= expected_side then
      fail(path .. ".rail_side", "incoherent rail side")
    end
    validate_rect(page.safe_rect, page, path .. ".safe_rect", RECT_FIELDS)
    validate_id_array(page.native_note_ids, path .. ".native_note_ids", notes_by_id)
    validate_id_array(page.carry_in_note_ids, path .. ".carry_in_note_ids", notes_by_id)
    validate_id_array(page.placed_note_ids, path .. ".placed_note_ids", notes_by_id)
    validate_id_array(page.reported_note_ids, path .. ".reported_note_ids", notes_by_id)
    require_array(page.obstacles, path .. ".obstacles")
    local obstacle_order = {}
    for obstacle_index, obstacle in ipairs(page.obstacles) do
      local obstacle_path = string.format("%s.obstacles[%d]", path, obstacle_index)
      require_closed_object(obstacle, obstacle_path, OBSTACLE_FIELDS)
      require_string(obstacle.id, obstacle_path .. ".id")
      if obstacle_ids[obstacle.id] then
        fail(obstacle_path .. ".id", "duplicate obstacle id")
      end
      obstacle_ids[obstacle.id] = true
      validate_rect(obstacle, page, obstacle_path, OBSTACLE_FIELDS)
      obstacle_order[#obstacle_order + 1] = {
        obstacle.top_sp,
        obstacle.bottom_sp,
        obstacle.left_sp,
        obstacle.right_sp,
        obstacle.id,
      }
    end
    require_canonical_order(obstacle_order, path .. ".obstacles")
    for field, by_note in next, memberships do
      for _, note_id in ipairs(page[field]) do
        by_note[note_id][page.shipout_index] = true
      end
    end

    local native_order = {}
    for _, note_id in ipairs(page.native_note_ids) do
      local note = notes_by_id[note_id]
      native_order[#native_order + 1] = { note.origin_y_sp, note.global_order, note_id }
    end
    require_canonical_order(native_order, path .. ".native_note_ids")
    for _, field in ipairs({ "carry_in_note_ids", "reported_note_ids" }) do
      local order = {}
      for _, note_id in ipairs(page[field]) do
        local note = notes_by_id[note_id]
        order[#order + 1] = { note.global_order, note_id }
      end
      require_canonical_order(order, path .. "." .. field)
    end
    local placed_order = {}
    for _, note_id in ipairs(page.placed_note_ids) do
      local note = notes_by_id[note_id]
      if json_container_type(note.target_y_sp) == "null" then
        fail(path .. ".placed_note_ids", "placed note has no target_y_sp")
      end
      placed_order[#placed_order + 1] = { note.target_y_sp, note.global_order, note_id }
    end
    require_canonical_order(placed_order, path .. ".placed_note_ids")
    pages_by_index[page.shipout_index] = page
  end

  local require_complete = layout.state == "stable"
  for _, note in ipairs(layout.notes) do
    local note_path = label .. ".notes[" .. note.id .. "]"
    local origin_page = pages_by_index[note.origin_shipout_index]
    if not origin_page then
      fail(note_path .. ".origin_shipout_index", "unknown origin page")
    end
    if note.origin_folio ~= origin_page.folio then
      fail(note_path .. ".origin_folio", "does not match origin page")
    end
    if note.origin_y_sp > origin_page.page_height_sp then
      fail(note_path .. ".origin_y_sp", "origin lies outside its page")
    end
    local target_index_is_null = json_container_type(note.target_shipout_index) == "null"
    local target_y_is_null = json_container_type(note.target_y_sp) == "null"
    if target_index_is_null ~= target_y_is_null then
      fail(note_path, "half-null target")
    end
    if not target_index_is_null and not pages_by_index[note.target_shipout_index] then
      fail(note_path .. ".target_shipout_index", "unknown target page")
    end
    if require_complete and target_index_is_null then
      fail(note_path, "stable note has no target")
    end
    local expected_effective_height = note.base_height_sp
    if note.report_depth > 0 then
      expected_effective_height = expected_effective_height
        + note.report_decoration_height_sp
    end
    if note.effective_height_sp ~= expected_effective_height then
      fail(note_path .. ".effective_height_sp", "incoherent effective height")
    end
    if note.report_depth > 0 then
      if note.report_decoration_height_sp <= 0 then
        fail(note_path, "reported note lacks report decoration")
      end
      if not note.requires_marker then
        fail(note_path, "reported note lacks marker")
      end
    end
    if not target_index_is_null then
      local target_page = pages_by_index[note.target_shipout_index]
      local safe_rect = target_page.safe_rect
      if note.target_y_sp < safe_rect.top_sp then
        fail(note_path .. ".target_y_sp", "starts above safe rectangle")
      end
      if note.target_y_sp + note.effective_height_sp > safe_rect.bottom_sp then
        fail(note_path .. ".target_y_sp", "ends below safe rectangle")
      end
      if note.width_sp > safe_rect.right_sp - safe_rect.left_sp then
        fail(note_path .. ".width_sp", "wider than safe rectangle")
      end
    end

    local native, carry, placed, reported = expected_memberships(note)
    local expected = {
      native_note_ids = native,
      carry_in_note_ids = carry,
      placed_note_ids = placed,
      reported_note_ids = reported,
    }
    for field, expected_pages in next, expected do
      if not sets_equal(memberships[field][note.id], expected_pages) then
        fail(note_path, "incoherent " .. field)
      end
    end
  end
  if require_complete then
    validate_stable_geometry(layout.pages, notes_by_id)
  end
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
  if json_container_type(array) ~= "array" then
    fail("solver", "internal array copy received a non-array")
  end
  return setmetatable({}, { __nexus_json_type = "array" })
end

local function skip_obstacles(y_sp, height_sp, left_sp, right_sp, obstacles)
  local candidate = y_sp
  local changed = true
  while changed do
    changed = false
    for _, obstacle in ipairs(obstacles) do
      local bottom = candidate + height_sp
      local horizontal_intersection = left_sp < obstacle.right_sp
        and right_sp > obstacle.left_sp
      if horizontal_intersection
          and candidate < obstacle.bottom_sp and bottom > obstacle.top_sp then
        candidate = obstacle.bottom_sp + GAP_SP
        changed = true
      end
    end
  end
  return candidate
end

local function longest_fitting_prefix(notes, safe_bottom_sp)
  local keep = 0
  for index, note in ipairs(notes) do
    if note.target_y_sp + note.effective_height_sp <= safe_bottom_sp then
      keep = index
    else
      break
    end
  end
  return keep
end

local function effective_height(note)
  if note.report_depth > 0 then
    return note.base_height_sp + note.report_decoration_height_sp
  end
  return note.base_height_sp
end

local function sort_note_ids_by_order(note_ids, notes_by_id)
  table.sort(note_ids, function(first_id, second_id)
    return order_less(notes_by_id[first_id], notes_by_id[second_id])
  end)
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
  local minimum_target_by_id = {}
  for _, note in ipairs(result.notes) do
    notes_by_id[note.id] = note
    if json_container_type(note.target_shipout_index) == "null" then
      minimum_target_by_id[note.id] = note.origin_shipout_index
    else
      minimum_target_by_id[note.id] = note.target_shipout_index
    end
    note.effective_height_sp = effective_height(note)
  end

  local incoming_by_page = {}
  for page_index = 1, #result.pages do
    incoming_by_page[page_index] = {}
  end

  for page_index, page in ipairs(result.pages) do
    local cursor = page.safe_rect.top_sp
    local placed_ids = new_array_like(page.placed_note_ids)
    local reported_ids = new_array_like(page.reported_note_ids)
    local carry_ids = new_array_like(page.carry_in_note_ids)
    local carry = incoming_by_page[page_index]
    table.sort(carry, order_less)
    for _, note in ipairs(carry) do
      carry_ids[#carry_ids + 1] = note.id
    end
    sort_note_ids_by_order(carry_ids, notes_by_id)
    page.carry_in_note_ids = carry_ids

    local native = {}
    for _, note_id in ipairs(page.native_note_ids) do
      native[#native + 1] = notes_by_id[note_id]
    end
    table.sort(native, note_less)
    page.native_note_ids = new_array_like(page.native_note_ids)
    for _, note in ipairs(native) do
      page.native_note_ids[#page.native_note_ids + 1] = note.id
    end

    local candidates = {}
    for _, note in ipairs(carry) do
      candidates[#candidates + 1] = { note = note, is_carry = true }
    end
    for _, note in ipairs(native) do
      candidates[#candidates + 1] = { note = note, is_carry = false }
    end

    local placements = {}
    local forced_suffix = false
    for _, candidate in ipairs(candidates) do
      local note = candidate.note
      local y_sp
      if forced_suffix or minimum_target_by_id[note.id] > page.shipout_index then
        forced_suffix = true
        y_sp = page.safe_rect.bottom_sp + 1
      else
        y_sp = cursor
        if not candidate.is_carry then
          y_sp = math.max(note.origin_y_sp, y_sp)
        end
        local note_left_sp = page.safe_rect.left_sp
        local note_right_sp = note_left_sp + note.width_sp
        y_sp = skip_obstacles(
          y_sp,
          note.effective_height_sp,
          note_left_sp,
          note_right_sp,
          page.obstacles
        )
        cursor = y_sp + note.effective_height_sp + GAP_SP
      end
      placements[#placements + 1] = {
        note = note,
        target_y_sp = y_sp,
        effective_height_sp = note.effective_height_sp,
      }
    end

    local keep = longest_fitting_prefix(placements, page.safe_rect.bottom_sp)
    for index = 1, keep do
      local placement = placements[index]
      local note = placement.note
      note.target_shipout_index = page.shipout_index
      note.target_y_sp = placement.target_y_sp
      note.report_depth = page.shipout_index - note.origin_shipout_index
      note.effective_height_sp = effective_height(note)
      placed_ids[#placed_ids + 1] = note.id
    end

    if keep < #placements then
      if page_index == #result.pages then
        local note = placements[keep + 1].note
        fail(
          "result.notes[" .. note.id .. "].target_y_sp",
          "margin-report-impossible: no following page"
        )
      end
      local next_incoming = incoming_by_page[page_index + 1]
      for index = keep + 1, #placements do
        local note = placements[index].note
        reported_ids[#reported_ids + 1] = note.id
        next_incoming[#next_incoming + 1] = note
        if json_container_type(note.target_shipout_index) == "null"
            or note.target_shipout_index <= page.shipout_index then
          note.target_shipout_index = page.shipout_index + 1
          note.report_depth = note.report_depth + 1
        end
        note.target_y_sp = page.safe_rect.top_sp
        note.requires_marker = true
        note.effective_height_sp = effective_height(note)
      end
    end
    page.placed_note_ids = placed_ids
    sort_note_ids_by_order(reported_ids, notes_by_id)
    page.reported_note_ids = reported_ids
  end
  validate_layout(result, "result")
  return result
end

return M
