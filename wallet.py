from discord.ext import commands
import discord
import json
import os

class Banking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.balances_file = "balances.json"
        self.load_balances()

    def load_balances(self):
        if os.path.exists(self.balances_file):
            with open(self.balances_file, "r") as f:
                self.pd = json.load(f)
        else:
            self.pd = {}
        if 'lsr' not in self.pd:
            self.pd['lsr'] = {}
        self.balances = self.pd['lsr']

    def save_balances(self):
        with open(self.balances_file, "w") as f:
            json.dump(self.pd, f, indent = 2)

    @commands.command()
    async def change(self, ctx, amount: int, member: discord.Member = None):
        role = discord.utils.find(lambda r: r.name == 'director', ctx.message.guild.roles)
        if role not in ctx.author.roles:
            await ctx.message.reply('yeah. right. as if i let you')
            return
        member = member or ctx.author
        mid = member.id
        await ctx.send(self._change(mid, amount))

    def _change(self, mid, amount):
        mid = str(mid)
        if mid not in self.balances:
            self.balances[mid] = 0
        self.balances[mid] += amount
        self.save_balances()
        return f"<@{mid}>'s balance is now {self.balances[mid]:,}."

    @commands.command()
    async def balance(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        if str(member.id) in self.balances:
            await ctx.send(f"{member.mention}, your balance is {self.balances[str(member.id)]:,}.")
        else:
            await ctx.send(f"{member.mention}, you do not have a balance.")

    @commands.command()
    async def mywallet(self, ctx, member: discord.Member = None, amount: int = None):
        try:
            if 'users' not in self.pd:
                self.pd['users'] = {}
            ud = self.pd['users']
            aid = str(ctx.author.id)
            if amount and member:
                if member.id == 602676777399091230:
                    member = self.bot.get_user(139179662369751041)
                self.change_mywallet(ud, aid, member.id, amount)
                self.save_balances()
                await ctx.send(f"{member.mention}'s balance is now {ud[aid][str(member.id)]:,}.")
            else:
                if aid not in ud:
                    ud[aid] = {}
                w = ud[aid]
                b = [(k, v) for k, v in w.items() if v != 0]
                sorted_balances = sorted(b, key=lambda x: x[1], reverse=True)
                leaderboard = "\n".join([f"{self.bot.get_user(int(member_id)).mention}: {balance:,}" for member_id, balance in sorted_balances])
                await ctx.send(f"your wallet:\n{leaderboard}\nuse `.mywallet <user> <amount>` to add records")
        except Exception as e:
            await ctx.send(str(e))

    def change_mywallet(self, ud, aid, mid, amount, first = True):
        aid = str(aid)
        mid = str(mid)
        if aid not in ud:
            ud[aid] = {}
        w = ud[aid]
        if str(mid) not in w:
            w[str(mid)] = 0
        w[str(mid)] += amount
        if first:
            self.change_mywallet(ud, mid, aid, -amount, False)

    @commands.command()
    async def wallet(self, ctx):
        b = [(k, v) for k, v in self.balances.items() if v > 0]
#        sorted_balances = sorted(self.balances.items(), key=lambda x: x[1], reverse=True)
        sorted_balances = sorted(b, key=lambda x: x[1], reverse=True)
        leaderboard = "\n".join([f"{self.bot.get_user(int(member_id)).mention}: {balance:,}" for member_id, balance in sorted_balances])
        await ctx.send(f"wallet:\n{leaderboard}")

async def setup(bot):
    await bot.add_cog(Banking(bot))
