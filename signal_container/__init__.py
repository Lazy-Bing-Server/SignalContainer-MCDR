import re

from mcdreforged.api.all import *
from typing import Optional, List, Any

from signal_container.config import Config
from signal_container.utils import ntr, rtr, named_thread, DEBUG
from signal_container.generic import MessageText


psi = ServerInterface.psi()
config = Config.load()


def help_msg(source: CommandSource):
    def htr(translation_key: str, *args, _lb_htr_prefixes: Optional[List[str]] = None,
            **kwargs) -> RTextMCDRTranslation:
        def __get_regex_result(line: str):
            pattern = r'(?<=§7){}[\S ]*?(?=§)'
            for prefix_tuple in _lb_htr_prefixes:
                for prefix in prefix_tuple:
                    result = re.search(pattern.format(prefix), line)
                    if result is not None:
                        return result
            return None

        def __htr(key: str, *inner_args, **inner_kwargs) -> MessageText:
            original, processed = psi.tr(key, *inner_args, **inner_kwargs), []
            if not isinstance(original, str):
                return key
            for line in original.splitlines():
                result = __get_regex_result(line)
                if result is not None:
                    command = result.group() + ' '
                    processed.append(RText(line).c(RAction.suggest_command, command).h(
                        rtr(f'help.suggest', command)))
                else:
                    processed.append(line)
            return RTextBase.join('\n', processed)

        return RTextMCDRTranslation(translation_key, *args, **kwargs).set_translator(__htr)

    source.reply(
        htr(
            f"{psi.get_self_metadata().id}.help.detailed", id=psi.get_self_metadata().name, ver=str(psi.get_self_metadata().version),
            _lb_htr_prefixes=[config.prefix], pre=config.prefix
        )
    )


@named_thread
def get_signal_container(source: PlayerCommandSource, signal: int):
    container = config.get_target_container(source.player)
    psi.logger.info(container.get_item_stack(signal))
    command = container.get_give_command(source.player, signal)
    psi.execute(command)
    source.reply(rtr("get.obtained", signal=signal, player=source.player))


@named_thread
def give_signal_container(source: PlayerCommandSource, signal: int, target_player: str, use_executors_pref: bool = False):
    container = config.get_target_container(source.player if use_executors_pref else target_player)
    command = container.get_give_command(target_player, signal)
    psi.execute(command)
    source.reply(rtr("get.obtained", signal=signal, player=target_player))


@named_thread
def set_preference(source: PlayerCommandSource, key: str, value: Any):
    if config.set_personal_preference(source, key, value):
        return source.reply(rtr('set.local', k=str(key), v=str(value)))
    source.reply(rtr('set.failed', k=str(key), v=str(value)))


@named_thread
def set_global_config(source: CommandSource, key: str, value: Any):
    if config.set_global(source, key, value):
        return source.reply(rtr('set.global', k=str(key), v=str(value)))
    source.reply(rtr('set.failed', k=str(key), v=str(value)))


@named_thread
def info_config(source: CommandSource, key: str):
    source.reply(rtr(f'info.{key}.name').set_styles(RStyle.bold).set_color(RColor.aqua) + f"(§7{key}§r)")
    source.reply(rtr(f'info.{key}.desc'))
    if isinstance(source, PlayerCommandSource) and config.preferences.get(source.player):
        source.reply(
            rtr('info.local_value', str(getattr(config.preferences.get(source.player), key))).set_hover_text(
                "Edit preferred config item {}"
            ).set_click_event(
                RAction.suggest_command, f"{config.prefix} cfg set {key} "
            )
        )
    gl_value = rtr('info.global_value', str(getattr(config.global_config, key)))
    if source.has_permission(config.permission.set_global):
        gl_value.set_hover_text("Edit global config item {}").set_click_event(
                RAction.suggest_command, f"{config.prefix} cfg set-global {key} "
            )
    source.reply(gl_value)


@named_thread
def list_config(source: CommandSource):
    source.reply(rtr('list').set_styles(RStyle.bold))
    for key in config.get_key_lists():
        source.reply(
            (
                rtr(f'info.{key}.name').set_styles(RStyle.bold).set_color(RColor.aqua) + f"(§7{key}§r) [>]"
            ).set_click_event(
                RAction.run_command, f"{config.prefix} cfg info {key}"
            )
        )


def build_command():
    def permed_literal(literal: str):
        permission_level: int = config.permission.serialize().get(literal.replace("-", "_"), 0)
        return Literal(literal).requires(
            lambda src, ctx: src.get_permission_level() >= permission_level,
            lambda: rtr("error.perm_denied")
        )

    def signal_integer(arg_name: str):
        def signal_validate(src: CommandSource, ctx: CommandContext):
            return ctx[arg_name] > 0
        return Integer(arg_name).requires(signal_validate, lambda: rtr("error.requires_positive"))

    prefix = config.prefix
    root_builder = SimpleCommandBuilder()
    root_builder.command(prefix, help_msg)
    root_builder.command(f"{prefix} get <signal>", lambda src, ctx: get_signal_container(src, ctx['signal']))
    root_builder.literal('get', permed_literal)
    root_builder.arg('signal', signal_integer).requires(lambda src: src.is_player, lambda: rtr("error.not_a_player"))
    root_builder.command(
        f"{prefix} give <player> <signal_>",
        lambda src, ctx: give_signal_container(src, ctx['signal_'], ctx['player'])
    )
    root_builder.literal('give', permed_literal)
    root_builder.arg("player", QuotableText)
    root_builder.arg('signal_', signal_integer).post_process(
        lambda node: node.then(
            Literal(["--use-my-pref", '-U']).requires(lambda src: src.is_player, lambda: rtr("error.not_a_player")).runs(
                lambda src, ctx: give_signal_container(src, ctx['signal_'], ctx['player'], use_executors_pref=True)
            )
        )
    )
    root_builder.command(
        f"{prefix} cfg set <key> <value>", lambda src, ctx: set_preference(src, ctx['key'], ctx['value'])
    )
    root_builder.literal('set', permed_literal).requires(lambda src: src.is_player, lambda: rtr("error.not_a_player"))
    root_builder.command(
        f"{prefix} cfg set-global <key> <value>", lambda src, ctx: set_global_config(src, ctx['key'], ctx['value'])
    )
    root_builder.literal('set-global', permed_literal)
    root_builder.command(f"{prefix} cfg info <key>", lambda src, ctx: info_config(src, ctx['key']))
    root_builder.arg('key', QuotableText).requires(lambda src, ctx: ctx['key'] in config.get_key_lists())
    root_builder.arg('value', QuotableText)
    root_builder.command(f"{prefix} cfg list", list_config)
    root_builder.register(psi)


def on_load(server: PluginServerInterface, prev_module):
    build_command()
    server.register_help_message(config.prefix, rtr('help.mcdr'))

