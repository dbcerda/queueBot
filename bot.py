import os
import discord
import random
from discord.ext import commands

BOT_PREFIX = os.environ['prefix']
TOKEN = os.environ['token']
bot = commands.Bot(command_prefix=BOT_PREFIX)

# TODO winstreak - integracao com twitch?
# TODO estatisticas (longest winstreak, maior numero de vitorias, lista de quem cada jogador venceu)
# TODO avisar quando jogador fez volta inteira na fila
# TODO guardar IP dos jogadores e passar no call_next_match()
# TODO limite de rodadas por evento
# TODO caixa de bombom
# TODO funcao para reverter o ultimo vencedor caso haja algum troll/equivoco
# TODO lista negra de usuarios que trollam

BOMBONS = ["Prestigio", "Alpino", "Suflair", "Classic", "Galak", "Lollo", "Charge", "Sensação", "Chokito", "Negresco", "Smash"]


class QManager:
    def __init__(self):
        self.queue = []
        self.last_winner = None

        # statistics
        self.victimList = {}
        self.winLog = {}

    # -- DATA HANDLING FUNCTIONS --

    async def add_player(self, context):
        member = context.author
        if member in self.queue:
            await context.send(f'{member.name} ja esta na fila na posicao {self.queue.index(member) + 1}')
        else:
            self.queue.append(member)
            if self.number_of_players() == 2:
                await self.call_next_match(context)
            elif self.active_queue():
                await context.send(f"{member.name} foi adicionado a fila na posicao {self.queue.index(member) - 1}")
            else:
                await context.send(f"{member.name} esta esperando desafiantes")

    async def remove_player(self, context):
        member = context.author
        if member not in self.queue:
            await context.send(f"{member.name} nao esta na fila")
        else:
            player_pos = self.queue.index(member)
            self.queue.remove(member)
            await context.send(f"{member.name} correu que nem um franguinho")
            if player_pos < 2 and self.number_of_players() > 1:
                await self.call_next_match(context)

    async def skip_turn(self, context):
        member = context.author
        if member not in self.queue or not self.active_queue():
            await context.send(f"Nao")
        elif member in self.first_players():
            self.queue.remove(member)
            self.queue.append(member)
            await self.call_next_match(context)
            await context.send(f"{member.name} foi pro fim da fila")

    def force_skip(self, context, target):
        self.queue.remove(target)
        self.queue.append(target)
        # TODO se admin precisar pular um usuario
        return

    def force_remove(self, context, target):
        self.queue.remove(target)
        self.queue.append(target)
        # TODO se admin precisar remover um usuario
        return

    async def resolve_match(self, context):
        winner = context.author
        if winner in self.first_players():
            self.last_winner = winner
            pos = self.queue.index(winner)
            if pos == 1:  # winner is second in line
                loser = self.queue.pop(0)
            else:  # winner is first in line
                loser = self.queue.pop(1)

            self.queue.append(loser)
            await self.call_next_match(context)
            # TODO statistics
        else:
            await context.send(f"Nao mente, rapaz!")

    def first_players(self):
        return self.queue[0:2]

    def show_queue(self):
        return [member.name for member in self.queue]

    def number_of_players(self):
        return len(self.queue)

    def active_queue(self):
        return len(self.queue) > 2

    def reset(self):
        pass  # TODO resetar dados

    async def call_next_match(self, context):
        await context.send(f'Proxima partida: {self.queue[0].mention} vs {self.queue[1].mention} - {self.rule_set()}')

    def rule_set(self):
        if len(self.queue) > 4:
            return "FT2"
        else:
            return "FT3"


QUEUE = QManager()

# -- CUSTOM CHECKER --


def is_channel(channel_name):
    def predicate(ctx):
        return ctx.message.channel.name == channel_name
    return commands.check(predicate)


# -- BOT EVENTS --

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="!comandos"))


# -- BOT COMMANDS --

@bot.command(name="ativar")
@commands.has_role("Moderador")
async def open_queue(ctx):
    await ctx.send("" + "Teste ativar")


@bot.command(name="desativar")
@commands.has_role("Moderador")
async def close_queue(ctx):
    await ctx.send("" + "Teste desativar")


@bot.command(name="entrar")
# @is_channel("eventos")
async def join_queue(ctx):
    await QUEUE.add_player(ctx)


@bot.command(name="sair")
# @is_channel("eventos")
async def leave_queue(ctx):
    await QUEUE.remove_player(ctx)


@bot.command(name="pular")
# @is_channel("eventos")
async def skip_turn(ctx):
    await QUEUE.skip_turn(ctx)


@bot.command(name="ggez")
# @is_channel("eventos")
async def ggez(ctx):
    await QUEUE.resolve_match(ctx)


@bot.command(name="fila")
# @is_channel("eventos")
async def show_queue(ctx):
    await ctx.send(QUEUE.show_queue())


@bot.command(name="comandos")
async def show_commands(ctx):
    await ctx.send("" + "[moeda], [d20], [fila], [ggez], [pular], [entrar], [sair]")


@bot.command(name="moeda")
async def coin_toss(ctx):
    answer = random.choice(["cara", "coroa"])
    await ctx.send(ctx.author.mention + " jogou uma moeda e deu: " + answer)


@bot.command(name="d20")
async def d20_roll(ctx):
    answer = random.randint(1, 20)
    await ctx.send(f'{ctx.author.mention} jogou um dado e caiu: {answer}')


bot.run(TOKEN)
