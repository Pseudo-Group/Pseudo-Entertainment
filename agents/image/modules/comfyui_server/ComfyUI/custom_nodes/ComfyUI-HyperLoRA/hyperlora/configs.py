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

from dataclasses import dataclass, field
from transformers import CLIPVisionModelWithProjection, CLIPImageProcessor
from typing import Dict, Any, List, Literal


@dataclass
class BaseConfig:
    def from_dict(self, config_dict: Dict[str, Any]):
        for key, value in config_dict.items():
            if not hasattr(self, key):
                print(f'Ignoring unknown key "{key}"')
                continue
            default_value = getattr(self, key)
            if isinstance(default_value, BaseConfig):
                default_value.from_dict(value)
            elif not default_value == value:
                print(f'Value of key "{key}" was changed from "{default_value}" to "{value}"')
                setattr(self, key, value)

    def print(self, indent: int = 0):
        for key, value in vars(self).items():
            if isinstance(value, BaseConfig):
                print(f'{" " * indent}{key}:')
                value.print(indent + 2)
            else:
                print(f'{" " * indent}{key}: {value}')

    def instantiate(self):
        pass


@dataclass
class BaseImageEncoderConfig(BaseConfig):
    pretrained_model: str = None

    def instantiate(self):
        assert not self.pretrained_model is None
        return CLIPVisionModelWithProjection.from_pretrained(self.pretrained_model)


@dataclass
class BaseImageProcessorConfig(BaseConfig):
    pretrained_model: str = None

    def instantiate(self):
        assert not self.pretrained_model is None
        return CLIPImageProcessor.from_pretrained(self.pretrained_model)


@dataclass
class ResamplerConfig(BaseConfig):
    dim: int = 1024
    dim_head: int = 64
    heads: int = 12
    depth: int = 4
    ff_mult: int = 4


@dataclass
class HyperLoRAConfig(BaseConfig):
    image_processor: BaseImageProcessorConfig = field(default_factory=lambda: BaseImageProcessorConfig())
    image_encoder: BaseImageEncoderConfig = field(default_factory=lambda: BaseImageEncoderConfig())
    resampler: ResamplerConfig = field(default_factory=lambda: ResamplerConfig())

    encoder_types: List[Literal['clip', 'arcface']] = field(default_factory=lambda: ['clip'])

    face_analyzer: str = 'antelopev2'
    insightface_root: str = './'

    id_embed_dim: int = 512
    num_id_tokens: int = 4
    hyper_dim: int = 1024
    lora_rank: int = 4

    has_base_lora: bool = False
