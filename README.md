Signal Container
-----

**English** | [中文(Chinese)](README_zh.md)

A MCDR plugin helps you get container with required signal level


# Basic Command

`!!sig` Get help message

`!!sig get <signal>` Get container that output specified redstone signal level

`!!sig give <player> <signal> [-U]` Give someone the required container, add `-U` to use your own preference to generate the container property instead of the target player's

# Customize preferences

Some config items can be modified in game, and have global and personal values

`!!sig cfg list` List all config items

`!!sig cfg info <key>` Get config item info

`!!sig cfg set <key> <value>` Set config item value for yourself

`!!sig cfg set-global <key> <value>` Set config item globally

Available in-game config items:

`container_item`: Container item ID, default to barrel (`minecraft:barrel`), this only specify the id, the `max_slots` should be checked if your container has different slots count

`max_slots`: Slots count that the container specified has

`allow_overstack_under_15`: If this enabled, container can be filled with overstacked unstackable item in any situation

`unstackable_fillings`: Set the unstackable item that will be used to fill the container

`stackable_fillings`: Set the stackable item that will be used to fill the container

# Plugin config

Plugin config locates in `config/signal_container/config.json`

Plugin config items:

`permission`: If a player has lower permission level than the value in this map, the player can't execute the corresponding command

`prefix`: Command prefix, default to `!!sig`, that means all the `!!sig` in the commands mentioned above can be replaced with this config value
