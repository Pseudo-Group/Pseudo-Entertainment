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

from .hyperlora.nodes import HYPER_LORA_CLASS_MAPPINGS, HYPER_LORA_DISPLAY_NAME_MAPPINGS


NODE_CLASS_MAPPINGS = {
    **HYPER_LORA_CLASS_MAPPINGS
}

NODE_DISPLAY_NAME_MAPPINGS = {
    **HYPER_LORA_DISPLAY_NAME_MAPPINGS
}
