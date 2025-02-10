import discord
from discord.ext import commands
from bs4 import BeautifulSoup as bs
##from lxml import html
from urllib.request import urlopen, urlretrieve
##import urllib
##import wikia
from sqlite3 import *
from random import *
import os

heart = connect("undercards.db")
c = heart.cursor()

costs = {row[0]:row[1] for row in c.execute("""SELECT name, cost FROM cards WHERE rarity != "removed" ORDER BY cost, name ASC""")}
prices = [n for n in costs]

spells = [row[0] for row in c.execute("""SELECT name FROM cards WHERE soul != "" AND rarity != "removed" ORDER BY cost, name ASC""")]
monsters = [m for m in prices if m not in spells]

gen = {row[0]:row[1] for row in c.execute("""SELECT name, source FROM gen ORDER BY source, name ASC""")}

rarities = {}
for r in ['base', 'common', 'rare', 'epic', 'legendary', 'determination']:
    rarities.update({r: [row[0] for row in c.execute("""SELECT name FROM cards WHERE rarity = "{}" ORDER BY name ASC""".format(r))]})
    
tribes = {}
for t in ['all', 'amalgamate', 'bomb', 'chaos weapon', 'dog', 'froggit', 'g follower', 'lost soul', 'mold', 'plant', 'royal guard', 'snail', 'temmie']:
    tribes.update({t: [row[0] for row in c.execute("""SELECT name FROM cards WHERE tribe = "{}" ORDER BY name ASC""".format(t))]\
                   + [row[0] for row in c.execute("""SELECT name FROM gen WHERE tribe = "{}" AND name != "Lost Souls" ORDER BY name ASC""".format(t))]})

classes = {}
for s in ['dt', 'patience', 'bravery', 'integrity', 'pv', 'kindness', 'justice']:
    classes.update({s: [row[1] for row in c.execute("""SELECT name, blurb FROM souls WHERE name = '{}'""".format(s))]\
    + [row[1] for row in c.execute("""SELECT name, spells FROM souls WHERE name = '{}'""".format(s))][0].split("\n")})

arts = {}
for a in ['normal', 'legendary', 'generated']:
    arts.update({a: {row[0]: row[1] for row in c.execute("""SELECT name, blurb FROM artifacts WHERE rarity = "{}" ORDER by name ASC""".format(a))}})

effects = {row[0]: row[1] for row in c.execute("""SELECT name, blurb FROM effects""")}

skins = {row[0]:[row[1], row[2], row[3]] for row in c.execute("""SELECT name, source, artist, cost FROM skins ORDER BY source, name ASC""")}
artists = list(set([row[0] for row in c.execute("""SELECT artist FROM skins""")]))

nine = commands.Bot(command_prefix = "98!", description = "`* I Am 98, A Bot Dedicated to the Card Game Known As 'Undercards'.`", case_insensitive = True)

def get_images(url, card, rat = None):
    rarities = ["BASE", "COMMON", "RARE", "EPIC", "LEGENDARY", "DETERMINATION", "UNKOWN"]
    links = []
    try:
        soup = bs(urlopen(url).read(), "html.parser")
    except:
        return "`* Card Not Found.`"
    images = [img for img in soup.findAll('img')]
    image_links = [each.get('src') for each in images]
    for each in image_links:
        if "vignette.wikia.nocookie.net/undercards/images/" in each or "static.wikia.nocookie.net/undercards/images/" in each:
            links.append(each)
    for pack in links:
        for r in rarities:
            if r in pack:
                links.remove(pack)
    posts = []
    if rat:
        for pack in links:
            if pack.find("Skin") == -1:
                if True: # rep(rat) in pack:
                    if rat.title().split()[0] in pack:
                        if rat.title().split()[-1] + "." in pack\
                            or rat.title().split()[-1] + "_" in pack:
                                posts.append(pack)
    if not posts:
        if "scale-to-width-down/" in links[0]:
            find = links[0].find("scale-to-width-down/")
            links[0] = links[0][0:find] + links[0][find + 23:]
        if "/revision/latest" in links[0]:
            find = links[0].find("/revision/latest")
            links[0] = links[0][0:find]
        return links[0]
    else:
        if "scale-to-width-down/" in posts[0]:
            find = posts[0].find("scale-to-width-down/")
            posts[0] = posts[0][0:find] + posts[0][find + 23:]
        if "/revision/latest" in posts[0]:
            find = posts[0].find("/revision/latest")
            posts[0] = posts[0][0:find]
        return posts[0]

@nine.event
async def on_ready():
    await nine.change_presence(activity=discord.Streaming(name='Undercards ❤', url='https://undercards.net/'))
    
@nine.command(pass_context=True)
async def greet(ctx):
    """Says Hello."""
    greetings = ["How Are You Today?", "I Am 98.", "What Is Up?"]
    await ctx.send("`* Greetings, " + str(ctx.message.author.display_name).title() + ". " + choice(greetings) + "`")

@commands.is_owner()
@nine.command(pass_context=True)
async def post(ctx, *args):
    post = ""
    for l in args:
        post += str(l) + " "
    post = post[:-1]
    await ctx.send(post)

@commands.is_owner()
@nine.command(pass_context=True)
async def say(ctx, *args):
    post = ""
    for l in args:
        post += str(l) + " "
    post = post[:-1]
    await ctx.send("`" + post + "`")

@nine.command(pass_context=True)
async def check(ctx, *args):
    """Checks Undercards Wiki For The Requested Card."""
    url = None
    card = ""
    rat = None
    for l in args:
        card += str(l) + " "
    if not card.endswith("... "):
        if not card:
            card = choice(monsters)
        if rep(card).replace("_", " ")[:-1] in gen:
            if rep(card).startswith("Lost"):
                card = "Lost Souls "
            rat = card
            card = gen[rep(card).replace("_", " ")[:-1]]
            for bit in gen:
                if rat.title()[:-1] in bit:
                    url = "http://undercards.wikia.com/wiki/" + rep(gen[bit])
        if not url:
            url = "http://undercards.wikia.com/wiki/" + rep(card)
        await ctx.send(get_images(url, card, rat))
    else:
        await ctx.send(wild(card))

@nine.command(name = "soul", aliases = ["class"], pass_context=True)
async def soul(ctx, *args):
    """Displays data on the specified class."""
    text = None
    spell = None
    if len(args) > 1:
        await ctx.send("`* I Can Only Handle One Soul At A Time.`")
    elif not args:
        Class = choice(list(classes.keys()))
    else:
        Class = args[0].lower()
    if Class == "determination":
        Class = "dt"
    if Class.startswith("pers"):
        Class = "pv"
    if Class.startswith("int"):
        Class = "integrity"
    if Class in classes:
        text = classes[Class][0]
        spell = choice(classes[Class][1:])
    if text and spell:
##        await ctx.send(text + "\n`Here Is A Random " + text.split(":")[0][2:] + " Spell:`")
##        await ctx.invoke(check, spell)
        await ctx.send('`' + text + '`' + "\n`Here Are The Spells Of This Class: " + str(classes[Class][1:]).replace("[", "").replace("]", "") + "`")
    else:
        await ctx.send("`* Soul Not Found.`")
   
@nine.command(name = "artifact", aliases = ["art", "artefact"], pass_context=True)
async def artifact(ctx, *args):
    """Gives a description of the requested artifact."""
    art = ""
    fax = []
    for a in args:
        art += str(a) + " "
    art = art[:-1].title()
    if not art:
        if randint(1, 2) == 1:
            art = choice(list(arts["normal"].keys()))
        else:
            art = choice(list(arts["legendary"].keys()))
    if art.endswith("..."):
        for i in arts["normal"]:
            if art[:-3] in i:
                fax.append(i)
        for i in arts["legendary"]:
            if art[:-3] in i:
                fax.append(i)
        for i in arts["generated"]:
            if art[:-3] in i:
                fax.append(i)
        if len(fax) > 1:
            await ctx.send("`* Here Are The Artifacts I Found: " + str(fax).replace("[", "").replace("]", "") + "`")
        elif not fax:
            pass
        else:
            art = fax[0]
    if (art not in arts["normal"] and art not in arts["legendary"] and art not in arts["generated"]) and not fax:
        await ctx.send("`* Artifact Not Found.`")
    else:
        if art in arts["normal"]:
            await ctx.send("`'" + art + " | Normal | " + arts["normal"][art] + "'`")
        elif art in arts["legendary"]:
            await ctx.send("`'" + art + " | Legendary | " + arts["legendary"][art] + "'`")
        elif art in arts["generated"]:
            await ctx.send("`'" + art + " | Generated | " + arts["generated"][art] + "'`")

@nine.command(name = "generate", aliases = ["gen"], pass_context=True)
async def generate(ctx, *args):
    """Generates a random unrestricted deck of the soul you choose, including artifacts."""
    soul = None
    facts = []
    deck = []
    ment = []
    ranks = ""
    limits = {"base": 3, "common": 3, "rare": 3, "epic": 2, "legendary": 1}
    Det = False
    for a in args:
        ment.append(a.lower())
    if len(ment) > 1:
        if "ranked" in ment:
            pass
        else:
            await ctx.send("`* I Can Only Handle One Soul At A Time.`")
    elif not args:
        soul = choice(['dt', 'patience', 'bravery', 'integrity', 'pv', 'kindness', 'justice'])
    if "ranked" in ment:
        Det = True
        ranks = "Ranked "
        ment.remove("ranked")
    if not soul:
        soul = ment[0].lower()
    if soul == "determination":
        soul = "dt"
    if soul.startswith("pers"):
        soul = "pv"
    if soul.startswith("int"):
        soul = "integrity"
    if soul not in classes:
        if soul == "ranked":
            soul = choice(['dt', 'patience', 'bravery', 'integrity', 'pv', 'kindness', 'justice'])
        else:
            soul = None
            await ctx.send("`* Soul Not Found.`")
    if soul:
        pool = monsters + classes[soul][1:]
        while len(deck) < 25:
            mon = choice(pool)
            if mon == "Heal Delivery" or mon == "Sharing":
                pass
            elif mon in rarities["common"] or mon in rarities["rare"]:
                if deck.count(mon) < 3:
                    deck.append(mon)
            elif mon in rarities["epic"]:
                if deck.count(mon) < 2:
                    deck.append(mon)
            elif mon in rarities["legendary"]:
                if deck.count(mon) < 1:
                    deck.append(mon)
            elif mon in rarities["determination"]:
                if not Det:
                    deck.append(mon)
                    Det = True
        rarity = randint(1, 2)
        if rarity == 1:           
            facts.append(choice(list(arts["normal"].keys())))
            facts.append(choice(list(arts["normal"].keys())))
            while facts[0] == facts[1]:
                facts.remove(facts[1])
                facts.append(choice(list(arts["normal"].keys())))
            facts.sort()
        elif rarity == 2:
            facts.append(choice([l for l in list(arts["legendary"].keys()) if l != "Criticals"]))
    if deck:
        deck.sort(key = lambda x: prices.index(x))
        post = "Your " + ranks + classes[soul][0].split(":")[0] + " Deck: "
        for d in deck:
            post += rep(d).replace("_", " ") + ", "
        post = post[:-2]
        post += "\nArtifacts: "
        for f in facts:
            post += f + ", "
##        if "Gerson" in deck:
##            post += choice(list(arts["Gerson"].keys()))
        else:
            post = post[:-2]
        await ctx.send("`" + post + "`")
                         
@nine.command(pass_context=True)
async def rarity(ctx, *args):
    """Returns a random card of the selected rarity."""
    rar = ""
    if len(args) > 1:
        await ctx.send("`* I Can Only Handle One Rarity At A Time.`")
    elif not args:
        rar = choice(["base", "common", "rare", "epic", "legendary", "determination"])
    else:
        rar = args[0].lower()
    if rar == "dt":
        rar = "determination"
    car = choice(rarities[rar])
    await ctx.send("`* There Are " + str(len(rarities[rar])) + " " + rar.title() + " Cards.\nHere Is A Random One:`")
    await ctx.invoke(check, car)

@nine.command(name = "effect", aliases = ["keyword"], pass_context=True)
async def effect(ctx, *args):
    """Gives a description of an effect or keyword."""
    global effects
    psuedonyms = {"Kr": "KR", "Another chance": "Another Chance", "Not targetable": "Locked", "Can't attack": "Disarmed",
                  "Start of turn": "Turn start", "End of turn": "Turn end"}
    eff = ""
    if not args:
        eff = choice(list(effects.keys())) + " "
    else:
        for i in args:
            eff += i + " "
    eff = eff[:-1].capitalize()
    for f in psuedonyms:
        if eff == f:
            eff = psuedonyms[f]
    if eff in effects:
        await ctx.send('`"' + eff + ": " + effects[eff] + '"`')
    else:
        await ctx.send("`Effect Not Found.`")
        
@nine.command(pass_context=True)
async def tribe(ctx, *args):
    global tribes
    tri = ""
    if not args:
        tri = choice(list(tribes.keys())) + " "
    else:
        for i in args:
            tri += i + " "
    tri = tri[:-1].lower()
    if tri in tribes:
        if len(tribes[tri]) == 1:
            await ctx.send('`There is just 1 member of the ' + tri.title() + ' tribe.\nIt is:`')
            await ctx.invoke(check, choice(tribes[tri]))
        else:
            await ctx.send('`There are ' + str(len(tribes[tri])) + ' members of the ' + tri.title() + ''' tribe.
They are: ''' + str(tribes[tri]).replace("[", "").replace("]", "") + "`")
    else:
        await ctx.send("`Tribe Not Found.`")
        
@nine.command(pass_context=True)
async def skin(ctx, *args):
    global skins
    ski = ""
    if not args:
        ski = choice(list(skins.keys())) + " "
    else:
        for i in args:
            ski += i + " "
    ski = rep(ski[:-1].title()).replace("_", " ")
    pieces = [k for k,v in skins.items()\
              if ski in [rep(str(i)).replace("_", " ") for i in v]]
    if ski in skins:
        await ctx.send("`'" + ski + "' - " + skins[ski][0] + " - " + str(skins[ski][2]) + """ UCP
by """ + skins[ski][1] + "`\nhttps://undercards.net/images/cards/" + ski.replace(" ", "_") + ".png")
    elif ski in [rep(s.title()).replace("_", " ") for s in artists]:
        switch = ['s. One is:`', '.`']
        await ctx.send('`' + ski + ' has made ' + str(len(pieces)) + ' skin' + switch[len(pieces) == 1])
        await ctx.invoke(skin, choice(pieces))
    elif ski in prices or ski in list(gen.keys()):
        if len(pieces) == 1:
            await ctx.invoke(skin, pieces[0])
        else:
            await ctx.send("`There are " + str(len(pieces)) + " " + ski + """ skins.
They are: """ + str(pieces).replace("[", "").replace("]", "") + "`")
    else:
        await ctx.send('`Skin Not Found.`')

def wild(card):
    global monsters
    global gen
    url = None
    pages = []
    rat = None
    for page in monsters:
        if card[:-4].title() in page:
            pages.append(page)
    for arc in spells:
        if card[:-4].title() in arc:
            pages.append(arc)
    for tor in gen:
        if card[:-4].title() in tor:
            pages.append(tor)        
    if len(pages) > 1:
        for p in pages:
            p = rep(p).replace("_", " ")        
        return("`* Here Are The Cards I Found: " + str(pages).replace("[", "").replace("]", "") + "`")
    elif not pages:
        return("`* Card Not Found.`")
    else:
        if pages[0] in gen:
            card = gen[pages[0]]
            rat = pages[0]
        else:
            card = pages[0]
        for bit in gen:
            if card.title()[:-1] in bit:
                url = "http://undercards.wikia.com/wiki/" + rep(gen[bit])
        if not url:
            url = "http://undercards.wikia.com/wiki/" + rep(card)
        return get_images(url, card, rat)
    
def rep(text):
    text = text.replace(" ", "_").title().replace("To_", "to_").replace("Of", "of").replace("'S", "'s").replace("Mtt", "MTT").replace("Neo", "NEO").replace("Tv", "TV")

    return text

nine.remove_command("help")

@nine.command()
async def help(ctx):
    """Shows My Instruction Manual."""
    emb = discord.Embed(title = "98", description = nine.description, inline = False)
    emb.add_field(name = "98!greet", value = "Says hello.", inline = False)
    emb.add_field(name = "98!check <card>", value = "Checks Undercards Wiki for the requested card.\n('...' for autocomplete, but only with full keywords)", inline = False)
    emb.add_field(name = "98!soul <soul>", value = "Returns information on the specified soul, and the spells of that class. (alias: 98!class)", inline = False)
    emb.add_field(name = "98!artifact <artifact>", value = "Gives a description of the requested artifact. (alias: 98!art)", inline = False)
    emb.add_field(name = "98!rarity <rarity>", value = "Returns a random card of the selected rarity.", inline = False)
    emb.add_field(name = "98!effect <effect>", value = "Gives a description of the requested effect of keyword. (alias: 98!keyword)", inline = False)
    emb.add_field(name = "98!generate <soul>", value = "Generates a random deck of the soul you choose, including artifacts. Call `98!generate <soul> ranked` for no DTs. (alias: 98!gen)", inline = False)
    emb.add_field(name = "98!tribe <tribe>", value = "Gives the number of cards in a tribe, as well as a list of them.", inline = False)
    emb.add_field(name = "98!skin <skin/artist/card>", value = "Gives information on a skin, information on an artist, or information about the skins a card has.", inline = False)
    emb.add_field(name = "98!help", value = "Shows commands.", inline = False)
    await ctx.send(embed=emb)
                        
nine.run(os.environ["BOT_TOKEN"])
