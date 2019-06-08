import os
import discord
import random
from discord.ext import commands

BOT_PREFIX = os.environ['prefix']
TOKEN = os.environ['token']
bot = commands.Bot(command_prefix=BOT_PREFIX)

# TODO implementar mostrar fila e ggez
# TODO (modo de fila rapida ou normal (FT2 ou FT3) conforme tamanho da fila)
# TODO (avisar quando jogador fez volta inteira na fila)
# TODO limite de rodadas
# TODO caixa de bombom
# TODO streak functionality - integracao com twitch?

BOMBONS = ["Prestigio", "Alpino", "Suflair", "Classic", "Galak", "Lollo", "Charge", "Sensação", "Chokito", "Negresco", "Smash"]


class QManager:
    def __init__(self):
        self.queue = []
        self.last_winner = None

        # statistics
        self.victimList = {}
        self.winLog = {}

    # -- DATA HANDLING FUNCTIONS --

    # returns relative position of entering player or the position he is already in
    # TODO resolve async dependencies
    def add_player(self, context):
        member = context.author
        if member in self.queue:
            return - (self.queue.index(member) + 1)
        self.queue.append(member)
        if self.active_queue():
            return self.queue.index(member) - 1
        else:
            if len(self.queue) == 2:
                self.call_next_match(context)
            return 0

    def remove_player(self, context):
        member = context.author
        if member not in self.queue:
            return False
        else:
            player_pos = self.queue.index(member)
            self.queue.remove(member)
            if player_pos < 2 and len(self.queue) > 1:
                self.call_next_match(context)
        return True

    def skip_turn(self, context):
        member = context.author
        if member not in self.queue[:2] or not self.active_queue():
            return False
        else:
            if member not in self.queue[:2]:
                self.queue.remove(member)
                self.queue.append(member)
            else:
                self.queue.remove(member)
                self.queue.append(member)
                self.call_next_match(context)
            return True

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

    def resolve_match(self, context):
        winner = context.author
        if len(self.queue) < 3:
            return
        active_players = self.queue[:2]
        if winner in active_players:
            self.last_winner = winner
            pos = self.queue.index(winner)
            if pos == 1:  # winner is second in line
                loser = self.queue.pop(0)
            else:  # winner is first in line
                loser = self.queue.pop(1)

            self.queue.append(loser)
            self.call_next_match(context)
            # TODO statistics
            return
        else:
            return

    def active_players(self):
        return self.queue[0:2]

    def show_queue(self):
        return [member.name for member in self.queue]

    def player_count(self):
        return len(self.queue)

    def active_queue(self):
        return len(self.queue) > 2

    def reset(self):
        pass  # TODO resetar dados

    def call_next_match(self, context):
        context.send(f'Proxima partida: {self.queue[0].mention} vs {self.queue[1].mention}')


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
    value = QUEUE.add_player(ctx)
    if value > 0:
        await ctx.send("{}  foi adicionado a fila na posicao {}".format(ctx.author.name,value))
    elif value < 0:
        await ctx.send("{} ja esta na fila na posicao {}".format(ctx.author.name, abs(value)))
    else:
        await ctx.send("{} entrou pra porrada".format(ctx.author.name))


@bot.command(name="sair")
# @is_channel("eventos")
async def leave_queue(ctx):
    if QUEUE.remove_player(ctx):
        await ctx.send(ctx.author.name + " removido da fila")
    else:
        await ctx.send(f'Jogador nao consta na fila')


@bot.command(name="pular")
# @is_channel("eventos")
async def skip_turn(ctx):
    if QUEUE.skip_turn(ctx):
        await ctx.send(ctx.author.name + " foi para o fim da fila")
    else:
        await ctx.send(f'Nao foi possivel completar sua chamada, verifique o numero discado ou consulte informacoes DDD')


@bot.command(name="ggez")
# @is_channel("eventos")
async def ggez(ctx):
    QUEUE.resolve_match(ctx)


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
