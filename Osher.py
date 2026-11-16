from cmu_graphics import *
import random
import copy
import math
from PIL import Image

def makeRandomDeck(existingDeck=None):
    deck = ''
    for i in random.sample(range(52), 52):
        rank = 'A23456789TJQK'[i%13]
        suit = 'shdc'[i//13]
        card = rank + suit
        if existingDeck != None and card not in existingDeck: deck += card
        elif existingDeck == None: deck += card
    return deck

def reshuffleDeck(app):
    cardsInPlay = set()
    for hand in app.cards:
        for card in app.cards[hand]:
            if card == None: continue
            cardsInPlay.add(card.value)
    if app.topCard != None: cardsInPlay.add(app.topCard)
    if app.cardBeingSeen != None: cardsInPlay.add(app.cardBeingSeen)
    if app.tempCard != None: cardsInPlay.add(app.tempCard.value)
    return makeRandomDeck(cardsInPlay)

def dealCard(app):
    if len(app.deck) < 2: app.deck = reshuffleDeck(app)
    card = app.deck[:2]
    app.deck = app.deck[2:]
    return card

def chance(probability):
    return random.random() < probability

def activeHands(app):
    if app.players == 2: return [0, 2]
    elif app.players == 3: return [0, 1, 2]
    return [0, 1, 2, 3]

def handActive(app, i):
    return i in activeHands(app)

def computerHands(app):
    hands = []
    for i in activeHands(app):
        if i != 0: hands.append(i)
    return hands

def nextHand(app, i):
    hands = activeHands(app)
    if i not in hands: return hands[0]
    return hands[(hands.index(i) + 1) % len(hands)]

def computerName(app, i):
    if app.players == 2: return 'Computer'
    return f'Computer {i}'

def scoreHand(app, player):
    if app.cards[player] == [None]*6: return 0
    score = 0
    for card in app.cards[player]:
        if card == None: continue
        if card.value[0] in 'TJQ': score += 10
        elif card.value[0] == 'A': score += 1
        elif card.value[0] == 'K':
            if card.value[1] in 'sc': score += 10
            else: score -= 1
        else: score += int(card.value[0])
    return score

class Card:
    def __init__(self, value, i, j, app, initialDeal = True):
        coords = loadCoords(app)
        xList, yList = coords[i*2], coords[i*2 + 1]
        self.value = value
        self.i = i
        self.j = j
        self.left = xList[j]
        self.top = yList[j]
        self.width = app.len/15 if i in [0,2] else app.len/10
        self.height = app.len/10 if i in [0,2] else app.len/15
        self.computerKnows = [None] + [False]*3
        if initialDeal and i != 0 and j in [2,3]:
            self.computerKnows[i] = True
    def __repr__(self):
        return f'{self.value}: ({self.i}, {self.j}) {self.computerKnows[1]}'
    def __eq__(self, other):
        if isinstance(other, Card):
            return self.value == other.value
        if isinstance(other, str):
            return self.value[0] == other[0]
    def __hash__(self):
        return hash(str(self))
    def clicked(self, mouseX, mouseY):
        if (self.left < mouseX < self.left + self.width and
           self.top < mouseY < self.top + self.height):
            return True
        return False
    def update(self, app):
        self.width = app.len/15 if self.i in [0,2] else app.len/10
        self.height = app.len/10 if self.i in [0,2] else app.len/15

def dealHands(app):
    app.deck = makeRandomDeck()
    allCards = []
    for i in range(4):
        allCards.append([None]*6)
    for j in range(4):
        for i in activeHands(app):
            allCards[i][j] = dealCard(app)
    app.cardsShown = set()
    app.cardsHighlighted = set()
    app.cardsMoused = set()
    updateCards(app, allCards)

def loadImages(app):
    app.cardImageRaw = Image.open('images/Card.jpg')
    app.tableImageRaw = getTransparentImage('images/Table (2).png')
    app.easyBackgroundRaw = Image.open('images/Background-Easy.jpg')
    app.mediumBackgroundRaw = Image.open('images/Background-Medium.jpg')
    app.hardBackgroundRaw = Image.open('images/Background-Hard.jpg')
    app.impossibleBackgroundRaw = Image.open('images/Background-Impossible.jpg')
    app.coverImage = CMUImage(Image.open('images/Cover.jpg'))
    app.wordmark = CMUImage(Image.open('images/Wordmark.png'))
    app.buttonImageRaw = getTransparentImage('images/Button.png')
    loadCardImages(app)
    rescaleImages(app)

def scaledSize(value):
    size = int(value)
    if size < 1: size = 1
    return size

def rescaleImages(app):
    if (app.scaledLen == app.len and app.scaledWidth == app.width and
        app.scaledHeight == app.height): return
    app.scaledLen, app.scaledWidth = app.len, app.width
    app.scaledHeight = app.height
    cardW, cardH = scaledSize(app.len/15), scaledSize(app.len/10)
    bgW, bgH = scaledSize(app.width), scaledSize(app.height)
    tableSize = scaledSize(app.len - app.len/4.1)
    app.cardImage = CMUImage(app.cardImageRaw.resize((cardW, cardH)))
    app.tableImage = CMUImage(app.tableImageRaw.resize((tableSize, tableSize)))
    app.easyBackground = CMUImage(app.easyBackgroundRaw.resize((bgW, bgH)))
    app.mediumBackground = CMUImage(app.mediumBackgroundRaw.resize((bgW, bgH)))
    app.hardBackground = CMUImage(app.hardBackgroundRaw.resize((bgW, bgH)))
    app.impossibleBackground = CMUImage(
        app.impossibleBackgroundRaw.resize((bgW, bgH)))
    app.rulesButton = CMUImage(
        app.buttonImageRaw.resize((scaledSize(app.len/3.5),
                                   scaledSize(app.len/3))))
    app.settingsButton = CMUImage(
        app.buttonImageRaw.resize((scaledSize(app.len/3.1),
                                   scaledSize(app.len/3))))
    app.cardFaces = dict()
    for suit in ['c', 'd', 'h', 's']:
        app.cardFaces[suit] = []
        for i in range(13):
            scaled = app.cardFacesRaw[suit][i].resize((cardW, cardH))
            app.cardFaces[suit].append(CMUImage(scaled))

def loadCardImages(app):
    app.cardFacesRaw = dict()
    app.cardFacesRaw['c'] = []
    app.cardFacesRaw['d'] = []
    app.cardFacesRaw['h'] = []
    app.cardFacesRaw['s'] = []
    for i in range(13):
        app.cardFacesRaw['d'].append(Image.open(f'images/DIAMOND-{i+1}.png'))
        app.cardFacesRaw['h'].append(Image.open(f'images/HEART-{i+1}.png'))
        app.cardFacesRaw['s'].append(Image.open(f'images/SPADE-{i+1}.png'))
        app.cardFacesRaw['c'].append(Image.open(f'images/CLUB-{i+1}.png'))
    app.cardFacesFull = dict()
    for suit in ['c', 'd', 'h', 's']:
        app.cardFacesFull[suit] = []
        for i in range(13):
            app.cardFacesFull[suit].append(CMUImage(app.cardFacesRaw[suit][i]))

def getTransparentImage(path): 
    image = Image.open(path) 
    for i in range(image.width): 
        for j in range(image.height): 
            pixel = image.getpixel((i, j)) 
            if pixel[3] == 0: 
                image.putpixel((i, j), (0, 0, 0, 0)) 
    return image

def updateCards(app, allCards = None):
    coords = loadCoords(app)
    if allCards == None:
        for k in app.cards:
            for card in app.cards[k]:
                if card == None: continue
                card.update(app)
                xList, yList = coords[k*2], coords[k*2 + 1]
                card.left,card.top = xList[card.j], yList[card.j]
    else:
        app.cards = dict()
        app.cards[0],app.cards[1] = [None]*6, [None]*6
        app.cards[2],app.cards[3] = [None]*6, [None]*6
        for i in range(len(allCards)):
            for j in range(len(allCards[i])):
                card = allCards[i][j]
                if card != None:
                    app.cards[i][j] = Card(card, i, j, app)

def loadCoords(app):
    if (app.coordsCache != None and app.coordsLen == app.len and
        app.coordsWidth == app.width and app.coordsHeight == app.height):
        return app.coordsCache
    cardLength, cardWidth = app.len/10, app.len/15
    tableOffsetX, tableOffsetY, d = app.len/45, app.len/11, app.len/200
    xList0n2 = [app.width/2 - cardWidth - d, app.width/2 + d,
             app.width/2 - cardWidth - d, app.width/2 + d,
             app.width/2 - 2*cardWidth - 3*d, app.width/2 + cardWidth + 3*d]
    yList0 = [app.height/2 + 2*cardLength, app.height/2 + 2*cardLength,
             app.height/2+3*cardLength+2*d,app.height/2+3*cardLength+2*d,
             app.height/2 + 3*cardLength + 2*d,app.height/2 + 3*cardLength+2*d]
    xList1 = [app.width/2 + cardLength + tableOffsetX, app.width/2 + cardLength 
              + tableOffsetX, app.width/2 + 2*cardLength + 2*d + tableOffsetX,
              app.width/2 + 2*cardLength + 2*d + tableOffsetX, app.width/2 + 2*
              cardLength + 2*d + tableOffsetX, app.width/2 + cardLength + 
              tableOffsetX]
    yList1n3 = [app.height/2 + tableOffsetY + d,app.height/2 + tableOffsetY - 
                d - cardWidth,app.height/2 + tableOffsetY + d, app.height/2 + 
                tableOffsetY - d - cardWidth, app.height/2 + tableOffsetY + 3*d 
                + cardWidth, app.height/2 + tableOffsetY + 3*d + cardWidth]
    yList2 = [app.height/2 - 2.2*cardLength + tableOffsetY, app.height/2 - 2.2*
              cardLength + tableOffsetY,app.height/2 - 3.2*cardLength - 2*d + 
              tableOffsetY, app.height/2 - 3.2*cardLength - 2*d + tableOffsetY,
              app.height/2 - 3.2*cardLength - 2*d + tableOffsetY,
              app.height/2 - 3.2*cardLength - 2*d + tableOffsetY]
    xList3 = [app.width/2 - 2*cardLength - tableOffsetX, app.width/2 - 
              2*cardLength - tableOffsetX, app.width/2 - 3*cardLength - 2*d - 
              tableOffsetX,app.width/2 - 3*cardLength - 2*d - tableOffsetX,
              app.width/2 - 3*cardLength - 2*d - tableOffsetX,
              app.width/2 - 2*cardLength - tableOffsetX]
    app.coordsCache = (xList0n2, yList0, xList1, yList1n3, xList0n2, yList2,
                       xList3, yList1n3)
    app.coordsLen = app.len
    app.coordsWidth = app.width
    app.coordsHeight = app.height
    return app.coordsCache

def assignBools(app):
    app.gameOver = True
    app.firstCardSelected = False
    app.secondCardSelected = False
    app.kingViewed = False
    app.holdingDrawnCard = False
    app.sevenOrEight = False
    app.nineOrTen = False
    app.jackOrQueen = False
    app.king = False
    app.isTopCard = False
    app.viewingRules = False
    app.viewingSettings = False
    app.viewingBottomCards = False
    app.displayStickMessages = [False]*4
    app.displayMistakeMessages = [False]*4
    app.displayStickOpponentMessage = False
    app.lookingAtCard = False
    app.playerDrawingCard = False
    app.lagReduce = False
    app.cardsMoving = False
    app.cardMoving = False
    app.tempCardMoving = False
    app.tempCardShown = False
    app.swapProgress = app.swapStart = None
    app.moveProgress = app.moveStart = None
    app.tempProgress = app.tempStart = None

def startNewGame(app):
    app.players = app.pendingPlayers
    app.deck = makeRandomDeck()
    dealHands(app)
    assignBools(app)
    app.message = 'Welcome to Osher!'
    app.topCard = dealCard(app)
    app.osherCaller = None
    app.timers = []
    app.cardBeingSeen = None
    app.sticker = None
    app.movingCard = app.targetI = app.targetJ = None
    app.firstCard = app.secondCard = None
    app.firstCardSelected = app.secondCardSelected = False
    app.opponentStuck = None
    app.tempCard = None

def rules(app):
    app.rules = '''- The objective of Osher is to have the lowest score in \
your hand.

- The scoring is as follows: aces are 1, every number card is its number, and
 all face cards are 10 with the exception of the red kings, which are -1.

- At the beginning of the game, you get to look at your bottom two cards only
 once, and you must remember them (suit does not matter except for kings).

- On your turn, you draw a card, either from the draw pile or the top of the
 discard pile. Keep in mind that all other players can see the top card of the
 discard pile and will know the card if you draw it from there.

- You can choose to either discard this card or replace it for one of the cards
 in your deck (unless it's from the discard pile, in which case you cannot
 discard it again.)

- Certain cards have special powers when you draw them from the draw pile
 and discard them. The powers are as follows:

- 7,8: You can look at one of your own cards (once). 
- 9,10: You can look at another player's card (once). 
- J,Q: You can swap the positions of two cards on the table. 
- K: You can look at any two cards, and swap any two cards (which
 could be different from the ones you looked at). Remember to keep red kings!

- The reason knowing cards on the table is so important is because of \
"sticking."
 At any point in the game, if you know a card on the table is the same number/
 face as the top card in the discard pile, you can "stick" that card.

- If that card is your own, then you get rid of it. You now have one less card.
 However, if that card is your opponent's, you can then choose any one of your
 cards to give them as a replacement. Again, you now have one less card.

- Some rules about sticking: only one player can stick per turn! If you try to
 stick a card and another player has already stuck during that turn, you have
 made a mistake and must draw another card.

- Additionally, if you try to stick a card that is not the same as the top card,
 this is also a mistake and you must draw another card.

- If you make a mistake and end up with more than 6 cards, you lose!

- The game ends when any player, at the beginning of their turn, calls "Osher."
 After the call, that player's turn is skipped, and each other player gets \
to play 
 once before the game ends. During this period, the caller's cards cannot be 
 stuck or swapped. When the game ends, the player with the lowest score wins!

Good luck! If you're confused, that's okay; the best way to learn is to play.'''
    app.rulePosition = 0

def onResize(app):
    app.len = app.height if app.height < app.width else app.width
    rescaleImages(app)
    updateCards(app)

def onAppStart(app):
    app.coordsCache = app.coordsLen = None
    app.coordsWidth = app.coordsHeight = None
    app.scaledLen = app.scaledWidth = app.scaledHeight = None
    rules(app)
    app.timers = []
    app.len = app.width
    app.players = 4
    app.pendingPlayers = 4
    app.player = 5
    app.stepsPerSecond = 20
    app.backgroundColor = rgb(0, 100, 30)
    app.width = 711
    app.showLength = 1
    app.realCards = True
    app.displayCover = True
    app.displayArrowMessage = True
    startNewGame(app)
    loadImages(app)

def getSuit(suit):
    if suit == 'c': return chr(0x2663)
    elif suit == 'd': return chr(0x2666)
    elif suit == 'h': return chr(0x2665)
    if suit == 's': return chr(0x2660)

def drawCardVertical(app, x, y, fillColor, card, highlight, moused):
    if fillColor == 'red':
        drawImage(app.cardImage,x,y,align='left-top')
        if highlight: drawRect(x,y,app.len/15,app.len/10,fill=None,
                               border='yellow',borderWidth=app.len/350)
        elif moused:
            drawRect(x,y,app.len/15,app.len/10,fill=None,border='lightBlue',
                     borderWidth=app.len/450)
        else: drawRect(x-app.len/800,y-app.len/800,app.len/15+app.len/400,
                       app.len/10+app.len/400,fill=None,border='fireBrick',
                       borderWidth=app.len/800)
    elif fillColor == 'white':
        cardColor = 'red' if card[1] in 'hd' else 'black'
        if app.realCards:
            i = getRealCardIndex(card)
            drawRect(x-app.len/800,y-app.len/800,app.len/15+app.len/400,
                       app.len/10+app.len/400,fill='white')
            drawImage(app.cardFaces[card[1]][i],x,y,align='left-top')
        else:
            drawRect(x,y,app.len/15,app.len/10, fill = fillColor, 
                     border='black', borderWidth=app.len/200)
            if card[0] == 'T':
                drawLabel('10',x + app.len/30, y + app.len/30,
                        fill=cardColor, size=app.len/30, font='Times New Roman')
            else: drawLabel(f'{card[0]}', x + app.len/30, y+ app.len/30, 
                            fill=cardColor, size=app.len/30, 
                            font='Times New Roman')
            drawLabel(getSuit(card[1]), x + app.len/30, y+ app.len/14.5, 
                    fill=cardColor, size=app.len/30, font = 'symbols')

def getRealCardIndex(card):
    if card[0] == 'A': return 0
    elif card[0] == 'T': return 9
    elif card[0] == 'J': return 10
    elif card[0] == 'Q': return 11
    elif card[0] == 'K': return 12
    else: return int(card[0]) - 1

def drawCardHorizontal(app, x, y, fillColor, card, highlight, moused):
    if fillColor == 'red':
        drawImage(app.cardImage,x,y,align='left-top',rotateAngle = 90)
        if highlight: drawRect(x,y,app.len/10,app.len/15,fill=None,
                               border='yellow',borderWidth=app.len/350)
        elif moused: drawRect(x,y,app.len/10,app.len/15,fill=None,
                              border='lightBlue',borderWidth=app.len/450)
        else: drawRect(x-app.len/800,y-app.len/800,app.len/10 + app.len/400,
                       app.len/15 + app.len/400,fill=None,border='fireBrick',
                       borderWidth=app.len/800)
    if fillColor == 'white':
        if app.realCards:
            i = getRealCardIndex(card)
            drawRect(x-app.len/800,y-app.len/800,app.len/10 + app.len/400,
                       app.len/15 + app.len/400,fill='white')
            drawImage(app.cardFaces[card[1]][i],x,y,align='left-top',
                      rotateAngle=90)
        else: 
            drawRect(x,y,app.len/10,app.len/15, fill = fillColor, 
                     border='black', borderWidth=app.len/200)
            cardColor = 'red' if card[1] in 'hd' else 'black'
            if card[0] == 'T':
                drawLabel('10',x + app.len/30, y + app.len/30,
                        fill=cardColor, size=app.len/30, font='Times New Roman')
            else:
                drawLabel(f'{card[0]}', x + app.len/30, y+ app.len/30, 
                        fill=cardColor, size=app.len/30, font='Times New Roman')
            drawLabel(getSuit(card[1]), x + app.len/15, y+ app.len/29, 
                    fill=cardColor, size=app.len/30, font = 'symbols')

def drawCards(app):
    for k in app.cards:
        for card in app.cards[k]:
            if card == None: continue
            fillColor = 'white' if (k, card.j) in app.cardsShown else 'red'
            if k in [0,2]:
                drawCardVertical(app, card.left, card.top, fillColor,
                                card.value, (k, card.j) in app.cardsHighlighted,
                                (k, card.j) in app.cardsMoused)
            elif k in [1,3]:
                drawCardHorizontal(app, card.left, card.top, fillColor,
                                card.value, (k, card.j) in app.cardsHighlighted,
                                (k, card.j) in app.cardsMoused)
    if app.tempCard != None:
        fillColor = 'white' if app.tempCardShown else 'red'
        if app.tempCard.i in [0,2]:
            drawCardVertical(app,app.tempCard.left,app.tempCard.top,fillColor,
                             app.tempCard.value, False, False)
        else:
            drawCardHorizontal(app,app.tempCard.left,app.tempCard.top,fillColor,
                             app.tempCard.value, False, False)

def drawCenterCards(app,d):
    cardLength = app.len/10
    cardWidth = app.len/15
    tableOffsetY = app.len/11
    drawCardVertical(app, app.width/2 - d - cardWidth,
                     app.height/2 + tableOffsetY - cardLength/2, 'red', None,
                     False, False)
    if not app.gameOver and app.topCard != None: 
        drawCardVertical(app, app.width/2 + d, app.height/2 + 
                         tableOffsetY - cardLength/2, 'white', app.topCard,
                         False, False)

def drawRulesBorder(app):
    drawRect(0, 0, app.width, app.height, fill = 'white', opacity = 25)
    drawRect(app.width/2,app.height/2,app.width/1.5,app.height/1.5,
             align='center', fill='white', border='black',
             borderWidth=app.len/100)
    drawRect(app.width/2 + app.width/3 - app.len/40 - app.len/20, app.height/2 
                - app.height/3+app.len/40,app.len/20,app.len/20, fill = 'red')
    drawLabel('X', app.width/2 + app.width/3 - app.len/20, app.height/2 -
                app.height/3 + app.len/20, size = app.len/20, fill = 'white')

def drawScrollBar(app):
    drawRect(app.width/2 + app.width/3 - app.len/20 - app.len/40, 
             app.height/2 - app.height/3 + app.len/12, app.len/20, app.len/20, 
             border = 'black', fill = None, borderWidth = app.len/200)
    drawRect(app.width/2 + app.width/3 - app.len/20 - app.len/40,
                app.height/2 + app.height/3-app.len/12, app.len/20, app.len/20,
                border = 'black', fill = None, borderWidth = app.len/200)
    drawRect(app.width/2 + app.width/3 - app.len/20 - app.len/40,
                app.height/2 - app.height/3 + app.len/12 + app.len/20,
                app.len/20, app.len/2 - app.len/20, fill = 'gray', opacity = 50)
    drawRect(app.width/2 + app.width/3 - app.len/20 - app.len/40,
                app.height/2 - app.height/3 + app.len/12 + app.len/20 + 
                (app.len/2 - app.len/20)/48*app.rulePosition, app.len/20,
                (app.len/2 - app.len/20)/48*15, fill = 'red')
    drawLabel('\u2191', app.width/2 + app.width/3 - app.len/20,
                app.height/2 - app.height/3 + app.len/12 + app.len/20 - 
                app.len/35, size = app.len/30, fill = 'black')
    drawLabel('\u2193', app.width/2 + app.width/3 - app.len/20,
                app.height/2 + app.height/3 - app.len/12 + app.len/48.5, 
                size = app.len/30, fill = 'black')

def drawRuleBox(app):
    drawRulesBorder(app)
    drawScrollBar(app)  
    for rule in range(app.rulePosition, app.rulePosition + 15):
        drawLabel(app.rules.splitlines()[rule], app.width/2 - 
                    app.width/3.25, app.height/2 - app.height/3 + app.len/25 + 
                    (rule-app.rulePosition)*app.len/24, size = app.len/35,
                    font = 'Georgia', align = 'left')
    if app.displayArrowMessage:
        drawRect(app.width/2 + app.len/4.3, app.height/2 - app.len/3.67, 
                 app.len/4, app.len/12, borderWidth = app.len/200, 
                 fill = 'white', border='black')
        drawLabel('You can hold the', app.width/2 + app.len/2.8, 
                    app.height/2 - app.len/4, font = 'Georgia',size=app.len/40)
        drawLabel('arrow keys to scroll!', app.width/2 + app.len/2.8,
                    app.height/2 - app.len/4 + app.len/30, font = 'Georgia', 
                    size = app.len/40)

def drawArrowButton(app, arrow, x, y):
    drawRect(x, y, app.len/14, app.len/14, fill = None, border = 'black',
             borderWidth = app.len/200, align = 'center')
    drawLabel(arrow, x, y, size = app.len/22, font = 'symbols',
              fill = 'black')

def drawSettingsBox(app):
    drawSettingsBorder(app)
    drawLabel('Difficulty', app.width/2, app.height/2 - app.len/2.662, 
              size = app.len/20, font = 'Georgia')
    drawLabel('Number of Players', app.width/2, app.height/2 - app.len/5.665,
              size = app.len/20, font = 'Georgia')
    drawLabel('Simplified Cards', app.width/2, app.height/2 + app.len/44.33,
              size = app.len/20, font = 'Georgia')
    drawLabel('Lag Reduce Mode', app.width/2, app.height/2 + app.len/4.098,
              size = app.len/20, font = 'Georgia')
    drawSettingsValues(app)
    if app.showLength in [0.65, 0.4, 0.2]:
        drawArrowButton(app, '\u2190', app.width/2 - app.len/3.5,
                        app.height/2 - app.len/3.623)
    if app.showLength in [0.65, 1, 0.4]:
        drawArrowButton(app, '\u2192', app.width/2 + app.len/3.5,
                        app.height/2 - app.len/3.623)
    if app.pendingPlayers > 2:
        drawArrowButton(app, '\u2190', app.width/2 - app.len/3.5,
                        app.height/2 - app.len/12.99)
    if app.pendingPlayers < 4:
        drawArrowButton(app, '\u2192', app.width/2 + app.len/3.5,
                        app.height/2 - app.len/12.99)

def drawSettingsBorder(app):
    drawRect(0, 0, app.width, app.height, fill = 'white', opacity = 25)
    drawRect(app.width/2,app.height/2,app.len/1.15,app.len/1.15,
             align='center', fill='white', border='black',
             borderWidth=app.len/100)
    drawRect(app.width/2 + app.len/2.3 - app.len/40 - app.len/20, app.height/2 
                - app.len/2.3+app.len/40,app.len/20,app.len/20, fill = 'red')
    drawLabel('X', app.width/2 + app.len/2.3 - app.len/20, app.height/2 -
                app.len/2.3 + app.len/20, size = app.len/20, fill = 'white')

def drawSettingsValues(app):
    if app.showLength == 1: difficulty = 'Easy'
    elif app.showLength == 0.65: difficulty = 'Medium'
    elif app.showLength == 0.4: difficulty = 'Hard'
    elif app.showLength == 0.2: difficulty = 'Impossible'
    cards = 'Off' if app.realCards else 'On'
    lags = 'On' if app.lagReduce else 'Off'
    drawRect(app.width/2, app.height/2 + app.len/7.502, app.len/5, app.len/10,
             fill = 'white', border = 'black', borderWidth = app.len/150,
             align = 'center')
    drawRect(app.width/2, app.height/2 + app.len/2.819, app.len/5, app.len/10,
             fill = 'white', border = 'black', borderWidth = app.len/150,
             align = 'center')
    drawLabel(cards, app.width/2, app.height/2 + app.len/7.502,
              size = app.len/15, font = 'Georgia')
    drawLabel(difficulty, app.width/2, app.height/2 - app.len/3.623,
              size = app.len/15, font = 'Georgia')
    drawLabel(f'{app.pendingPlayers}', app.width/2,
              app.height/2 - app.len/12.99,
              size = app.len/15, font = 'Georgia')
    drawLabel(lags, app.width/2, app.height/2 + app.len/2.819,
              size = app.len/15, font = 'Georgia')

def stickPossible(app):
    return (not app.gameOver and not app.playerDrawingCard and not
        app.lookingAtCard and not app.holdingDrawnCard and not
        app.viewingBottomCards and app.osherCaller != 0 and not
        app.sevenOrEight and not app.nineOrTen and not app.king
        and not app.jackOrQueen and not app.displayStickOpponentMessage
        and not app.cardsMoving and not app.cardMoving)

def drawMessages(app):
    drawLabel(app.message, app.width/2, app.height/18, size=app.len/25,
              font = 'Georgia')
    if app.gameOver:
        drawLabel('Press n to start a new game.', app.width/2, app.height/7.5,
                  size = app.len/25, font = 'Georgia')
    elif (app.osherCaller != None and app.osherCaller != 0 and 
          stickPossible(app)):
        drawLabel(f'{computerName(app, app.osherCaller)} called Osher! \
(You cannot stick them).', app.width/2, app.height/7.5, size = app.len/25,
                  font = 'Georgia')
    elif stickPossible(app):
        drawLabel('Click on any card to stick.', app.width/2, app.height/7.5,
                  size = app.len/25, font = 'Georgia')
    elif app.osherCaller == 0:
        drawLabel('You called Osher! (You cannot stick any cards.)', 
                  app.width/2, app.height/7.5, size = app.len/25,
                  font = 'Georgia')
    elif app.playerDrawingCard:
        drawLabel("Press o to call Osher.", app.width/2, app.height/7.5,
                  size = app.len/25, font = 'Georgia')
    elif app.holdingDrawnCard and not app.isTopCard:
        drawLabel("Press d to discard this card.", app.width/2, app.height/7.5,
                  size = app.len/25, font = 'Georgia')
    elif ((app.sevenOrEight or app.nineOrTen or app.jackOrQueen or app.king) and
          not app.lookingAtCard and not app.cardsMoving):
        drawLabel("Press r to skip this action.", app.width/2, app.height/7.5, 
                  size = app.len/25, font = 'Georgia')
    elif app.cardsMoving:
        drawLabel("Swapping cards...", app.width/2, app.height/7.5, 
                  size = app.len/25, font = 'Georgia')

def drawTable(app,d):
    if app.showLength == 1: 
        drawImage(app.easyBackground,0,0,align='left-top')
    elif app.showLength == 0.65: 
        drawImage(app.mediumBackground,0,0,align='left-top')
    elif app.showLength == 0.4: 
        drawImage(app.hardBackground,0,0,align='left-top')
    elif app.showLength == 0.2: 
        drawImage(app.impossibleBackground,0,0,align='left-top')
    drawImage(app.tableImage, app.width/2, app.height/2 + app.len/11,
                align='center')
    drawCircle(app.width/2, app.height/2 + app.len/11,
               app.len/2 - app.len/8.5, border = 'black', fill=None,
               borderWidth = app.len/100)
    drawCenterCards(app, d)
    drawCards(app)

def drawDrawnCard(app):
    if not app.realCards:
        drawRect(app.width/2,app.height/2 + app.len/15,app.len/6,app.len/4,
                align='center', fill = 'white', border='black',
                borderWidth = app.len/100)
        cardColor = 'red' if app.cardBeingSeen[1] in 'dh' else 'black'
        cardNumber = app.cardBeingSeen[0] if app.cardBeingSeen[0]!='T' else '10'
        drawLabel(cardNumber,app.width/2, app.height/2 + app.len/75,
                size = app.len/9, fill=cardColor, font = 'Times New Roman')
        drawLabel(getSuit(app.cardBeingSeen[1]), app.width/2,
                app.height/2 + app.len/9 + app.len/500, size = app.len/7.5, 
                fill=cardColor, font='symbols')
    else:
        i = getRealCardIndex(app.cardBeingSeen)
        drawRect(app.width/2,app.height/2 + app.len/15,app.len/5.8,app.len/4,
                align='center', fill = 'white')
        drawImage(app.cardFacesFull[app.cardBeingSeen[1]][i], app.width/2,
                app.height/2 + app.len/15, width = app.len/6, 
                height = app.len/4,align='center')
    
def drawStickMessages(app):
    if app.displayStickMessages[0]:
        drawRect(app.width/2,app.height/2 + app.len/6, app.len/5, app.len/10, 
                 align='center', fill = 'white', border = 'black', 
                 borderWidth = app.len/150)
        drawLabel('Stick!', app.width/2, app.height/2 + app.len/6, 
                  size = app.len/15)
    if app.displayStickMessages[1]:
        drawRect(app.width/2 + app.len/4.4,app.height/2+app.len/11, app.len/6.5, 
                 app.len/13, align='center',fill='white',border='black',
                 borderWidth = app.len/150)
        drawLabel('Stick!',app.width/2 + app.len/4.4,app.height/2+app.len/11,
                  size=app.len/20)
    if app.displayStickMessages[2]:
        drawRect(app.width/2,app.height/2-app.len/7.5, app.len/6.5,
                 app.len/13, align='center',fill='white',border='black',
                 borderWidth = app.len/150)
        drawLabel('Stick!',app.width/2,app.height/2-app.len/7.5, 
                  size=app.len/20)
    if app.displayStickMessages[3]:
        drawRect(app.width/2 - app.len/4.4,app.height/2+app.len/11, app.len/6.5, 
                 app.len/13, align='center',fill='white',border='black',
                 borderWidth = app.len/150)
        drawLabel('Stick!',app.width/2 - app.len/4.4,app.height/2+app.len/11,
                  size=app.len/20)

def drawMistakeMessages(app):
    if app.displayMistakeMessages[0]:
        drawRect(app.width/2,app.height/2 + app.len/5, app.len/3.5, app.len/10, 
                 align='center', fill = 'white', border = 'black', 
                 borderWidth = app.len/150)
        drawLabel('Mistake!', app.width/2, app.height/2 + app.len/5, 
                  size = app.len/15)
    if app.displayMistakeMessages[1]:
        drawRect(app.width/2 + app.len/4.4,app.height/2+app.len/11, app.len/4.6, 
                 app.len/13, align='center',fill='white',border='black',
                 borderWidth = app.len/150)
        drawLabel('Mistake!',app.width/2 + app.len/4.4,app.height/2+app.len/11,
                  size=app.len/20)
    if app.displayMistakeMessages[2]:
        drawRect(app.width/2,app.height/2-app.len/7.5, app.len/4.6,
                 app.len/13, align='center',fill='white',border='black',
                 borderWidth = app.len/150)
        drawLabel('Mistake!',app.width/2,app.height/2-app.len/7.5, 
                  size=app.len/20)
    if app.displayMistakeMessages[3]:
        drawRect(app.width/2 - app.len/4.4,app.height/2+app.len/11, app.len/4.6, 
                 app.len/13, align='center',fill='white',border='black',
                 borderWidth = app.len/150)
        drawLabel('Mistake!',app.width/2 - app.len/4.4,app.height/2+app.len/11,
                  size=app.len/20)

def displayTimedMessages(app):
    drawStickMessages(app)
    drawMistakeMessages(app)
    if app.displayStickOpponentMessage:
        drawRect(app.width/2, app.height/2 - app.len/10, app.len/1.8, app.len/6,
                 align = 'center',fill='white',border='black',
                 borderWidth = app.len/100)
        drawLabel('Select a card to give',app.width/2,
                  app.height/2 - app.len/7.4, size=app.len/18)
        drawLabel('to your opponent!',app.width/2,app.height/2-app.len/13.5,
                  size=app.len/18)

def drawUI(app):
    drawRect(0,0,app.width,app.height/5.3,opacity=25,fill='white')
    drawImage(app.rulesButton,app.width/10, app.height/10, align = 'center')
    drawImage(app.settingsButton, app.width - app.width/9, app.height/10, 
              align = 'center')
    drawLabel('Rules',app.width/10,app.height/10.5,
              fill='white', size=app.len/20, font = 'Georgia')
    drawLabel('Settings',app.width - app.width/9, app.height/10.5,
              fill='white', size=app.len/20, font = 'Georgia')
    drawComputerPlayerLabels(app)

def drawComputerPlayerLabels(app):
    if handActive(app, 2):
        drawRect(app.width/2, app.height/2 - app.len/3.65, app.len/5.5,
             app.len/20, fill = 'yellow' if app.player == 2 else 'gray', 
             border = 'black' if app.osherCaller != 2 else 'cyan',
             borderWidth = app.len/250, align = 'center')
    if handActive(app, 1):
        drawRect(app.width/2 + app.len/4.4, app.height/2 - app.len/60,
             app.len/5.5,
             app.len/20, fill = 'yellow' if app.player == 1 else 'gray', 
             border = 'black' if app.osherCaller != 1 else 'cyan', 
             borderWidth = app.len/250, align = 'center')
    if handActive(app, 3):
        drawRect(app.width/2 - app.len/4.4, app.height/2 - app.len/60,
             app.len/5.5,
             app.len/20, fill = 'yellow' if app.player == 3 else 'gray', 
             border = 'black' if app.osherCaller != 3 else 'cyan', 
             borderWidth = app.len/250, align = 'center')
    drawRect(app.width/2, app.height - app.len/20, app.len/7, app.len/20,
             align = 'center', fill = 'yellow' if app.player == 0 else 'gray',
             border = 'black' if app.osherCaller != 0 else 'cyan', 
             borderWidth = app.len/250)
    if handActive(app, 1):
        drawLabel(computerName(app, 1), app.width/2 + app.len/4.4,
              app.height/2-app.len/55, font = 'Georgia', size = app.len/35)
    if handActive(app, 2):
        drawLabel(computerName(app, 2), app.width/2,
              app.height/2 - app.len/3.62, font = 'Georgia',
              size = app.len/35)
    if handActive(app, 3):
        drawLabel(computerName(app, 3), app.width/2 - app.len/4.4,
              app.height/2-app.len/55, font = 'Georgia', size = app.len/35)
    drawLabel('Player', app.width/2, app.height - app.len/19,font='georgia',
              size = app.len/35)

def drawCover(app):
    drawImage(app.coverImage,0,0,align='left-top',width=app.width,
              height=app.height)
    drawRect(0,0,app.width,app.height,fill='white',opacity=15)
    drawImage(app.wordmark,app.width - app.len/2.7, app.height/20,
              height = app.len/2.7 - app.len/20, width = app.len/2.7 - 
              app.len/20)
    drawLabel("Osher", app.width/2 + app.len/2.3, app.height/2 + app.len/10,
              size = app.len/5,font = 'felix titling')
    drawLabel("A card game", app.width/2 + app.len/2.8, app.height/2+app.len/4,
              size = app.len/9, font = 'felix titling')
    drawLabel("Created with cmu graphics", app.width/2 + app.len/5,
              app.height/2+app.len/2.85, size=app.len/14, font='felix titling')
    drawLabel("Press any key to continue", app.width/2, app.height - app.len/16,
              size = app.len/25, font = 'malgun gothic')

def redrawAll(app):
    drawTable(app,app.len/200)
    drawUI(app)
    drawMessages(app)
    if app.holdingDrawnCard: drawDrawnCard(app)
    displayTimedMessages(app)
    if app.viewingRules: drawRuleBox(app)
    if app.viewingSettings: drawSettingsBox(app)
    if app.displayCover: drawCover(app)

def checkDrawnCard(app, mouseX, mouseY):
    topY = app.height/2 + app.len/11 - app.len/20
    if topY < mouseY < topY + app.len/10:
        xDraw = app.width/2 - app.len/200 - app.len/15
        xDiscard = app.width/2 + app.len/200
        if xDraw < mouseX < xDraw + app.len/15:
            app.cardBeingSeen = dealCard(app)
            app.playerDrawingCard = False
            app.holdingDrawnCard = True
            app.message = 'Click on one of your cards to replace.'
        elif ((xDiscard < mouseX < xDiscard + app.len/15) and 
              app.cards[0] != [None]*6):
            app.cardBeingSeen = app.topCard
            computersStick(app)
            app.playerDrawingCard = False
            app.holdingDrawnCard = True
            app.isTopCard = True
            app.message = 'Click on one of your cards to replace.'

def getClickedPlayerCard(app,mouseX,mouseY):
    for card in app.cards[0]:
        if card == None: continue
        if card.clicked(mouseX,mouseY): return card

def getClickedNonPlayerCard(app,mouseX,mouseY):
    for i in computerHands(app):
        for card in app.cards[i]:
            if card == None: continue
            if card.clicked(mouseX,mouseY): return card

def getAnyPressedCard(app,mouseX,mouseY):
    if getClickedPlayerCard(app,mouseX,mouseY) != None:
        return getClickedPlayerCard(app,mouseX,mouseY)
    if getClickedNonPlayerCard(app,mouseX,mouseY) != None:
        return getClickedNonPlayerCard(app,mouseX,mouseY)

def checkForRulesClick(app,mouseX,mouseY):
    if (app.width/2 + app.width/3 - app.len/40 - app.len/20 < mouseX <
        app.width/2 + app.width/3 - app.len/40 and
        app.height/2 - app.height/3 + app.len/40 < mouseY <
        app.height/2 - app.height/3 + app.len/40 + app.len/20):
        app.viewingRules = False
    elif (app.width/2 + app.width/3 - app.len/20 - app.len/40 < mouseX < 
          app.width/2 + app.width/3 - app.len/40 and
          app.height/2 - app.height/3 + app.len/12 < mouseY < 
          app.height/2 - app.height/3 + app.len/12 + app.len/20) and (
          app.rulePosition > 0):
        app.rulePosition -= 1
    elif (app.width/2 + app.width/3 - app.len/20 - app.len/40 < mouseX <
          app.width/2 + app.width/3 - app.len/40 and
          app.height/2 + app.height/3 - app.len/12 < mouseY <
          app.height/2 + app.height/3 - app.len/12 + app.len/20) and (
          app.rulePosition < len(app.rules.splitlines()) - 15):
        app.rulePosition += 1

def doSwap(app,mouseX,mouseY):
    card = getAnyPressedCard(app, mouseX, mouseY)
    if card == None: return
    if card.i == app.osherCaller: return
    if not app.firstCardSelected:
        app.firstCardSelected = True
        app.firstCard = card
        app.cardsHighlighted.add((app.firstCard.i,app.firstCard.j))
        app.message = 'Press on the second card you want to swap.'
    elif not app.secondCardSelected and app.firstCardSelected:
        app.secondCardSelected = True
        app.secondCard = card
        app.cardsHighlighted.add((app.secondCard.i,app.secondCard.j))
        app.message = 'Press s to swap the cards.'

def doKingView(app,mouseX,mouseY):
    card = getAnyPressedCard(app, mouseX, mouseY)
    if card == None: return
    if card.i == app.osherCaller: return
    if not app.firstCardSelected:
        app.firstCardSelected = True
        app.firstCard = card
        app.cardsHighlighted.add((app.firstCard.i,app.firstCard.j))
        app.message = 'Press on the second card you want to view.'
    elif not app.secondCardSelected and app.firstCardSelected:
        app.secondCardSelected = True
        app.secondCard = card
        app.cardsHighlighted.remove((app.firstCard.i,app.firstCard.j))
        app.cardsShown.add((app.firstCard.i,app.firstCard.j))
        app.cardsShown.add((app.secondCard.i,app.secondCard.j))
        app.message = 'Press f to finish viewing these cards.'

def giveMistakeCard(app):
    seenIndices = set()
    for i in range(len(app.cards[0])):
        if app.cards[0][i] != None: seenIndices.add(i)
    if len(seenIndices) == 6:
        app.gameOver = True
        app.message = 'Game over! You got more than 6 cards.'
    else:
        for i in range(6):
            if i not in seenIndices:
                app.cards[0][i] = Card(dealCard(app),0,i,app)
                break
    app.displayMistakeMessages[0] = True
    wait(app, 1, lambda app: disableMistakeMessage(app))

def disableMistakeMessage(app, player = 0):
    app.displayMistakeMessages[player] = False

def disableStickMessage(app, player = 0):
    app.displayStickMessages[player] = False

def hideCard(i, j, app):
    if (i,j) in app.cardsShown:
        app.cardsShown.remove((i,j))

def unHighlightCard(app, i = None, j = None):
    if i == None and j == None:
        app.cardsHighlighted = set()
    if (i,j) in app.cardsHighlighted:
        app.cardsHighlighted.remove((i,j))

def evalStick(app, card):
    if card == None: return
    if card.i == app.osherCaller: return
    if card.i == 0 and app.sticker in [None,0]:
        if app.topCard == card:
            app.topCard = card.value
            app.cards[card.i][card.j] = None
            app.displayStickMessages[0] = True
            app.sticker = 0
            wait(app, app.showLength, lambda app: disableStickMessage(app))
        else:
            card.computerKnows = [None] + [True]*3
            app.cardsShown.add((card.i,card.j))
            wait(app, app.showLength, lambda app: hideCard(card.i, card.j, app))
            giveMistakeCard(app)
    elif card.i != 0 and app.sticker in [None,0]:
        if app.topCard == card:
            app.topCard = card.value
            app.cards[card.i][app.cards[card.i].index(card)] = None
            app.displayStickOpponentMessage = True
            app.opponentStuck = card.i
            app.sticker = 0
        else:
            card.computerKnows = [None] + [True]*3
            app.cardsShown.add((card.i,card.j))
            wait(app, app.showLength, lambda app: hideCard(card.i, card.j, app))
            giveMistakeCard(app)
    elif app.sticker not in [None,0]:
        app.cardsShown.add((card.i,card.j))
        wait(app, app.showLength, lambda app: hideCard(card.i, card.j, app))
        giveMistakeCard(app)

def evalDrawnCard(app, mouseX, mouseY):
    card = getClickedPlayerCard(app, mouseX, mouseY)
    if card == None: return
    app.tempCardShown = app.isTopCard
    if app.isTopCard: app.topCard = None
    app.tempCard = createTempCard(app, 0, card.j, app.cardBeingSeen)
    app.tempCardMoving = True
    app.targetI = 0
    app.targetJ = card.j
    app.sticker = None
    computersStick(app)
    app.holdingDrawnCard = False
    app.isTopCard = False
    app.message = 'Press e to end your turn.'

def evalCardPowers(app, mouseX, mouseY):
    if app.sevenOrEight and not app.lookingAtCard:
        card = getClickedPlayerCard(app, mouseX, mouseY)
        if card != None:
            app.cardsShown.add((0,card.j))
            app.lookingAtCard = True
            app.message = 'Press f to finish viewing this card.'
    elif app.nineOrTen and not app.lookingAtCard:
        card = getClickedNonPlayerCard(app, mouseX, mouseY)
        if card != None:
            app.cardsShown.add((card.i,card.j))
            app.lookingAtCard = True
            app.message = 'Press f to finish viewing this card.'
    elif app.jackOrQueen and not (app.firstCardSelected and 
                                    app.secondCardSelected):
        doSwap(app,mouseX,mouseY)
    elif (app.king and not (app.firstCardSelected and 
                            app.secondCardSelected) and not app.kingViewed):
        doKingView(app,mouseX,mouseY)
    elif (app.king and not (app.firstCardSelected and
                            app.secondCardSelected) and app.kingViewed):
        doSwap(app,mouseX,mouseY)

def giveCard(app, mouseX, mouseY):
    card = getClickedPlayerCard(app,mouseX,mouseY)
    if card != None:
        indicesSeen = set()
        for i in range(len(app.cards[app.opponentStuck])):
            if app.cards[app.opponentStuck][i] != None: indicesSeen.add(i)
        for i in range(6):
            if i not in indicesSeen:
                app.cardMoving = True
                app.movingCard = card
                app.targetI = app.opponentStuck
                app.targetJ = i
                app.displayStickOpponentMessage = False
                break
        updateCards(app)

def checkForGameClick(app, mouseX, mouseY):
    if (app.width/10 - app.len/7.5 < mouseX < 
        app.width/10 - app.len/7.5 + app.len/3.75 and 
        app.height/10 - app.len/20 < mouseY < 
        app.height/10 - app.len/20 + app.len/10):
        app.viewingRules = True
        app.rulesPosition = 0
    elif (app.width - app.width/9 - app.len/6.5 < mouseX < 
          app.width - app.width/9 - app.len/6.5 + app.len/3.25 and 
          app.height/10 - app.len/20 < mouseY < 
          app.height/10 - app.len/20 + app.len/10):
        app.viewingSettings = True
    if app.player == 0 and app.playerDrawingCard:
        checkDrawnCard(app, mouseX, mouseY)
    if app.holdingDrawnCard: evalDrawnCard(app, mouseX, mouseY)
    elif stickPossible(app):
        cardIndex = getAnyPressedCard(app, mouseX, mouseY)
        evalStick(app, cardIndex)
    evalCardPowers(app, mouseX, mouseY)

def checkForSettingsClick(app, mouseX, mouseY):
    if (app.width/2 + app.len/2.3 - app.len/40 - app.len/20 < mouseX <
        app.width/2 + app.len/2.3 - app.len/40 and
        app.height/2 - app.len/2.3 + app.len/40 < mouseY <
        app.height/2 - app.len/2.3 + app.len/40 + app.len/20):
        app.viewingSettings = False
    if (app.width/2 - app.len/3.5 - app.len/28 < mouseX < 
        app.width/2 - app.len/3.5 + app.len/28 and
        app.height/2 - app.len/3.623 - app.len/28 < mouseY <
        app.height/2 - app.len/3.623 + app.len/28):
        if app.showLength == 0.65: app.showLength = 1
        elif app.showLength == 0.4: app.showLength = 0.65
        elif app.showLength == 0.2: app.showLength = 0.4
    if (app.width/2 + app.len/3.5 - app.len/28 < mouseX <
        app.width/2 + app.len/3.5 + app.len/28 and
        app.height/2 - app.len/3.623 - app.len/28 < mouseY <
        app.height/2 - app.len/3.623 + app.len/28):
        if app.showLength == 0.65: app.showLength = 0.4
        elif app.showLength == 1: app.showLength = 0.65
        elif app.showLength == 0.4: app.showLength = 0.2
    if (app.width/2 - app.len/3.5 - app.len/28 < mouseX <
        app.width/2 - app.len/3.5 + app.len/28 and
        app.height/2 - app.len/12.99 - app.len/28 < mouseY <
        app.height/2 - app.len/12.99 + app.len/28):
        if app.pendingPlayers > 2:
            setPlayers(app, app.pendingPlayers - 1)
    if (app.width/2 + app.len/3.5 - app.len/28 < mouseX <
        app.width/2 + app.len/3.5 + app.len/28 and
        app.height/2 - app.len/12.99 - app.len/28 < mouseY <
        app.height/2 - app.len/12.99 + app.len/28):
        if app.pendingPlayers < 4:
            setPlayers(app, app.pendingPlayers + 1)
    if (app.width/2 - app.len/10 < mouseX < app.width/2 + app.len/10 and
        app.height/2 + app.len/7.502 - app.len/20 < mouseY <
        app.height/2 + app.len/7.502 + app.len/20):
        app.realCards = not app.realCards
    if (app.width/2 - app.len/10 < mouseX < app.width/2 + app.len/10 and
        app.height/2 + app.len/2.819 - app.len/20 < mouseY <
        app.height/2 + app.len/2.819 + app.len/20):
        app.lagReduce, app.cardsMoused = not app.lagReduce, set()
        app.stepsPerSecond = 12

def setPlayers(app, number):
    app.pendingPlayers = number
    app.gameOver = True
    app.message = f'Players set to {number}.'

def onMousePress(app, mouseX, mouseY):
    if app.displayCover: app.displayCover = False
    elif app.viewingRules: checkForRulesClick(app,mouseX,mouseY)
    elif app.viewingSettings: checkForSettingsClick(app,mouseX,mouseY)
    elif not app.displayStickOpponentMessage: checkForGameClick(app,
                                                                mouseX, mouseY) 
    else: giveCard(app, mouseX, mouseY)

def playerToMove(app):
    return (app.player == 0 and not app.gameOver and not
    app.holdingDrawnCard and not
    app.viewingRules and not app.viewingBottomCards and not
    app.playerDrawingCard and not app.sevenOrEight and not
    app.nineOrTen and not app.jackOrQueen and not app.king)

def processGameStart(app):
    app.gameOver = False
    app.viewingRules = False
    app.viewingBottomCards = True
    hands = activeHands(app)
    app.player = hands[random.randint(0, len(hands) - 1)]
    app.nextPlayer = nextHand(app, app.player)
    app.cardsShown.add((0,2))
    app.cardsShown.add((0,3))
    app.message = 'Press f to finish looking at your cards.'

def checkForPowers(app):
    app.topCard = app.cardBeingSeen
    app.sticker = None
    app.holdingDrawnCard = False
    if not app.isTopCard:
        if app.topCard[0] in '78': app.sevenOrEight = True
        elif app.topCard[0] in '9T': app.nineOrTen = True
        elif app.topCard[0] in 'JQ': app.jackOrQueen = True
        elif app.topCard[0] == 'K': app.king = True
    if app.sevenOrEight: 
        app.message = 'Click on one of your cards to view it.'
    elif app.nineOrTen:
        app.message = "Click on one of your opponent's cards to view it."
    elif app.jackOrQueen:
        app.message = "Click on the first card you want to swap."
    elif app.king: 
        app.message = "Click on the first card you want to view."
    else: app.message = 'Press e to end your turn.'
    computersStick(app)
    
def moveCardsStep(app, firstCard, secondCard, time):
    coords = loadCoords(app)
    steps = int(time * app.stepsPerSecond)
    if steps < 1: steps = 1
    liveFirst = app.cards[firstCard.i][firstCard.j]
    liveSecond = app.cards[secondCard.i][secondCard.j]
    if liveFirst == None or liveSecond == None:
        app.swapProgress = app.swapStart = None
        app.cardsMoving = False
        app.firstCard = app.secondCard = None
        return
    if app.swapProgress == None:
        app.swapProgress = 0
        app.swapStart = (liveFirst.left, liveFirst.top,
                         liveSecond.left, liveSecond.top)
    app.swapProgress += 1
    t = min(1, app.swapProgress / steps)
    if t >= 1:
        app.swapProgress = app.swapStart = None
        app.cardsMoving = False
        app.firstCard = app.secondCard = None
        firstCard = copy.deepcopy(firstCard)
        secondCard = copy.deepcopy(secondCard)
        switchCards(app, firstCard, secondCard)
        updateCards(app)
        app.cardsHighlighted = set()
        if app.jackOrQueen or app.king:
            app.firstCardSelected, app.secondCardSelected = False, False
            app.jackOrQueen, app.king = False, False
            app.message = 'Press e to end your turn.'
    else:
        firstX0, firstY0, secondX0, secondY0 = app.swapStart
        firstX1 = coords[secondCard.i*2][secondCard.j]
        firstY1 = coords[secondCard.i*2 + 1][secondCard.j]
        secondX1 = coords[firstCard.i*2][firstCard.j]
        secondY1 = coords[firstCard.i*2 + 1][firstCard.j]
        liveFirst.left = firstX0 + (firstX1 - firstX0) * t
        liveFirst.top = firstY0 + (firstY1 - firstY0) * t
        liveSecond.left = secondX0 + (secondX1 - secondX0) * t
        liveSecond.top = secondY0 + (secondY1 - secondY0) * t

def moveCardStep(app, card, i, j, time):
    if app.movingCard == None: return
    coords = loadCoords(app)
    steps = int(time * app.stepsPerSecond)
    if steps < 1: steps = 1
    liveCard = app.cards[card.i][card.j]
    if liveCard == None:
        app.moveProgress = app.moveStart = None
        app.cardMoving = False
        app.movingCard = app.targetI = app.targetJ = None
        return
    if app.moveProgress == None:
        app.moveProgress = 0
        app.moveStart = (liveCard.left, liveCard.top)
    app.moveProgress += 1
    t = min(1, app.moveProgress / steps)
    if t >= 1:
        app.moveProgress = app.moveStart = None
        app.cardMoving = False
        app.movingCard = app.targetI = app.targetJ = None
        card = copy.deepcopy(card)
        app.cards[card.i][card.j] = None
        card.i, card.j = i, j
        app.cards[card.i][card.j] = card
        updateCards(app)
    else:
        x0, y0 = app.moveStart
        x1, y1 = coords[i*2][j], coords[i*2 + 1][j]
        liveCard.left = x0 + (x1 - x0) * t
        liveCard.top = y0 + (y1 - y0) * t

def moveTempCardStep(app, i, j, time, shown):
    coords = loadCoords(app)
    steps = int((time/1.3) * app.stepsPerSecond)
    if steps < 1: steps = 1
    if app.tempCard == None:
        app.tempProgress = app.tempStart = None
        app.tempCardMoving = False
        return
    i, j = app.tempCard.i, app.tempCard.j
    if app.tempProgress == None:
        app.tempProgress = 0
        app.tempStart = (app.tempCard.left, app.tempCard.top)
    app.tempProgress += 1
    t = min(1, app.tempProgress / steps)
    if t >= 1:
        app.tempProgress = app.tempStart = None
        if app.cards[i][j] == None:
            app.topCard = app.tempCard.value
            app.tempCard = None
            app.tempCardShown = False
            app.tempCardMoving = False
            return
        app.topCard = app.cards[i][j].value
        app.cards[i][j].value = app.tempCard.value
        if shown: app.cards[i][j].computerKnows = [None] + [True]*3
        else:
            app.cards[i][j].computerKnows = [None] + [False]*3
            if i != 0: app.cards[i][j].computerKnows[i] = True
        app.cardsHighlighted.add((i,j))
        wait(app, app.showLength, lambda app: unHighlightCard(app,i,j))
        app.tempCard = None
        app.tempCardShown = False
        app.tempCardMoving = False
    else:
        x0, y0 = app.tempStart
        x1, y1 = coords[i*2][j], coords[i*2 + 1][j]
        app.tempCard.left = x0 + (x1 - x0) * t
        app.tempCard.top = y0 + (y1 - y0) * t

def processPowerActions(app, key):
    if ((app.sevenOrEight or app.nineOrTen or app.jackOrQueen or 
        app.king) and key == 'r' and not app.lookingAtCard and
        not app.cardsMoving):
        app.message = 'Press e to end your turn.'
        app.sevenOrEight, app.nineOrTen = False, False
        app.jackOrQueen, app.king = False, False
        app.lookingAtCard = False
        app.kingViewed = False
        app.firstCardSelected, app.secondCardSelected = False, False
        app.firstCard = app.secondCard = None
        app.cardsShown = set()
        app.cardsHighlighted = set()
    if ((app.sevenOrEight or app.nineOrTen) and 
        key == 'f' and app.lookingAtCard):
        app.sevenOrEight, app.nineOrTen = False, False
        app.lookingAtCard = False
        app.cardsShown = set()
        app.message = 'Press e to end your turn.'
    if (app.jackOrQueen and key == 's' and app.firstCardSelected 
        and app.secondCardSelected): app.cardsMoving = True
    if (app.king and key == 'f' and app.firstCardSelected 
        and app.secondCardSelected and not app.kingViewed):
        app.cardsShown = set()
        app.firstCardSelected, app.secondCardSelected = False, False
        app.message = 'Click the first card you want to swap.'
        app.kingViewed = True
    elif (app.king and key == 's' and app.firstCardSelected and
            app.secondCardSelected and app.kingViewed): app.cardsMoving = True

def checkForRulesSettingsPress(app,key):
    if key == 'x': app.viewingRules = app.viewingSettings = False

def beginGame(app, key):
    if app.viewingBottomCards and key == 'f':
        app.viewingBottomCards = False
        app.cardsShown.remove((0,2))
        app.cardsShown.remove((0,3))
        if app.player == 0: 
            app.message = 'Click on the draw or discard pile to draw a card.'
            app.playerDrawingCard = True
        else: computerTakeTurn(app, app.player)
    if app.player == 0 and key == 'o' and app.playerDrawingCard: 
        app.osherCaller = 0
        app.player = nextHand(app, 0)
        computerTakeTurn(app, app.player)
        app.playerDrawingCard = False

def beginPlayerTurn(app):
    app.firstCardSelected = False
    app.secondCardSelected = False
    app.kingViewed = False
    app.holdingDrawnCard = False
    app.sevenOrEight = False
    app.nineOrTen = False
    app.jackOrQueen = False
    app.king = False
    app.isTopCard = False
    app.playerDrawingCard = True
    app.message = 'Click on the draw or discard pile to draw a card.'
    app.cardsMoused = set()

def checkForGamePress(app,key):
    if app.gameOver and key == 'n':
        startNewGame(app)
        processGameStart(app)
    elif app.playerDrawingCard and key == 'o':
        app.osherCaller = 0
        computerTakeTurn(app, nextHand(app, 0))
        app.playerDrawingCard = False
    elif app.holdingDrawnCard and key == 'd' and not app.isTopCard:
        checkForPowers(app)
    elif (playerToMove(app) and key == 'e'):
        app.player = nextHand(app, 0)
        computerTakeTurn(app, app.player)
    processPowerActions(app, key)
    beginGame(app, key)
    
def onKeyPress(app, key):
    if app.displayCover: app.displayCover = False
    elif app.viewingRules or app.viewingSettings: 
        checkForRulesSettingsPress(app,key)
    else: checkForGamePress(app,key)

def onKeyHold(app, keys):
    if app.viewingRules:
        if 'up' in keys and 'down' in keys: return
        elif 'up' in keys and app.rulePosition > 0: app.rulePosition -= 1
        elif ('down' in keys and app.rulePosition < 
              len(app.rules.splitlines()) - 15):
            app.rulePosition += 1
            app.displayArrowMessage = False

def wait(app, delayInSeconds, event):
    delayInSteps = int(delayInSeconds * app.stepsPerSecond)
    app.timers.append([delayInSteps, event])

def processTimers(app):
    activeTimers = []
    for timer in app.timers:
        timer[0] -= 1
        if timer[0] <= 0: timer[1](app)
        else: activeTimers.append(timer)
    app.timers = activeTimers

def scoreCard(cardValue):
    if cardValue[0] == 'A': return 1
    elif cardValue[0] in '23456789': return int(cardValue[0])
    elif cardValue[0] == 'T': return 10
    elif cardValue[0] == 'K' and cardValue[1] in 'hd': return -1
    elif cardValue[0] in 'JQK': return 10

def osherChance(score):
    chanceOfCalling = math.pow(0.1, (score + 2) / 7)
    if chanceOfCalling > 1: chanceOfCalling = 1
    return chanceOfCalling

def considersOsher(app, player):
    for card in app.cards[player]:
        if card == None: continue
        if not card.computerKnows[player]: return chance(0.05)
    return True

def computerTakeTurn(app, player):
    app.player = player
    app.nextPlayer = nextHand(app, app.player)
    if app.osherCaller == player: 
        endGame(app)
        return
    if player == 0:
        beginPlayerTurn(app)
        return
    app.message = f'{computerName(app, player)} is drawing...'
    score = scoreHand(app, player)
    if (considersOsher(app, player) and score < 5
        and chance(osherChance(score))):
        wait(app, app.showLength*2, lambda app: assignOsherCaller(app, player))
        wait(app, app.showLength*2,
                   lambda app: computerTakeTurn(app, app.nextPlayer))
    else:
        wait(app, app.showLength*2, 
             lambda app: computerDrawCard(app, player))

def assignOsherCaller(app, player):
    if app.osherCaller == None:
        app.osherCaller = player

def endGame(app):
    app.gameOver = True
    L = []
    for i in range(4):
        if handActive(app, i): L.append(scoreHand(app, i))
        else: L.append(10000)
    playerScore = L[0]
    winnerScore = min(L)
    winnersStr = None
    if L.count(winnerScore) > 1: winnersStr = processTie(app, winnerScore, L)
    else: winner = L.index(min(L))
    if winnersStr != None and isinstance(winnersStr, int): 
        winner = winnersStr
        winnersStr = None
    app.cardsShown = set({(0,0), (0,1), (0,2), (0,3), (0,4), (0,5),
                          (1,0), (1,1), (1,2), (1,3), (1,4), (1,5),
                          (2,0), (2,1), (2,2), (2,3), (2,4), (2,5),
                          (3,0), (3,1), (3,2), (3,3), (3,4), (3,5)})
    if winnersStr != None:
        app.message = f'There was a tie! {winnersStr} scored {winnerScore}.'
        return
    app.player = winner
    if winner == 0: 
        app.message = f'You win! Your score was {playerScore}.'
    else: 
        app.message = f'{computerName(app, winner)} wins! Their score was {winnerScore}.'

def processTie(app, winnerScore, L):
    winnersStr = None
    winners = set()
    for i in range(len(L)):
        if L[i] == winnerScore: winners.add(i)
    winners.discard(app.osherCaller)
    if len(winners) == 1: winner = winners.pop()
    else: 
        winners = list(winners)
        winnersStr = ''
        for i in winners:
            if i == 0: winnersStr += 'The player ' + 'and '
            else: winnersStr += computerName(app, i) + ' and '
    return winnersStr[:-5] if winnersStr != None else winner

def computerDrawCard(app, player):
    if (app.cards[player] != [None]*6 and (scoreCard(app.topCard) == -1 or 
        (scoreCard(app.topCard) <= 2 and chance(0.65)) and 
        scoreHand(app,player) > 2)): computerTakeTopCard(app, player)
    else: computerDrawDiscard(app, player)
    app.sticker = None

def computer78(app, player, drawnCard):
    app.topCard = drawnCard
    app.message = f'{computerName(app, player)} is looking at a card...'
    wait(app, app.showLength*3,
            lambda app: computerLookAtOwnCard(app, player))
    wait(app, app.showLength*3,
            lambda app: setMessage(app, 
                        f'{computerName(app, player)} is wrapping up their turn...'))
    wait(app, app.showLength*6,
            lambda app: computerTakeTurn(app, app.nextPlayer))

def computer9T(app, player, drawnCard):
    app.topCard = drawnCard
    app.message = f'{computerName(app, player)} is looking at a card...'
    wait(app, app.showLength*3,
            lambda app: computerLookAtOtherCard(app, player))
    wait(app, app.showLength*3,
            lambda app: setMessage(app, 
                        f'{computerName(app, player)} is wrapping up their turn...'))
    wait(app, app.showLength*6,
            lambda app: computerTakeTurn(app, app.nextPlayer))

def computerJQ(app, player, drawnCard):
    app.topCard = drawnCard
    app.message = f'{computerName(app, player)} is swapping cards...'
    wait(app, app.showLength*3,
            lambda app: computerDoSwap(app, player))
    wait(app, app.showLength*3,
            lambda app: setMessage(app, 
                        f'{computerName(app, player)} is wrapping up their turn...'))
    wait(app, app.showLength*6,
            lambda app: computerTakeTurn(app, app.nextPlayer))

def computerK(app, player, drawnCard):
    app.topCard = drawnCard
    app.message = f'{computerName(app, player)} is looking at 2 cards...'
    wait(app, app.showLength*3,
            lambda app: computerDoKingView(app, player))
    wait(app, app.showLength*3,
            lambda app: setMessage(app, 
                        f'{computerName(app, player)} is swapping cards...'))
    wait(app, app.showLength*6,
            lambda app: computerDoSwap(app, player))
    wait(app, app.showLength*6, 
            lambda app: setMessage(app, 
                        f'{computerName(app, player)} is wrapping up their turn...'))
    wait(app, app.showLength*9,
            lambda app: computerTakeTurn(app, app.nextPlayer))

def computerDrawDiscard(app, player):
    drawnCard = dealCard(app)
    if scoreCard(drawnCard) == -1: computerReplaceCard(app, player, drawnCard)
    elif drawnCard[0] in '78': computer78(app, player, drawnCard)
    elif drawnCard[0] in '9T': computer9T(app, player, drawnCard)
    elif drawnCard[0] in 'JQ': computerJQ(app, player, drawnCard)
    elif drawnCard[0] in 'K': computerK(app, player, drawnCard)
    elif app.cards[player] == [None]*6:
        app.topCard = drawnCard
        wait(app, app.showLength*3,
             lambda app: setMessage(app, 
                    f'{computerName(app, player)} is wrapping up their turn...'))
        wait(app, app.showLength*6,
             lambda app: computerTakeTurn(app, app.nextPlayer))
    else: computerReplaceCard(app, player, drawnCard)
    computersStick(app)

def setMessage(app, message):
    app.message = message

def computerReplaceCard(app, player, drawnCard):
    replaced = False
    if scoreCard(drawnCard) < 5:
        for card in app.cards[player]:
            if card == None: continue
            if not card.computerKnows[player] and chance(0.6):
                app.tempCardShown = False
                app.tempCard = createTempCard(app, player, card.j, app.topCard)
                app.tempCardMoving = True
                app.targetI = player
                app.targetJ = card.j
                card.computerKnows[player] = True
                replaced = True
                break
            elif (card.computerKnows[player] and scoreCard(card.value) > 
                  scoreCard(drawnCard)):
                app.tempCardShown = False
                app.tempCard = createTempCard(app, player, card.j, app.topCard)
                app.tempCardMoving = True
                app.targetI = player
                app.targetJ = card.j
                replaced = True
                break
        if not replaced: app.topCard = drawnCard
    else: app.topCard = drawnCard
    app.message = f'{computerName(app, player)} is wrapping up their turn...'
    wait(app, app.showLength*4, 
            lambda app: computerTakeTurn(app, app.nextPlayer))

def computerLookAtOtherCard(app,player):
    choices = []
    for i in activeHands(app):
        if i == player: continue
        for card in app.cards[i]:
            if card == None: continue
            if card.computerKnows[player]: continue
            choices.append((i, card.j))
    if len(choices) == 0: return
    playerLookingAt, cardLookingAt = choices[random.randint(0,len(choices)-1)]
    app.cards[playerLookingAt][cardLookingAt].computerKnows[player] = True
    app.cardsHighlighted.add((playerLookingAt,cardLookingAt))
    wait(app, app.showLength, lambda app: unHighlightCard(app, playerLookingAt,
                                                          cardLookingAt))

def computerLookAtOwnCard(app,player):
    for card in app.cards[player]:
        if card == None: continue
        if not card.computerKnows[player]:
            card.computerKnows[player] = True
            j = card.j
            app.cardsHighlighted.add((player,j))
            wait(app, app.showLength, lambda app: unHighlightCard(app,player,j))
            break

def unHighlightLater(app, i, j):
    wait(app, app.showLength, lambda app: unHighlightCard(app, i, j))

def computerDoKingView(app, player):
    cardsLookedAt = 0
    while cardsLookedAt < 2:
        choices = []
        for hand in activeHands(app):
            for card in app.cards[hand]:
                if card == None: continue
                if card.computerKnows[player]: continue
                choices.append(card)
        if len(choices) == 0: return
        card = choices[random.randint(0, len(choices) - 1)]
        card.computerKnows[player] = True
        app.cardsHighlighted.add((card.i, card.j))
        unHighlightLater(app, card.i, card.j)
        cardsLookedAt += 1

def computerTryStick(app, player):
    if app.osherCaller == player: return
    stuck = False
    if app.showLength == 1: mistakeChanceNum = 0.02
    elif app.showLength == 0.65: mistakeChanceNum = 0.01
    elif app.showLength == 0.4: mistakeChanceNum = 0.005
    elif app.showLength == 0.2: mistakeChanceNum = 0
    if app.sticker != None and app.sticker != player: return
    selfChanceNum = 0.8 if app.showLength == 1 else 0.95
    otherChanceNum = 0.4 if app.showLength == 1 else 0.7
    if app.showLength == 0.2: otherChanceNum = selfChanceNum = 1
    for hand in app.cards:
        for card in app.cards[hand]:
            if card == None: continue
            if (card.computerKnows[player] and card.value[0] == app.topCard[0]
                and app.cards[player] != [None]*6
                and card.i != app.osherCaller):
                if card.i == player and chance(selfChanceNum):
                    stuck = True
                    computerStickSelf(app,player,card)
                if card.i != player and chance(otherChanceNum):
                    stuck = True
                    computerStickOther(app,player,card)
    if chance(mistakeChanceNum) and not stuck: computerMakeMistake(app, player)

def computerStickSelf(app, player, card):
    if scoreCard(card.value) == -1: return
    app.sticker = player
    app.displayStickMessages[player] = True
    app.cards[card.i][card.j] = None
    app.topCard = card.value
    wait(app, app.showLength,
            lambda app: disableStickMessage(app, player))
    
def computerStickOther(app,player,card):
    app.sticker = player
    app.displayStickMessages[player] = True
    app.cards[card.i][card.j] = None
    app.topCard = card.value
    wait(app, app.showLength,
            lambda app: disableStickMessage(app, player))
    i, j = card.i, card.j
    wait(app, app.showLength*1.5,
            lambda app: computerGiveCard(app, player, i, j))


def computerMakeMistake(app, player):
    seenIndices = set()
    for i in range(len(app.cards[player])):
        if app.cards[player][i] != None: seenIndices.add(i)
    if len(seenIndices) == 6: return
    app.displayMistakeMessages[player] = True
    wait(app, app.showLength,
            lambda app: disableMistakeMessage(app, player))
    for i in range(6):
        if i not in seenIndices:
            app.cards[player][i] = Card(dealCard(app),player,i,app,False)
            break

def stickLater(app, player):
    wait(app, random.uniform(app.showLength*2, app.showLength*3), 
        lambda app: computerTryStick(app, player))

def computersStick(app):
    for i in computerHands(app):
        if app.osherCaller == i: continue
        stickLater(app, i)

def computerGiveCard(app, player, i, j):
    givenCard = None
    for card in app.cards[player]:
        if card == None: continue
        if (card.computerKnows[player] and scoreCard(card.value) > 5 
            and chance(0.2)):
            givenCard = card
            break
        elif not card.computerKnows[player] and chance(0.6):
            givenCard = card
            break
    if givenCard == None:
        while givenCard == None:
            givenCard = app.cards[player][random.randint(0,5)]
    app.cardMoving = True
    app.movingCard = givenCard
    app.targetI, app.targetJ = i, j

def computerDoSwap(app, player):
    firstCard = secondCard = None
    for card in app.cards[player]:
        if card == None: continue
        if not (card.computerKnows[player] or (card.computerKnows[player] and
                scoreCard(card.value) > 6) and chance(0.6)):
            firstCard = card
            break
    if firstCard == None:
        choices = []
        for hand in activeHands(app):
            if hand == app.osherCaller: continue
            for card in app.cards[hand]:
                if card != None: choices.append(card)
        if len(choices) == 0: return
        firstCard = choices[random.randint(0, len(choices) - 1)]
    for hand in activeHands(app):
        if hand == player or hand == app.osherCaller: continue
        for card in app.cards[hand]:
            if card == None: continue
            if (card.computerKnows[player] and scoreCard(card.value) < 6
            and firstCard != card and firstCard.i == player):
                secondCard = card
            elif (card.computerKnows[player] and chance(0.6) and
                  firstCard.i != card.i and firstCard.i == player):
                secondCard = card
    if secondCard == None or secondCard.i == firstCard.i:
        choices = []
        for hand in activeHands(app):
            if hand == firstCard.i or hand == app.osherCaller: continue
            for card in app.cards[hand]:
                if card != None: choices.append(card)
        if len(choices) == 0: return
        secondCard = choices[random.randint(0, len(choices) - 1)]
    app.firstCard = firstCard
    app.secondCard = secondCard
    app.cardsMoving = True

def switchCards(app, firstCard, secondCard):
    firstI, firstJ = firstCard.i, firstCard.j
    secondI, secondJ = secondCard.i, secondCard.j
    firstCard.i, firstCard.j = secondI, secondJ
    secondCard.i, secondCard.j = firstI, firstJ
    app.cards[firstI][firstJ] = None
    app.cards[secondI][secondJ] = None
    app.cards[secondI][secondJ] = firstCard
    app.cards[firstI][firstJ] = secondCard
    updateCards(app)

def computerTakeTopCard(app, player):
    computerDrawingCard = True
    for card in app.cards[player]:
        if card == None: continue
        if not card.computerKnows[player] and chance(0.6):
            app.tempCardShown = True
            app.tempCard = createTempCard(app, player, card.j, 
                                          app.topCard)
            app.topCard = None
            app.tempCardMoving = True
            app.targetI = player
            app.targetJ = card.j
            card.computerKnows = [None] + [True]*3
            computerDrawingCard = False
            break
    if computerDrawingCard:
        computerSmallestKnownCard(app,player)
        computerDrawingCard = False
    app.message = f'{computerName(app, player)} is wrapping up their turn...'
    wait(app, app.showLength*3,
         lambda app: computerTakeTurn(app, app.nextPlayer))
    computersStick(app)

def computerSmallestKnownCard(app, player):
    smallestCardScore = 100
    smallestCard = None
    for card in app.cards[player]:
        if card == None: continue
        if card.computerKnows[player]:
            score = scoreCard(card.value)
            if score < smallestCardScore:
                smallestCardScore = score
                smallestCard = card
    if smallestCard != None:
        app.tempCardShown = True
        app.tempCard = createTempCard(app, player, smallestCard.j, app.topCard)
        app.topCard = None
        app.tempCardMoving = True
        app.targetI = player
        app.targetJ = smallestCard.j
    else:
        app.tempCardShown = True
        app.tempCard = createTempCard(app, player, 0, app.topCard)
        app.topCard = None
        app.tempCardMoving = True
        app.targetI = player
        app.targetJ = 0

def createTempCard(app, i, j, value):
    if app.tempCardShown: 
        x = app.width/2 + app.len/200
        y = app.height/2 + app.len/11 - app.len/20
    else:
        x = app.width/2 - app.len/200 - app.len/15
        y = app.height/2 + app.len/11 - app.len/20
    result = Card(value, i, j, app)
    result.top = y
    result.left = x
    return result

def onMouseMove(app, mouseX, mouseY):
    if not app.lagReduce: checkAllMousedCards(app, mouseX, mouseY)

def checkAllMousedCards(app, mouseX, mouseY):
    if stickPossible(app) or app.jackOrQueen or app.king:
        selectable = []
        for i in activeHands(app):
            if i != app.osherCaller: selectable.append(i)
        checkMousedCards(app, mouseX, mouseY, selectable)
    elif (app.sevenOrEight or app.holdingDrawnCard or 
         app.displayStickOpponentMessage):
        checkMousedCards(app, mouseX, mouseY, [0])
    elif app.nineOrTen:
        checkMousedCards(app, mouseX, mouseY, computerHands(app))
    else: app.cardsMoused = set()

def checkMousedCards(app, mouseX, mouseY, players):
    app.cardsMoused = set()
    coords = loadCoords(app)
    for i in players:
        xList, yList = coords[i*2], coords[i*2+1]
        if mouseInHand(app, mouseX, mouseY, i, xList, yList):
            for j in range(6):
                if i in [0,2]:
                    if ((xList[j] <= mouseX <= xList[j] + app.len/15) and 
                        (yList[j] <= mouseY <= yList[j] + app.len/10)):
                        app.cardsMoused.add((i, j))
                elif i in [1,3]:
                    if ((xList[j] <= mouseX <= xList[j] + app.len/10) and 
                        (yList[j] <= mouseY <= yList[j] + app.len/15)):
                        app.cardsMoused.add((i,j))

def mouseInHand(app, mouseX, mouseY, i, xList, yList):
    if i == 0:
        if xList[4] < mouseX < xList[5] + app.len/15:
            if yList[0] < mouseY < yList[3] + app.len/10:
                return True
        return False
    elif i == 1:
        if xList[0] < mouseX < xList[3] + app.len/10:
            if yList[3] < mouseY < yList[4] + app.len/15:
                return True
        return False
    elif i == 2:
        if xList[4] < mouseX < xList[5] + app.len/15:
            if yList[3] < mouseY < yList[0] + app.len/10:
                return True
        return False
    elif i == 3:
        if xList[3] < mouseX < xList[0] + app.len/10:
            if yList[3] < mouseY < yList[4] + app.len/15:
                return True
        return False

def onStep(app):
    if not (app.viewingRules or app.displayStickOpponentMessage
            or app.gameOver or app.viewingSettings or
            app.cardsMoving or app.cardMoving
            or app.tempCardMoving): processTimers(app)
    elif app.cardsMoving:
        moveCardsStep(app, app.firstCard, app.secondCard, app.showLength)
    elif app.cardMoving:
        moveCardStep(app, app.movingCard, app.targetI, app.targetJ, 
                     app.showLength)
    elif app.tempCardMoving:
        moveTempCardStep(app, app.targetI, app.targetJ, 
                         app.showLength, app.tempCardShown)

def main():
    runApp()

main()