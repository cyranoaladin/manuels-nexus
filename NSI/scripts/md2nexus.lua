-- md2nexus.lua : filtre pandoc pour transposer les séquences NSI (Markdown)
-- vers les macros de la charte Nexus. Sortie = .candidate.tex à retravailler
-- par l'agent restructurateur, jamais du contenu final.

local function raw(tex) return pandoc.RawBlock("latex", tex) end

-- Blocs de code -> environnement python (ou console si le contenu ressemble à une session)
function CodeBlock(el)
  local lang = el.classes[1] or ""
  local body = el.text
  if body:match("^>>>") or body:match("\n>>>") then
    return raw("\\begin{console}\n" .. body .. "\n\\end{console}")
  end
  if lang == "python" or lang == "py" or lang == "" then
    return raw("\\begin{python}\n" .. body .. "\n\\end{python}")
  end
  return raw("\\begin{verbatim}\n" .. body .. "\n\\end{verbatim}")
end

-- Admonitions / blockquotes typées -> encadrés Nexus
function BlockQuote(el)
  local first = pandoc.utils.stringify(el.content[1] or "")
  local map = {
    ["^%s*[Dd][ée]finition"] = {"\\definition{", "}"},
    ["^%s*[Pp]ropri[ée]t[ée]"] = {"\\propriete{", "}"},
    ["^%s*[Aa]ttention"] = {"\\erreurFrequente{", "}"},
    ["^%s*[Ee]rreur"] = {"\\erreurFrequente{", "}"},
    ["^%s*[Rr]emarque"] = {"\\margeAppui{", "}"},
    ["^%s*[Ee]xemple"] = {"\\exemple{", "}"},
  }
  for pat, wrap in pairs(map) do
    if first:match(pat) then
      local inner = {}
      for i = 2, #el.content do table.insert(inner, el.content[i]) end
      if #inner == 0 then inner = el.content end
      local body = pandoc.write(pandoc.Pandoc(inner), "latex")
      return raw(wrap[1] .. body .. wrap[2])
    end
  end
  return el
end

-- Titres : niveau 1 des fichiers de séquence -> section ; le reste descend d'un cran
function Header(el)
  if el.level == 1 then
    return raw("\\section{" .. pandoc.utils.stringify(el.content) .. "}")
  elseif el.level == 2 then
    return raw("\\subsection{" .. pandoc.utils.stringify(el.content) .. "}")
  end
  return raw("\\subsubsection{" .. pandoc.utils.stringify(el.content) .. "}")
end

-- Marqueur explicite pour l'agent : tout HTML brut est signalé
function RawBlock(el)
  if el.format == "html" then
    return raw("% TODO-RESTRUCTURATION : bloc HTML source à transposer manuellement\n% " ..
               el.text:gsub("\n", "\n% "))
  end
  return el
end
