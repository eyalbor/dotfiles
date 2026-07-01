# Eyal's dotfiles

Forked from [elentok/dotfiles](https://github.com/elentok/dotfiles).

To install run:

```bash
curl -L https://github.com/eyalbor/dotfiles/raw/main/online_install.sh | bash
```

By default it will clone the repository from "<https://github.com/eyalbor/dotfiles>". To use SSH run
this:

```bash
curl -L https://github.com/eyalbor/dotfiles/raw/main/online_install.sh | bash -s use-ssh
```

## Documentation

- [keys.md](docs/keys.md) - a cheatsheet of all of my vim keybindings (can be accessed from the
  command line using the `k` command)
- [help.md](docs/help.md) - a cheatsheet of useful commands (can be accessed from the command line
  using the `h` or `h {query}` commands)
- [commands.md](docs/commands.md) - a cheatsheet of of my custom shell scripts

### Git

Use `~/.dotlocal/gitconfig`:

```gitconfig
[user]
  name = Eyal Borovsky
  email = you@gmail.com
[github]
  user = eyalbor
```

Personal name and email are not stored in this repo — keep them in `~/.dotlocal/gitconfig` only.
