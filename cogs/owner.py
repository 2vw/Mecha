import voltage, asyncio, random, time, psutil, pymongo, json, datetime, io, contextlib, requests, string, os, sys
from bson.son import SON
from voltage.ext import commands
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

with open("json/config.json", "r") as f:
    config = json.load(f)

DBclient = MongoClient(config["MONGOURI"])

db = DBclient["beta"]
userdb = db["users"]
serverdb = db["servers"]

def setup(client) -> commands.Cog:
  owner = commands.Cog(
    "Owner",
    "Some commands for testing."
  )
  
  @owner.command()
  async def statz(ctx):
    """Different from normal stats, the normal one shows the stats of the bot, this one shows complex stats. Like CPU usage and whatnot."""
    if ctx.author.id == "01FZB2QAPRVT8PVMF11480GRCD":
      with open("json/data.json", "r") as f:
        uptime = json.load(f)['uptime']
      embed = voltage.SendableEmbed(
        title=f"{client.user.name}'s Stats",
        description=f"""
  ## Computer Based Stats
  > CPU Usage: `{psutil.cpu_percent()}%`
  > RAM Usage: `{psutil.virtual_memory().percent}%`
  > Disk Usage: `{psutil.disk_usage('/').percent}%`
        
  ## Bot Stats
  > Servers: `{len(client.servers)}`
  > Users: `{len(client.users)}`
  > Uptime: `{str(datetime.timedelta(seconds=int(round(time.time() - uptime))))}s`
        """,
        colour="#44ff44"
      ) # fix the uptime formatting at some point i swear to god
      await ctx.send(embed=embed)
    else:
        await ctx.reply("Not owner, cant use this.")
  
  @owner.command()
  async def oping(ctx):
    """Different from normal ping command, this one checks response time and rate limits."""
    if ctx.author.id == "01FZB2QAPRVT8PVMF11480GRCD":
      start = time.time()
      embed=voltage.SendableEmbed(
        title="Pinging..", 
        description=f"Ping!", 
        color="#44ff44"
      )
      msg = await ctx.reply(content="[]()", embed=embed)
      for i in range(1,10):
        embed1 = voltage.SendableEmbed(
          title="Running PING sequence!",
          description=f"Ping! `{i}/10`",
          colour="#44ff44"
        )
        await msg.edit(embed=embed1)
      end = time.time()
      total = end - start
      await msg.edit(
        embed=voltage.SendableEmbed(
          title="Pong!",
          description=f"Pong! in {round(total, 2)}s", # usually this should be 3s - 4s, if its above, you're fucked.
          colour="#44ff44"
        )
      )
    else:
      await ctx.reply("Not owner, cant use this.")
    
  @owner.command(name="eval", description="Run commands in multiple languages!")
  async def eval_fn(ctx, *, code):
        if ctx.author.id in [
            "01FZB2QAPRVT8PVMF11480GRCD",
            "01FZBQCQPT53YTAD86T28WV69X",
        ]:
            languagespecifiers = [
                "python",
                "py",
                "javascript",
                "js",
                "html",
                "css",
                "php",
                "md",
                "markdown",
                "go",
                "golang",
                "c",
                "c++",
                "cpp",
                "c#",
                "cs",
                "csharp",
                "java",
                "ruby",
                "rb",
                "coffee-script",
                "coffeescript",
                "coffee",
                "bash",
                "shell",
                "sh",
                "json",
                "http",
                "pascal",
                "perl",
                "rust",
                "sql",
                "swift",
                "vim",
                "xml",
                "yaml",
            ]
            loops = 0
            while code.startswith("`"):
                code = "".join(list(code)[1:])
                loops += 1
                if loops == 3:
                    loops = 0
                    break
            for languagespecifier in languagespecifiers:
                if code.startswith(languagespecifier):
                    code = code.lstrip(languagespecifier)
            while code.endswith("`"):
                code = "".join(list(code)[0:-1])
                loops += 1
                if loops == 3:
                    break
            code = "\n".join(f"    {i}" for i in code.splitlines())
            code = f"async def eval_expr():\n{code}"

            async def send(text):
                await ctx.send(text)

            env = {
                "bot": client,
                "client": client,
                "ctx": ctx,
                "print": send,
                "_author": ctx.author,
                "_message": ctx.message,
                "_channel": ctx.channel,
                "_guild": ctx.server,
                "_me": ctx.me,
            }
            env.update(globals())
            try:
                exec(code, env)
                eval_expr = env["eval_expr"]
                result = await eval_expr()
                if result:
                    embed = voltage.SendableEmbed(
                        title="Code Ran with no errors!",
                        description=result,
                        colour="#00FF00",
                    )
                    await ctx.send(content=ctx.author.mention, embed=embed)
            except Exception as e:
                embed = voltage.SendableEmbed(
                    title="Error occured!",
                    description=f"```{languagespecifier}\n{e}\n```",
                    colour="#0000FF",
                )
                await ctx.send(content=ctx.author.mention, embed=embed)
        else:
            embed = voltage.SendableEmbed(
                title="Whoops!",
                description="You aren't an owner of this bot!",
                colour="#FFFF00",
            )
            return await ctx.send(content=ctx.author.mention, embed=embed)

    
  @owner.command(
    name="kwargstest", 
    description="working with kwargs sucks, kids.",
    aliases=['kt', 'okt', 't']
  )
  async def kwargstest(ctx, *time, **message):
    if ctx.author.id == "01FZB2QAPRVT8PVMF11480GRCD":
      await ctx.send(f"{str(time)}\n{str(message)}")
    else:
      await ctx.reply("Not owner, cant use this.")

  @owner.command()
  async def aggregate(ctx):
    await ctx.send("done")
    
  def restart_bot(): 
    os.execv(sys.executable, ['python'] + sys.argv)

  @owner.command(name= 'restart')
  async def restart(ctx):
    if ctx.author.id == "01FZB2QAPRVT8PVMF11480GRCD":
      await ctx.send("Restarting bot...")
      restart_bot()
    else:
      await ctx.reply("Not owner, cant use this.")

  @owner.command()
  async def servers(ctx):
    if ctx.author.id == "01FZB2QAPRVT8PVMF11480GRCD":
      for server in client.servers:
        print(f"[{server.id}] {server.name} - {len(server.members)}")
    else:
      await ctx.reply("Not owner, cant use this.")
      
    
  return owner