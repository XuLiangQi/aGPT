# Load third-party modules
import torch
from torch.nn import functional as F

# Load custom modules
from tools.txt_loader import load_text
from tools.get_batch import get_batch
from models.bigram_language_model import BigramLanguageModel as BLM


batch_size = 4  # How many independent sequences will we precess in parallel
block_size = 8  # What is the maximum context length for predictions

# Check and assign GPU (CUDA) or MPS (Apple Metal) if available
device = torch.device("cpu")
if torch.cuda.is_available():
    device = torch.device("cuda")
elif torch.backends.mps.is_available():
    # Disabled due to bus error caused by mps backend
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
decode = lambda l : ''.join([itos[i] for i in l])   # ''.join connects tuples with '' and convert them into string
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

# # Break text into chunks
# block_size = 8
# print(train_data[:block_size + 1])

# x = train_data[:block_size]
# y = train_data[1:block_size + 1]
# for t in range(block_size):
#     context = x[:t + 1]
#     target = y[t]
#     print(f"When input is {context} the target is : {target}")

torch.manual_seed(1337)

xb, yb = get_batch(train_data, batch_size, block_size)
print('Inputs:')
print(xb.shape)
print(xb)
print('Targets:')
print(yb.shape)
print(yb)

# for b in range(batch_size):
#     for t in range(block_size):
#         context = xb[b, :t+1]
#         target = yb[b, t]
#         print(f"When input is {context.tolist()} the target: {target}")

m = BLM(device)
logits, loss = m.forward(xb, yb)
print(logits.shape)
print(loss)

# # idx = torch.zeros((1, 1), dtype = torch.long, device = device)
# print(decode(m.generate(torch.zeros((1, 1), dtype = torch.long, device = device), max_new_tokens=100)[0].tolist()))
#
# m.train(train_data, batch_size, block_size)
# print(decode(m.generate(torch.zeros((1, 1), dtype = torch.long, device = device), max_new_tokens=100)[0].tolist()))

# Version 1
torch.manual_seed(1337)
B, T, C = 4, 8, 2
x = torch.randn(B, T, C)
xbow = torch.zeros((B, T, C))
for b in range(B):
    for t in range(T):
        xprev = x[b, :t+1]  # (t, C)
        xbow[b, t] = torch.mean(xprev, 0)   # Averaging out the 0 dimension
print(x.shape)
print(x[0])     # Print 0th batch of elements
print(xbow[0])

# Version 2
weights = torch.tril(torch.ones(T, T))
weights = weights / weights.sum(1, keepdim=True)
xbow2 = weights @ x  # (B, T, T) @ (B, T, C)
print(xbow2[0])
print(torch.allclose(xbow, xbow2))

# Version 3
tril = torch.tril(torch.ones(T, T))
weights = torch.zeros((T, T))
print(weights)
weights = weights.masked_fill(tril == 0, float('-inf'))  # Fill all element in tril where is 0 to negative infinity
print(weights)
weights = F.softmax(weights, dim=1)
print(weights)