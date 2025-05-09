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

from typing import Dict, Iterable, Tuple


def inputs_def(required: Iterable = [], optional: Iterable = []) -> Dict[str, Dict]:
    return {
        'required': {
            k: v for k, v in required
        },
        'optional': {
            k: v for k, v in optional
        }
    }

def image_field(name: str = 'image') -> Tuple[str, Tuple]:
    return name, ('IMAGE', )

def mask_field(name: str = 'mask') -> Tuple[str, Tuple]:
    return name, ('MASK', )

def custom_field(name: str = 'custom', type_name: str = 'CUSTOM') -> Tuple[str, Tuple]:
    return name, (type_name, )

def enum_field(name: str = 'enum_field', options: Iterable = []) -> Tuple[str, Tuple]:
    return name, (options, )

def int_field(name: str = 'int_field', default: int = 50, minimum: int = 0, maximum: int = 100, step: int = 1) -> Tuple[str, Tuple]:
    return name, ('INT', {
        'default': default,
        'min': minimum,
        'max': maximum,
        'step': step,
        'display': 'number'
    })

def float_field(name: str = 'float_field', default: float = 0.5, minimum: float = 0.0, maximum: float = 1.0, step: float = 0.1) -> Tuple[str, Tuple]:
    return name, ('FLOAT', {
        'default': default,
        'min': minimum,
        'max': maximum,
        'step': step,
        'round': step,
        'display': 'number'
    })

def str_field(name: str = 'str_field', default: str = '', multiline: bool = False) -> Tuple[str, Tuple]:
    return name, ('STRING', {
        'default': default,
        'multiline': multiline
    })

def bool_field(name: str = 'bool_field', default: bool = False) -> Tuple[str, Tuple]:
    return name, ('BOOLEAN', {
        'default': default
    })
