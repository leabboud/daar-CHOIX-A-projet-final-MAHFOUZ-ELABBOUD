from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers
import os

TEST_DIR = "Tests/"
TEST_TEXTS_DIR= TEST_DIR + "Texts/"
ACTUAL_TEXTS_DIR = "bookInfo/bookIndices"

def get_all_stored_indices():
	return (list(map(lambda x: x[:len(x)-5],os.listdir(ACTUAL_TEXTS_DIR))))

def getText(text_id):
	text = strip_headers(load_etext(text_id)).strip()
	return text

def getAllTexts():
	bids=get_all_stored_indices()
	for bid in bids:
		try:
			t = getText(int(bid))
			write_check="x"
			if (os.path.isfile(TEST_TEXTS_DIR+str(bid)+".txt")):
				write_checl="w"
			with open(TEST_TEXTS_DIR+str(bid)+".txt",write_check) as f:
				f.write(t)
		except Exception as e:
			print("Error writing bid: "+bid)
			print(e)

getAllTexts()