return {
  on_attach = function(client, bufnr)
    -- When biome is used, disable jsonls's formatting.
    if require("eyal.utils").hasfile({ "biome.json", "biome.jsonc" }) then
      client.server_capabilities.documentFormattingProvider = false
      client.server_capabilities.documentRangeFormattingProvider = false
    end

    require("eyal.lsp-utils").on_attach(client, bufnr)
  end,
}
