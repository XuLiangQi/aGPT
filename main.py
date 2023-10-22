# Load third-party modules
import torch

# Load custom modules
from tools.txt_loader import load_text
from models.bigram_language_model import BigramLanguageModel as BLM

# Check and assign GPU (CUDA) or MPS (Apple Metal) if available
device = torch.device("cpu")
if torch.cuda.is_available():
    device = torch.device("cuda")
elif torch.backends.mps.is_available():
    pass
    #device = torch.device("mps")

# Read tiny shakespear txt file
text_dir = "data/tinyShakespeare.txt"
text = load_text(text_dir)
# print("Length of dataset in characters: ", len(text))

all_chars = set(text)
all_chars_in_list = list(all_chars)
all_chars_in_list_sorted = sorted(all_chars_in_list)
vocab_size = len(all_chars_in_list_sorted) 
#print(all_chars_in_list_sorted)
#print("Total # vocabs: " + str(vocab_size))

# A simple encoder/decoder
stoi = {}
itos = {}
for i, ch in enumerate(all_chars):
    stoi[ch] = i
    itos[i] = ch

encode = lambda s : [stoi[c] for c in s]
decode = lambda i : [itos[n] for n in i]
# print(encode("Hello World!"))
# print(decode(encode("Hello World!")))

# Convert text into tensor 
data = torch.tensor(encode(text), dtype=torch.long, device=device)
# print(data.shape, data.dtype)
# print(data[:1000])

# Set up a threshold to split data into 90% train, 10% test
train_test_thres = int(0.9 * len(data))
train_data = data[:train_test_thres]
val_data = data[train_test_thres:]

# Break text into chunks
block_size = 8
print(train_data[:block_size + 1])

# x = train_data[:block_size]
# y = train_data[1:block_size + 1]
# for t in range(block_size):
#     context = x[:t + 1]
#     target = y[t]
#     print(f"When input is {context} the target is : {target}")

torch.manual_seed(1337)
batch_size = 4  # How many independent sequences will we precess in parallel
block_size = 8  # What is the maximum context length for predictions

def get_batch(split):
    temp_data = train_data if split == 'train' else val_data
    ix = torch.randint(len(temp_data) - block_size, (batch_size,))
    x = torch.stack([temp_data[i:i + block_size] for i in ix])
    y = torch.stack([temp_data[i + 1:i + block_size + 1] for i in ix])
    return x, y

xb, yb = get_batch('train')
print('Inputs:')
print(xb.shape)
print(xb)
print('Targets:')
print(yb.shape)
print(yb)

for b in range(batch_size):
    for t in range(block_size):
        context = xb[b, :t+1]
        target = yb[b, t]
        print(f"When input is {context.tolist()} the target: {target}")

m = BLM(vocab_size, device)
logits, loss = m.forward(xb, yb)
print(logits.shape)
print(loss)