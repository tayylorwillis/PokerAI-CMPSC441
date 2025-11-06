from flask import Flask, render_template, send_file
from PIL import Image, ImageDraw, ImageFont
import io


app = Flask(__name__)

   #SPADE      #CLUB    #HEART   #DIAMOND
SUITS = ["\u2660", "\u2663","\u2665","\u2666"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
DECK = [(rank,suit) for suit in SUITS for rank in RANKS]

large_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 100)
small_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 35)

@app.route('/')
def index():
    return render_template('index.html', deck=DECK)

@app.route('/card/<rank>/<suit>')
def card_image(rank, suit):
                #SPADE      #CLUB
    if suit in ["\u2660", "\u2663"]:
        color = "black"
    else:
        color = "red"

    # Create card image template
    width, height = 300,400
    card_image = Image.new('RGB', (width, height), 'white')
    card = ImageDraw.Draw(card_image)

    # Draw card elements
    card.rectangle([10,10, width-10, height-10], outline='black', width=4)
    card.text((20, 20), rank + suit, font=small_font, fill=color)
    card.text((width//2 - 30, height//2 - 50), suit, font=large_font, fill=color)
    card.text((width - 80, height - 70), rank + suit, font=small_font, fill=color)

    # Return image as response
    byte_io = io.BytesIO()
    card_image.save(byte_io, 'PNG')
    byte_io.seek(0)
    return send_file(byte_io, mimetype='image/png')

    
if __name__ == '__main__':
    app.run(debug=True)
