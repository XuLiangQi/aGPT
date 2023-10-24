import torch
import torch.nn as nn
from torch.nn import functional as F

from tools.get_batch import get_batch

torch.manual_seed(1337)

batch_size = 4  # How many independent sequences will we precess in parallel
block_size = 8  # What is the maximum context length for predictions
max_iters = 3000
eval_interval = 300
learning_rate = 1e-2
eval_iters = 200
vocab_size = 65
n_embd = 32

class BigramLanguageModel(nn.Module):
    def __init__(self, device):
        super().__init__()
        self.device = device
        # Each token directly reads off the logits for the next token from a lookup table
        # Initializing the embedding table with size of vocab_size**2
        self.token_embedding_table = nn.Embedding(vocab_size, vocab_size, n_embd, self.device)
        self.lm_head = nn.Linear(n_embd, vocab_size)

    def forward(self, idx, targets=None):
        # idx and targets are both (B, T) tensor of integers
        tok_emb = self.token_embedding_table(idx)    # (B, T, C), in this case (4 (batch_size), 8 (block_size), 65(vocab_size))
                                                     # becase idx is (B, T), and each element from "idx" will go in token_embedding_table
                                                     # and get a row of data (1, 65(C))

        logits = self.lm_head(tok_emb)               # (B, T, vocab_size)

        if targets is not None:
            B, T, C = logits.shape

            logits = logits.view(B*T, C)        # Returns a new tensor with the same data as the self tensor but of a different shape.
            targets = targets.view(B*T)

            loss = F.cross_entropy(logits, targets)
        else:
            loss = None

        return logits, loss

    def generate(self, idx, max_new_tokens):
        # idx is (B, T) array of indices in the current context
        for _ in range(max_new_tokens):
            # Get the predictions
            logits, _ = self.forward(idx)
            # Focus only on the last time step
            logits = logits[:, -1, :]   # becomes (B, C)
            # Apply softmax to get probabilities
            probs = F.softmax(logits, dim = -1)     # (B, C)
            # Sample from the distribution
            idx_next = torch.multinomial(probs, num_samples = 1)    # (B, 1)
            # Append sampled index to the running sequencing
            idx = torch.cat((idx, idx_next), dim = 1)      # (B, T+1)

        return idx

    def train(self, train_data, batch_size, block_size):
        optimizer = torch.optim.AdamW(self.parameters(), lr = 1e-3)
        # batch_size = 32
        for iter in range(max_iters):
            # Sample a batch of data
            xb, yb = get_batch(train_data, batch_size, block_size)

            # Evaluate the loss
            _, loss = self.forward(xb, yb)
            optimizer.zero_grad(set_to_none = True)
            loss.backward()
            optimizer.step()

            # Print loss every 1000 steps
            if iter % 1000 == 0:
                print(loss.item())