vim.loader.enable()
require("config.settings")
require("config.pack")
require("config.keymaps")
require("config.lsp")
require("config.colors")

require("eyal.dotplugins")
require("eyal.slack")
if vim.g.neovide then require("eyal.neovide") end
