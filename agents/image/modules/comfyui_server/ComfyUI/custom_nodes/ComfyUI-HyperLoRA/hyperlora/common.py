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

import base64
import functools
import io
import itertools
import requests
import torch
import numpy as np
from enum import Enum
from dataclasses import dataclass
from PIL import Image
from typing import Any, Callable, Dict, Iterable, List


SD15_ATTN_DOWN_BLOCK_IDS = [ 1, 2, 4, 5, 7, 8 ]
SD15_ATTN_UP_BLOCK_IDS = [ 3, 4, 5, 6, 7, 8, 9, 10, 11 ]

SDXL_ATTN_DOWN_BLOCK_IDS = [
    (4, 0), (4, 1),
    (5, 0), (5, 1),
    (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (7, 9),
    (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (8, 8), (8, 9)
]
SDXL_ATTN_MID_BLOCK_IDS = [
    (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9)
]
SDXL_ATTN_UP_BLOCK_IDS = [
    (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9),
    (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9),
    (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9),
    (3, 0), (3, 1),
    (4, 0), (4, 1),
    (5, 0), (5, 1)
]


@dataclass
class FaceAttrInfo:
    rect: np.ndarray
    landmarks: np.ndarray

@dataclass
class SmashResp:
    n_face: int
    w: int
    h: int

@dataclass
class FaceAttrResp(SmashResp):
    faces: List[FaceAttrInfo]


class ResizeMode(Enum):
    LONG_EDGE = 0
    SHORT_EDGE = 1
    WIDTH = 2
    HEIGHT = 3

class BatchType(Enum):
    TENSOR = 0
    LIST = 1


def tensor2images(tensor: torch.Tensor) -> List[Image.Image]:
    images = []
    for i in range(tensor.shape[0]):
        image = tensor[i].cpu().numpy()
        image = (image.clip(0.0, 1.0) * 255.0).astype(np.uint8)
        images.append(Image.fromarray(image))
    return images

def images2tensor(images: Iterable[Image.Image]) -> torch.Tensor:
    tensor_list = []
    for image in images:
        image = np.array(image).astype(np.float32) / 255.0
        tensor_list.append(torch.from_numpy(image).unsqueeze(0))
    return torch.cat(tensor_list, dim=0)

def image2base64(image: Image.Image) -> str:
    with io.BytesIO() as f:
        image.save(f, format='PNG')
        img_bytes = f.getvalue()
    return str(base64.b64encode(img_bytes), encoding='utf-8')

def image_from_url(url: str) -> Image.Image:
    return Image.open(requests.get(url, stream=True).raw)

def resize_image(image: Image.Image, size: int, mode: ResizeMode = ResizeMode.LONG_EDGE) -> Image.Image:
    w, h = image.size
    if mode == ResizeMode.LONG_EDGE:
        scale = size / max(w, h)
    elif mode == ResizeMode.SHORT_EDGE:
        scale = size / min(w, h)
    elif mode == ResizeMode.WIDTH:
        scale = size / w
    elif mode == ResizeMode.HEIGHT:
        scale = size / h
    scale += 1e-5
    return image.resize((int(w * scale), int(h * scale)), Image.Resampling.BICUBIC if scale >= 1.0 else Image.Resampling.LANCZOS)

def batch_proc(**arg_types: Dict[str, BatchType]):
    def wrapper(func: Callable):
        def worker(*args: List[Any], **kwargs: Dict[str, Any]) -> Any:
            # convert tensor to images and get max batch size
            max_bs = 0
            batch_args = {}
            for name, type in arg_types.items():
                assert name in kwargs, f'{name} is not in kwargs'
                if type == BatchType.TENSOR:
                    batch_args[name] = tensor2images(kwargs[name])
                elif type == BatchType.LIST:
                    batch_args[name] = kwargs[name]
                else:
                    assert False, f'{type} is not supported'
                max_bs = max(max_bs, len(batch_args[name]))
            # check if all args have the same batch size or batch size is 1
            for name, type in arg_types.items():
                if len(batch_args[name]) == max_bs:
                    continue
                elif len(batch_args[name]) == 1:
                    batch_args[name] = [ batch_args[name][0] for _ in range(max_bs) ]
                else:
                    assert False, 'All args must have the same batch size or batch size is 1'
            # batch process
            batch_args_cnt = len(batch_args)
            outs = []
            for items in zip(*map(functools.partial(itertools.repeat, times=max_bs), batch_args.keys()), *batch_args.values()):
                for name, value in zip(items[:batch_args_cnt], items[batch_args_cnt:]):
                    kwargs[name] = value
                outs.append(func(*args, **kwargs))
            # post process
            results = []
            for items in zip(*outs):
                if isinstance(items[0], Image.Image):
                    results.append(images2tensor(items))
                else:
                    results.append(list(items))
            return tuple(results)
        return worker
    return wrapper
