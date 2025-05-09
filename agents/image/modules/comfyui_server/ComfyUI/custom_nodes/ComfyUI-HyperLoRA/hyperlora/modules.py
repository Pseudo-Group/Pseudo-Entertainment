# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates. All rights reserved.

# Licensed under the GNU General Public License, Version 3.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.gnu.org/licenses/gpl-3.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import torch
import torch.nn as nn
from diffusers.models.attention import FeedForward
from diffusers.models.attention_processor import Attention
from typing import Tuple


class PerceiverAttentionBlock(nn.Module):
    def __init__(self, dim, dim_head=64, heads=8, ff_mult=4, n_conds=1):
        super().__init__()

        self.norm_attn1 = nn.LayerNorm(dim)
        self.norm_attn2_l = nn.LayerNorm(dim)
        self.norm_attn2_x = nn.LayerNorm(dim)
        if n_conds == 2:
            self.norm_attn3_l = nn.LayerNorm(dim)
            self.norm_attn3_y = nn.LayerNorm(dim)
        self.norm_ff = nn.LayerNorm(dim)

        self.attn1 = Attention(query_dim=dim, cross_attention_dim=dim, heads=heads, dim_head=dim_head, out_bias=False)
        self.attn2 = Attention(query_dim=dim, cross_attention_dim=dim, heads=heads, dim_head=dim_head, out_bias=False)
        if n_conds == 2:
            self.attn3 = Attention(query_dim=dim, cross_attention_dim=dim, heads=heads, dim_head=dim_head, out_bias=False)
        self.ff = FeedForward(dim=dim, mult=ff_mult, activation_fn='gelu')

    def forward(self, x, latents, y=None):
        # attention 1
        norm_latents = self.norm_attn1(latents)
        latents = self.attn1(norm_latents, encoder_hidden_states=norm_latents) + latents

        # attention 2
        norm_latents = self.norm_attn2_l(latents)
        norm_x = self.norm_attn2_x(x)
        latents = self.attn2(norm_latents, encoder_hidden_states=norm_x) + latents

        # attention 3
        if not y is None:
            norm_latents = self.norm_attn3_l(latents)
            norm_y = self.norm_attn3_y(y)
            latents = self.attn3(norm_latents, encoder_hidden_states=norm_y) + latents

        # feed forward
        norm_latents = self.norm_ff(latents)
        latents = self.ff(norm_latents) + latents

        return latents


class Resampler(nn.Module):
    def __init__(self, dim=1024, depth=8, dim_head=64, heads=8, num_queries=16, embedding_dim=768, output_dim=1024, ff_mult=4, n_conds=1):
        super().__init__()

        self.latents = nn.Parameter(torch.randn(1, num_queries, dim) / dim ** 0.5)
        self.proj_in = nn.Linear(embedding_dim, dim)
        self.proj_out = nn.Linear(dim, output_dim)

        self.layers = nn.ModuleList([
            PerceiverAttentionBlock(dim=dim, dim_head=dim_head, heads=heads, ff_mult=ff_mult, n_conds=n_conds)
            for _ in range(depth)
        ])

        if n_conds == 2:
            self.proj_in_2 = nn.Linear(embedding_dim, dim)

    def norm_out(self, x):
        return x * (x.pow(2.0).sum(dim=-1, keepdim=True) + 1e-8).rsqrt()

    def forward(self, x, y=None):
        latents = self.latents.repeat(x.shape[0], 1, 1)

        x = self.proj_in(x)
        if not y is None:
            y = self.proj_in_2(y)
        for layer in self.layers:
            latents = layer(x, latents, y)

        latents = self.proj_out(latents)
        latents = torch.mean(latents, dim=0, keepdim=True) # get mean latents across batch
        latents = self.norm_out(latents)

        return latents


class HyperLoRALayer(nn.Module):
    def __init__(self, dim: int, in_features: int, out_features: int, lora_rank: int = 4, has_base_lora: bool = False):
        super().__init__()

        self.id_down_basis = nn.Parameter(torch.zeros(dim, in_features, lora_rank))
        self.id_up_basis = nn.Parameter(torch.zeros(dim, lora_rank, out_features))

        if has_base_lora:
            self.base_down_basis = nn.Parameter(torch.zeros(dim, in_features, lora_rank // 2))
            self.base_up_basis = nn.Parameter(torch.zeros(dim, lora_rank // 2, out_features))

    def linear_mix(self, coeffs: torch.Tensor, basis: torch.Tensor):
        return torch.einsum('bi, ijk -> bjk', coeffs, basis)

    def forward(self, tokens: torch.Tensor, mode='id'):
        down_coeffs, up_coeffs = tokens[:,0,:], tokens[:,1,:]
        if mode == 'id':
            down, up = self.linear_mix(down_coeffs, self.id_down_basis), self.linear_mix(up_coeffs, self.id_up_basis)
        elif mode == 'base':
            down, up = self.linear_mix(down_coeffs, self.base_down_basis), self.linear_mix(up_coeffs, self.base_up_basis)
        return down[0].t().contiguous(), up[0].t().contiguous()


class HyperLoRAModule(nn.Module):
    def __init__(self, dim: int, hidden_size: int, cross_attention_dim: int, lora_rank: int = 4, has_base_lora: bool = False):
        super().__init__()

        self.to_q = HyperLoRALayer(dim, hidden_size, hidden_size, lora_rank=lora_rank, has_base_lora=has_base_lora)
        self.to_k = HyperLoRALayer(dim, cross_attention_dim or hidden_size, hidden_size, lora_rank=lora_rank, has_base_lora=has_base_lora)
        self.to_v = HyperLoRALayer(dim, cross_attention_dim or hidden_size, hidden_size, lora_rank=lora_rank, has_base_lora=has_base_lora)
        self.to_out = HyperLoRALayer(dim, hidden_size, hidden_size, lora_rank=lora_rank, has_base_lora=has_base_lora)

    def forward(self, tokens: torch.Tensor, mode='id'):
        q, k, v, out = tokens.chunk(4, dim=1)
        return {
            'to_q': self.to_q(q, mode=mode),
            'to_k': self.to_k(k, mode=mode),
            'to_v': self.to_v(v, mode=mode),
            'to_out_0': self.to_out(out, mode=mode)
        }


class Reshape(nn.Module):
    def __init__(self, shape: Tuple[int]):
        super().__init__()
        self.shape = shape

    def forward(self, x: torch.Tensor):
        return x.reshape(*self.shape)
