local M = {}

local SAFE_INTEGER = 9007199254740991
local ARRAY_MT = { __nexus_json_type = "array" }
local OBJECT_MT = { __nexus_json_type = "object" }
local NULL_MT = { __nexus_json_type = "null" }

M.JSON_NULL = setmetatable({}, NULL_MT)

function M.new_array()
  return setmetatable({}, ARRAY_MT)
end

function M.new_object()
  return setmetatable({}, OBJECT_MT)
end

function M.container_type(value)
  local metatable = type(value) == "table" and getmetatable(value) or nil
  return metatable and metatable.__nexus_json_type or nil
end

local function fail(kind, position, message)
  if position then
    error(string.format("JSON %s error at byte %d: %s", kind, position, message), 0)
  end
  error(string.format("JSON %s error: %s", kind, message), 0)
end

local function is_continuation(byte)
  return byte and byte >= 0x80 and byte <= 0xBF
end

local function utf8_sequence_end(text, position, kind)
  local first = text:byte(position)
  if not first then
    fail(kind, position, "unexpected end of UTF-8 sequence")
  end
  if first < 0x80 then
    return position + 1
  end

  local second = text:byte(position + 1)
  if first >= 0xC2 and first <= 0xDF then
    if not is_continuation(second) then
      fail(kind, position, "invalid UTF-8 continuation byte")
    end
    return position + 2
  end

  local third = text:byte(position + 2)
  if first == 0xE0 then
    if not second or second < 0xA0 or second > 0xBF or not is_continuation(third) then
      fail(kind, position, "invalid or overlong UTF-8 sequence")
    end
    return position + 3
  end
  if first >= 0xE1 and first <= 0xEC then
    if not is_continuation(second) or not is_continuation(third) then
      fail(kind, position, "invalid UTF-8 continuation byte")
    end
    return position + 3
  end
  if first == 0xED then
    if not second or second < 0x80 or second > 0x9F or not is_continuation(third) then
      fail(kind, position, "UTF-8 surrogate or invalid sequence")
    end
    return position + 3
  end
  if first >= 0xEE and first <= 0xEF then
    if not is_continuation(second) or not is_continuation(third) then
      fail(kind, position, "invalid UTF-8 continuation byte")
    end
    return position + 3
  end

  local fourth = text:byte(position + 3)
  if first == 0xF0 then
    if not second or second < 0x90 or second > 0xBF
        or not is_continuation(third) or not is_continuation(fourth) then
      fail(kind, position, "invalid or overlong UTF-8 sequence")
    end
    return position + 4
  end
  if first >= 0xF1 and first <= 0xF3 then
    if not is_continuation(second) or not is_continuation(third)
        or not is_continuation(fourth) then
      fail(kind, position, "invalid UTF-8 continuation byte")
    end
    return position + 4
  end
  if first == 0xF4 then
    if not second or second < 0x80 or second > 0x8F
        or not is_continuation(third) or not is_continuation(fourth) then
      fail(kind, position, "UTF-8 code point is above U+10FFFF")
    end
    return position + 4
  end
  fail(kind, position, "invalid UTF-8 leading byte")
end

local function utf8_from_codepoint(codepoint)
  if codepoint <= 0x7F then
    return string.char(codepoint)
  end
  if codepoint <= 0x7FF then
    return string.char(
      0xC0 + math.floor(codepoint / 0x40),
      0x80 + codepoint % 0x40
    )
  end
  if codepoint <= 0xFFFF then
    return string.char(
      0xE0 + math.floor(codepoint / 0x1000),
      0x80 + math.floor(codepoint / 0x40) % 0x40,
      0x80 + codepoint % 0x40
    )
  end
  return string.char(
    0xF0 + math.floor(codepoint / 0x40000),
    0x80 + math.floor(codepoint / 0x1000) % 0x40,
    0x80 + math.floor(codepoint / 0x40) % 0x40,
    0x80 + codepoint % 0x40
  )
end

local Parser = {}
Parser.__index = Parser

function Parser:new(text)
  if type(text) ~= "string" then
    fail("decode", nil, "input must be a string")
  end
  return setmetatable({ text = text, length = #text, position = 1 }, self)
end

function Parser:skip_whitespace()
  while self.position <= self.length do
    local byte = self.text:byte(self.position)
    if byte ~= 0x20 and byte ~= 0x09 and byte ~= 0x0A and byte ~= 0x0D then
      break
    end
    self.position = self.position + 1
  end
end

local function hex_value(byte)
  if byte >= 0x30 and byte <= 0x39 then
    return byte - 0x30
  end
  if byte >= 0x41 and byte <= 0x46 then
    return byte - 0x41 + 10
  end
  if byte >= 0x61 and byte <= 0x66 then
    return byte - 0x61 + 10
  end
  return nil
end

function Parser:read_hex4()
  local codepoint = 0
  local start = self.position
  for offset = 0, 3 do
    local byte = self.text:byte(start + offset)
    local value = byte and hex_value(byte) or nil
    if not value then
      fail("decode", start + offset, "expected four hexadecimal digits")
    end
    codepoint = codepoint * 16 + value
  end
  self.position = start + 4
  return codepoint
end

function Parser:parse_string()
  local pieces = {}
  self.position = self.position + 1
  local raw_start = self.position

  while self.position <= self.length do
    local byte = self.text:byte(self.position)
    if byte == 0x22 then
      pieces[#pieces + 1] = self.text:sub(raw_start, self.position - 1)
      self.position = self.position + 1
      return table.concat(pieces)
    end
    if byte == 0x5C then
      pieces[#pieces + 1] = self.text:sub(raw_start, self.position - 1)
      local escape_position = self.position
      self.position = self.position + 1
      local escaped = self.text:byte(self.position)
      if not escaped then
        fail("decode", escape_position, "unterminated escape")
      end
      local simple = {
        [0x22] = '"', [0x5C] = "\\", [0x2F] = "/", [0x62] = "\b",
        [0x66] = "\f", [0x6E] = "\n", [0x72] = "\r", [0x74] = "\t",
      }
      if simple[escaped] then
        pieces[#pieces + 1] = simple[escaped]
        self.position = self.position + 1
      elseif escaped == 0x75 then
        self.position = self.position + 1
        local codepoint = self:read_hex4()
        if codepoint >= 0xD800 and codepoint <= 0xDBFF then
          if self.text:sub(self.position, self.position + 1) ~= "\\u" then
            fail("decode", self.position, "high surrogate lacks a low surrogate")
          end
          self.position = self.position + 2
          local low = self:read_hex4()
          if low < 0xDC00 or low > 0xDFFF then
            fail("decode", self.position - 4, "invalid low surrogate")
          end
          codepoint = 0x10000 + (codepoint - 0xD800) * 0x400 + (low - 0xDC00)
        elseif codepoint >= 0xDC00 and codepoint <= 0xDFFF then
          fail("decode", self.position - 4, "isolated low surrogate")
        end
        pieces[#pieces + 1] = utf8_from_codepoint(codepoint)
      else
        fail("decode", self.position, "invalid escape")
      end
      raw_start = self.position
    elseif byte < 0x20 then
      fail("decode", self.position, "unescaped control character")
    elseif byte < 0x80 then
      self.position = self.position + 1
    else
      self.position = utf8_sequence_end(self.text, self.position, "decode")
    end
  end
  fail("decode", self.position, "unterminated string")
end

function Parser:parse_number()
  local start = self.position
  if self.text:byte(self.position) == 0x2D then
    self.position = self.position + 1
  end
  local first_digit = self.text:byte(self.position)
  if not first_digit or first_digit < 0x30 or first_digit > 0x39 then
    fail("decode", self.position, "expected an integer")
  end
  if first_digit == 0x30 then
    self.position = self.position + 1
    local following = self.text:byte(self.position)
    if following and following >= 0x30 and following <= 0x39 then
      fail("decode", self.position, "leading zero in integer")
    end
  else
    repeat
      self.position = self.position + 1
      first_digit = self.text:byte(self.position)
    until not first_digit or first_digit < 0x30 or first_digit > 0x39
  end
  local following = self.text:byte(self.position)
  if following == 0x2E or following == 0x65 or following == 0x45 then
    fail("decode", self.position, "fractions and exponents are forbidden")
  end
  local token = self.text:sub(start, self.position - 1)
  local number = tonumber(token)
  if not number or math.type(number) ~= "integer"
      or number < -SAFE_INTEGER or number > SAFE_INTEGER then
    fail("decode", start, "integer is outside the safe range")
  end
  return number
end

function Parser:parse_array()
  local result = M.new_array()
  self.position = self.position + 1
  self:skip_whitespace()
  if self.text:byte(self.position) == 0x5D then
    self.position = self.position + 1
    return result
  end
  while true do
    result[#result + 1] = self:parse_value()
    self:skip_whitespace()
    local byte = self.text:byte(self.position)
    if byte == 0x5D then
      self.position = self.position + 1
      return result
    end
    if byte ~= 0x2C then
      fail("decode", self.position, "expected ',' or ']' in array")
    end
    self.position = self.position + 1
    self:skip_whitespace()
  end
end

function Parser:parse_object()
  local result = M.new_object()
  local seen = {}
  self.position = self.position + 1
  self:skip_whitespace()
  if self.text:byte(self.position) == 0x7D then
    self.position = self.position + 1
    return result
  end
  while true do
    if self.text:byte(self.position) ~= 0x22 then
      fail("decode", self.position, "object key must be a string")
    end
    local key = self:parse_string()
    if seen[key] then
      fail("decode", self.position, "duplicate object key " .. key)
    end
    seen[key] = true
    self:skip_whitespace()
    if self.text:byte(self.position) ~= 0x3A then
      fail("decode", self.position, "expected ':' after object key")
    end
    self.position = self.position + 1
    self:skip_whitespace()
    result[key] = self:parse_value()
    self:skip_whitespace()
    local byte = self.text:byte(self.position)
    if byte == 0x7D then
      self.position = self.position + 1
      return result
    end
    if byte ~= 0x2C then
      fail("decode", self.position, "expected ',' or '}' in object")
    end
    self.position = self.position + 1
    self:skip_whitespace()
  end
end

function Parser:parse_value()
  local byte = self.text:byte(self.position)
  if byte == 0x22 then
    return self:parse_string()
  end
  if byte == 0x7B then
    return self:parse_object()
  end
  if byte == 0x5B then
    return self:parse_array()
  end
  if byte == 0x2D or (byte and byte >= 0x30 and byte <= 0x39) then
    return self:parse_number()
  end
  for literal, value in pairs({ ["true"] = true, ["false"] = false, ["null"] = M.JSON_NULL }) do
    if self.text:sub(self.position, self.position + #literal - 1) == literal then
      self.position = self.position + #literal
      return value
    end
  end
  fail("decode", self.position, "expected a JSON value")
end

function M.decode(text)
  local parser = Parser:new(text)
  parser:skip_whitespace()
  local result = parser:parse_value()
  parser:skip_whitespace()
  if parser.position <= parser.length then
    fail("decode", parser.position, "trailing data")
  end
  return result
end

local ESCAPES = {
  [0x08] = "\\b", [0x09] = "\\t", [0x0A] = "\\n", [0x0C] = "\\f",
  [0x0D] = "\\r", [0x22] = '\\"', [0x5C] = "\\\\",
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

local function encode_string(value)
  local pieces = { '"' }
  local position = 1
  while position <= #value do
    local byte = value:byte(position)
    local escaped = ESCAPES[byte]
    if escaped then
      pieces[#pieces + 1] = escaped
      position = position + 1
    elseif byte < 0x20 then
      pieces[#pieces + 1] = string.format("\\u%04x", byte)
      position = position + 1
    elseif byte < 0x80 then
      pieces[#pieces + 1] = string.char(byte)
      position = position + 1
    else
      local following = utf8_sequence_end(value, position, "encode")
      pieces[#pieces + 1] = value:sub(position, following - 1)
      position = following
    end
  end
  pieces[#pieces + 1] = '"'
  return table.concat(pieces)
end

local function encode_value(value, active)
  local value_type = type(value)
  if value_type == "string" then
    return encode_string(value)
  end
  if value_type == "boolean" then
    return value and "true" or "false"
  end
  if value_type == "number" then
    if math.type(value) ~= "integer"
        or value < -SAFE_INTEGER or value > SAFE_INTEGER then
      fail("encode", nil, "numbers must be safe integers")
    end
    return string.format("%d", value)
  end
  if value_type ~= "table" then
    fail("encode", nil, "unsupported value type " .. value_type)
  end

  local container_type = M.container_type(value)
  if container_type == "null" then
    return "null"
  end
  if container_type ~= "array" and container_type ~= "object" then
    fail("encode", nil, "table is not tagged as a JSON array or object")
  end
  if active[value] then
    fail("encode", nil, "cyclic table")
  end
  active[value] = true

  local pieces = {}
  if container_type == "array" then
    local count = 0
    local maximum = 0
    for key in next, value do
      if type(key) ~= "number" or math.type(key) ~= "integer" or key < 1 then
        fail("encode", nil, "JSON array has a non-positive-integer key")
      end
      count = count + 1
      maximum = math.max(maximum, key)
    end
    if count ~= maximum then
      fail("encode", nil, "JSON array has a hole")
    end
    for index = 1, maximum do
      pieces[index] = encode_value(value[index], active)
    end
    active[value] = nil
    return "[" .. table.concat(pieces, ",") .. "]"
  end

  local keys = {}
  for key in next, value do
    if type(key) ~= "string" then
      fail("encode", nil, "JSON object key must be a string")
    end
    keys[#keys + 1] = key
  end
  table.sort(keys, bytewise_less)
  for index, key in ipairs(keys) do
    pieces[index] = encode_string(key) .. ":" .. encode_value(value[key], active)
  end
  active[value] = nil
  return "{" .. table.concat(pieces, ",") .. "}"
end

function M.encode(value)
  return encode_value(value, {})
end

return M
