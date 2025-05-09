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

import cv2
import folder_paths
import json
import os
import numpy as np
import torch
import torch.nn as nn
from comfy.model_management import get_torch_device
from comfy.model_patcher import ModelPatcher
from comfy.sd import load_lora_for_models
from dataclasses import dataclass
from insightface.app import FaceAnalysis
from PIL import Image, ImageDraw, ImageFilter
from safetensors.torch import load_file
from .common import FaceAttrInfo, FaceAttrResp, images2tensor, tensor2images
from .configs import HyperLoRAConfig
from .modules import HyperLoRAModule, Resampler, Reshape
from .node_fields import *


@dataclass
class HyperLoRA:
    image_processor = None
    image_encoder = None
    face_analyzer: FaceAnalysis = None
    resampler: nn.Module = None
    base_resampler: nn.Module = None
    id_projector: nn.Module = None
    hyper_lora_modules: nn.ModuleList = None
    hyper_lora_modules_info: dict = None
    has_clip_encoder: bool = False


def list_models(model_type):
    full_folder = os.path.join(folder_paths.models_dir, model_type)
    models = []
    if os.path.exists(full_folder):
        for fn in os.listdir(full_folder):
            full_path = os.path.join(full_folder, fn)
            if os.path.isdir(full_path) or os.path.islink(full_path):
                models.append(fn)
    if len(models) == 0:
        models.append('Not found!')
    return models

def face_bbox(landmark: np.ndarray):
    x_min, y_min = landmark.min(axis=0)
    x_max, y_max = landmark.max(axis=0)
    c_x = (x_min + x_max) * 0.5
    c_y = (y_min + y_max) * 0.5
    l = max(x_max - x_min, y_max - y_min) * 0.75
    c_y -= l * 0.125
    return (c_x, c_y), l

def face_crop(image: Image.Image, landmark: np.ndarray, mask_scale: float = 1.0):
    OUTLINE_INDICES = [
        1, 9, 10, 11, 12, 13, 14, 15, 16, 2, 3, 4, 5, 6, 7, 8, 0,
        24, 23, 22, 21, 20, 19, 18, 32, 31, 30, 29, 28, 27, 26, 25, 17,
        101, 105, 104, 103, 102, 50, 51, 49, 48, 43
    ]
    # get mask by landmark
    pts = landmark[OUTLINE_INDICES]
    center = pts.mean(axis=0, keepdims=True)
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon((pts - center) * mask_scale + center, fill=255)
    # crop image & mask
    x_min, y_min = pts.min(axis=0)
    x_max, y_max = pts.max(axis=0)
    l = max(x_max - x_min, y_max - y_min) * 0.8
    c_x, c_y = center[0]
    crop_image = image.crop((c_x - l, c_y - l, c_x + l, c_y + l))
    crop_mask = mask.crop((c_x - l, c_y - l, c_x + l, c_y + l))
    return (crop_image, crop_mask), (c_x, c_y), l


class HyperLoRAConfigNode:

    @classmethod
    def INPUT_TYPES(cls):
        return inputs_def(required=[
            enum_field('image_processor', options=list_models('hyper_lora/clip_processor')),
            enum_field('image_encoder', options=list_models('hyper_lora/clip_vit')),
            int_field('resampler.dim', default=1024, minimum=64, maximum=2048, step=32),
            int_field('resampler.dim_head', default=64, minimum=32, maximum=512, step=32),
            int_field('resampler.heads', default=12, minimum=4, maximum=32, step=4),
            int_field('resampler.depth', default=4, minimum=4, maximum=16, step=2),
            int_field('resampler.ff_mult', default=4, minimum=2, maximum=8, step=2),
            enum_field('encoder_types', options=[ 'clip', 'arcface', 'clip + arcface' ]),
            enum_field('face_analyzer', options=list_models('insightface/models')),
            int_field('id_embed_dim', default=512, minimum=128, maximum=1024, step=32),
            int_field('num_id_tokens', default=4, minimum=4, maximum=128, step=4),
            int_field('hyper_dim', default=128, minimum=32, maximum=1024, step=32),
            int_field('lora_rank', default=4, minimum=2, maximum=32, step=2),
            bool_field('has_base_lora', default=False)
        ])

    RETURN_TYPES = ('HYPER_LORA_CONFIG', )
    FUNCTION = 'execute'
    CATEGORY = 'HyperLoRA'

    def execute(self, **kwagrs):
        config_dict = {
            'image_processor': {
                'pretrained_model': os.path.join(folder_paths.models_dir, 'hyper_lora/clip_processor', kwagrs['image_processor'])
            },
            'image_encoder': {
                'pretrained_model': os.path.join(folder_paths.models_dir, 'hyper_lora/clip_vit', kwagrs['image_encoder'])
            },
            'resampler': {
                'dim': kwagrs['resampler.dim'],
                'dim_head': kwagrs['resampler.dim_head'],
                'heads': kwagrs['resampler.heads'],
                'depth': kwagrs['resampler.depth'],
                'ff_mult': kwagrs['resampler.ff_mult']
            },
            'encoder_types': kwagrs['encoder_types'].split(' + '),
            'face_analyzer': kwagrs['face_analyzer'],
            'insightface_root': os.path.join(folder_paths.models_dir, 'insightface'),
            'id_embed_dim': kwagrs['id_embed_dim'],
            'num_id_tokens': kwagrs['num_id_tokens'],
            'hyper_dim': kwagrs['hyper_dim'],
            'lora_rank': kwagrs['lora_rank'],
            'has_base_lora': kwagrs['has_base_lora']
        }
        config = HyperLoRAConfig()
        config.from_dict(config_dict)
        config.print()
        return (config, )


class HyperLoRALoaderNode:

    @classmethod
    def INPUT_TYPES(cls):
        return inputs_def(required=[
            custom_field('config', type_name='HYPER_LORA_CONFIG'),
            enum_field('model', options=list_models('hyper_lora/hyper_lora')),
            enum_field('dtype', options=[ 'fp16', 'bf16', 'fp32' ])
        ])

    RETURN_TYPES = ('HYPER_LORA', )
    FUNCTION = 'execute'
    CATEGORY = 'HyperLoRA'

    def execute(self, config: HyperLoRAConfig, model, dtype):
        device = get_torch_device()
        full_folder = os.path.join(folder_paths.models_dir, 'hyper_lora/hyper_lora', model)
        hyper_lora = HyperLoRA()

        if dtype == 'fp16':
            dtype = torch.float16
        elif dtype == 'bf16':
            dtype = torch.bfloat16
        elif dtype == 'fp32':
            dtype = torch.float32

        # load clip vit
        if 'clip' in config.encoder_types or config.has_base_lora:
            hyper_lora.image_processor = config.image_processor.instantiate()
            hyper_lora.image_encoder = config.image_encoder.instantiate()
            hyper_lora.image_encoder.to(device, dtype).eval()
        hyper_lora.has_clip_encoder = ('clip' in config.encoder_types)

        # load hyper lora modules
        hyper_lora.hyper_lora_modules = nn.ModuleList()
        hyper_lora_modules_info_file = os.path.join(full_folder, 'hyper_lora_modules.json')
        assert os.path.isfile(hyper_lora_modules_info_file), 'HyperLoRA modules info file not found!'
        with open(hyper_lora_modules_info_file, 'rt') as f:
            hyper_lora_modules_info = json.load(f)
        hyper_lora.hyper_lora_modules_info = hyper_lora_modules_info
        for module_info in hyper_lora_modules_info.values():
            hyper_lora.hyper_lora_modules.append(HyperLoRAModule(
                config.hyper_dim, module_info['hidden_size'], module_info['cross_attention_dim'],
                lora_rank=config.lora_rank, has_base_lora=config.has_base_lora
            ))
        hyper_lora_modules_file = os.path.join(full_folder, 'hyper_lora_modules.safetensors')
        assert os.path.isfile(hyper_lora_modules_file), 'HyperLoRA modules file not found!'
        hyper_lora.hyper_lora_modules.load_state_dict(load_file(hyper_lora_modules_file))
        hyper_lora.hyper_lora_modules.to(device, dtype).eval()
        print('HyperLoRA modules loaded.')

        # load resampler
        hyper_lora.resampler = Resampler(
            dim=config.resampler.dim,
            depth=config.resampler.depth,
            dim_head=config.resampler.dim_head,
            heads=config.resampler.heads,
            num_queries=8 * len(hyper_lora.hyper_lora_modules),
            embedding_dim=hyper_lora.image_encoder.config.hidden_size if hyper_lora.has_clip_encoder else config.id_embed_dim,
            output_dim=config.hyper_dim,
            ff_mult=config.resampler.ff_mult,
            n_conds=len(config.encoder_types)
        )
        resampler_file = os.path.join(full_folder, 'resampler.safetensors')
        assert os.path.isfile(resampler_file), 'Resampler file not found!'
        hyper_lora.resampler.load_state_dict(load_file(resampler_file))
        hyper_lora.resampler.to(device, dtype).eval()
        print('Resampler loaded.')

        # load base resampler
        if config.has_base_lora:
            hyper_lora.base_resampler = Resampler(
                dim=config.resampler.dim,
                depth=config.resampler.depth,
                dim_head=config.resampler.dim_head,
                heads=config.resampler.heads,
                num_queries=8 * len(hyper_lora.hyper_lora_modules),
                embedding_dim=hyper_lora.image_encoder.config.hidden_size,
                output_dim=config.hyper_dim,
                ff_mult=config.resampler.ff_mult,
                n_conds=1
            )
            base_resampler_file = os.path.join(full_folder, 'base_resampler.safetensors')
            assert os.path.isfile(base_resampler_file), 'Base resampler file not found!'
            hyper_lora.base_resampler.load_state_dict(load_file(base_resampler_file))
            hyper_lora.base_resampler.to(device, dtype).eval()
            print('Base resampler loaded.')

        # load id projector
        if 'arcface' in config.encoder_types:
            hyper_lora.id_projector = nn.Sequential(
                nn.Linear(config.id_embed_dim, hyper_lora.resampler.proj_in.in_features * config.num_id_tokens),
                Reshape((-1, config.num_id_tokens, hyper_lora.resampler.proj_in.in_features)),
                nn.LayerNorm(hyper_lora.resampler.proj_in.in_features)
            )
            id_projector_file = os.path.join(full_folder, 'id_projector.safetensors')
            assert os.path.isfile(id_projector_file), 'ID projector file not found!'
            hyper_lora.id_projector.load_state_dict(load_file(id_projector_file))
            hyper_lora.id_projector.to(device, dtype).eval()
            print('ID projector loaded.')

            hyper_lora.face_analyzer = FaceAnalysis(name=config.face_analyzer, root=config.insightface_root, providers=['CPUExecutionProvider'])
            hyper_lora.face_analyzer.prepare(ctx_id=0, det_size=(640, 640))
            print('Face analyzer loaded.')

        return (hyper_lora, )


class HyperLoRAIDCondNode:

    @classmethod
    def INPUT_TYPES(cls):
        return inputs_def(required=[
            custom_field('hyper_lora', type_name='HYPER_LORA'),
            image_field('images'),
            custom_field('face_attr', type_name='FACE_ATTR'),
            bool_field('grayscale', default=False),
            bool_field('remove_background', default=True)
        ])

    RETURN_TYPES = ('ID_COND', 'IMAGE')
    FUNCTION = 'execute'
    CATEGORY = 'HyperLoRA'

    def make_id_cond(self, hyper_lora: HyperLoRA, image: Image.Image, face_attr: FaceAttrResp, grayscale, remove_background):
        if face_attr.n_face == 0:
            raise Exception('No face detected!')
        landmark = face_attr.faces[0].landmarks[:106, :]

        # face preprocess
        if remove_background:
            (crop_image, crop_mask), (c_x, c_y), l = face_crop(image, landmark, mask_scale=1.0)
            crop_mask = crop_mask.resize((512, 512))
            crop_mask = crop_mask.filter(ImageFilter.GaussianBlur(radius=15)).resize(crop_image.size)
            face = Image.new('RGB', image.size, '#7f7f7f')
            face.paste(crop_image, (int(c_x - l), int(c_y - l)), crop_mask)
        else: face = image

        # for clip
        (c_x, c_y), l = face_bbox(landmark)
        face = face.crop((c_x - l, c_y - l, c_x + l, c_y + l))
        if grayscale:
            face = face.convert('L')
        if hyper_lora.has_clip_encoder:
            id_image = hyper_lora.image_processor(face, return_tensors='pt').pixel_values
        else: id_image = None

        # for arcface
        l = l * 2.0
        image = image.crop((c_x - l, c_y - l, c_x + l, c_y + l))
        if not hyper_lora.face_analyzer is None:
            hyper_lora.face_analyzer.det_model.input_size = (640, 640)
            face_list = hyper_lora.face_analyzer.get(cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR))
            if len(face_list) == 0:
                raise Exception('No face detected!')
            id_embed = torch.from_numpy(face_list[0].normed_embedding).view(1, 1, 512)
        else: id_embed = None

        return id_image, id_embed, face.resize((512, 512))

    def execute(self, hyper_lora: HyperLoRA, images: torch.Tensor, face_attr: list[FaceAttrResp], grayscale, remove_background):
        images = tensor2images(images)
        id_images, id_embeds, faces = [], [], []
        for image, _face_attr in zip(images, face_attr):
            try:
                id_image, id_embed, face = self.make_id_cond(hyper_lora, image, _face_attr, grayscale, remove_background)
                if not id_image is None:
                    id_images.append(id_image)
                if not id_embed is None:
                    id_embeds.append(id_embed)
                faces.append(face)
            except:
                print('No face detected!')
        id_images = torch.cat(id_images, dim=0) if len(id_images) > 0 else None
        id_embeds = torch.cat(id_embeds, dim=0) if len(id_embeds) > 0 else None
        return [ id_images, id_embeds ], images2tensor(faces)


class HyperLoRABaseCondNode:

    @classmethod
    def INPUT_TYPES(cls):
        return inputs_def(required=[
            custom_field('hyper_lora', type_name='HYPER_LORA'),
            image_field('images'),
            custom_field('face_attr', type_name='FACE_ATTR'),
            bool_field('crop', default=True),
            str_field('crop_scale_LRTB', default='1,1,1,1'),
            bool_field('safe_crop', default=True)
        ])

    RETURN_TYPES = ('BASE_COND', 'IMAGE')
    FUNCTION = 'execute'
    CATEGORY = 'HyperLoRA'

    def make_base_cond(self, hyper_lora: HyperLoRA, image: Image.Image, face_attr: FaceAttrResp, crop, crop_scale_LRTB, safe_crop):
        if face_attr.n_face == 0:
            raise Exception('No face detected!')
        landmark = face_attr.faces[0].landmarks[:106, :]

        # face preprocess
        (crop_image, crop_mask), (c_x, c_y), l = face_crop(image, landmark, mask_scale=1.4)
        _size = crop_image.size
        crop_image = crop_image.resize((512, 512))
        crop_mask = crop_mask.resize((512, 512))
        crop_image = crop_image.filter(ImageFilter.GaussianBlur(radius=45)).resize(_size)
        crop_mask = crop_mask.filter(ImageFilter.GaussianBlur(radius=15)).resize(_size)
        image.paste(crop_image, (int(c_x - l), int(c_y - l)), crop_mask)

        # crop
        if crop:
            (c_x, c_y), l = face_bbox(landmark)
            a, b, c, d = map(float, crop_scale_LRTB.split(','))
            x1, y1, x2, y2 = c_x - l * a, c_y - l * c, c_x + l * b, c_y + l * d
            if safe_crop:
                x1, y1, x2, y2 = max(0, x1), max(0, y1), min(image.width, x2), min(image.height, y2)
            image = image.crop((x1, y1, x2, y2))

        # for clip
        if not hyper_lora.base_resampler is None:
            base_cond = hyper_lora.image_processor(image, return_tensors='pt').pixel_values
        else: base_cond = None

        return base_cond, image


    def execute(self, hyper_lora: HyperLoRA, images: torch.Tensor, face_attr: list[FaceAttrResp], crop, crop_scale_LRTB, safe_crop):
        images = tensor2images(images)
        base_conds, base_images = [], []
        for image, _face_attr in zip(images, face_attr):
            try:
                base_cond, base_image = self.make_base_cond(hyper_lora, image, _face_attr, crop, crop_scale_LRTB, safe_crop)
                if not base_cond is None:
                    base_conds.append(base_cond)
                base_images.append(base_image)
            except:
                print('No face detected!')
        base_conds = torch.cat(base_conds, dim=0) if len(base_conds) > 0 else None
        return base_conds, images2tensor(base_images)


class HyperLoRAGenerateIDLoRANode:

    @classmethod
    def INPUT_TYPES(cls):
        return inputs_def(required=[
            custom_field('hyper_lora', type_name='HYPER_LORA'),
            custom_field('id_cond', type_name='ID_COND')
        ])

    RETURN_TYPES = ('LORA', )
    FUNCTION = 'execute'
    CATEGORY = 'HyperLoRA'

    @torch.no_grad()
    def execute(self, hyper_lora: HyperLoRA, id_cond):
        device = get_torch_device()
        dtype = hyper_lora.resampler.proj_in.weight.dtype

        id_image, id_embed = id_cond
        assert not id_image is None or not id_embed is None, 'ID condition is None!'
        if not id_embed is None:
            id_embed = hyper_lora.id_projector(id_embed.to(device, dtype))
        if not id_image is None:
            conds = [ id_embed, hyper_lora.image_encoder(id_image.to(device, dtype), output_hidden_states=True).hidden_states[-2] ]
        else:
            conds = [ hyper_lora.image_encoder(id_image.to(device, dtype), output_hidden_states=True).hidden_states[-2], None ]
        tokens_list = hyper_lora.resampler(*conds).chunk(len(hyper_lora.hyper_lora_modules), dim=1)
        lora_weights = {}
        for name, module, tokens in zip(hyper_lora.hyper_lora_modules_info.keys(), hyper_lora.hyper_lora_modules, tokens_list):
            for key, (down, up) in module(tokens, mode='id').items():
                lora_key = f'{name}_{key}'
                lora_weights[f'{lora_key}.alpha'] = torch.tensor(float(down.shape[0])) * 0.5 # lora rank // 2
                lora_weights[f'{lora_key}.lora_down.weight'] = down.cpu()
                lora_weights[f'{lora_key}.lora_up.weight'] = up.cpu()
        return (lora_weights, )


class HyperLoRAGenerateBaseLoRANode:

    @classmethod
    def INPUT_TYPES(cls):
        return inputs_def(required=[
            custom_field('hyper_lora', type_name='HYPER_LORA'),
            custom_field('base_cond', type_name='BASE_COND')
        ])

    RETURN_TYPES = ('LORA', )
    FUNCTION = 'execute'
    CATEGORY = 'HyperLoRA'

    @torch.no_grad()
    def execute(self, hyper_lora: HyperLoRA, base_cond):
        device = get_torch_device()
        dtype = hyper_lora.resampler.proj_in.weight.dtype

        base_cond = hyper_lora.image_encoder(base_cond.to(device, dtype), output_hidden_states=True).hidden_states[-2]
        tokens_list = hyper_lora.base_resampler(base_cond).chunk(len(hyper_lora.hyper_lora_modules), dim=1)
        lora_weights = {}
        for name, module, tokens in zip(hyper_lora.hyper_lora_modules_info.keys(), hyper_lora.hyper_lora_modules, tokens_list):
            for key, (down, up) in module(tokens, mode='base').items():
                lora_key = f'{name}_{key}'
                lora_weights[f'{lora_key}.alpha'] = torch.tensor(float(down.shape[0])) * 0.5 # lora rank // 2
                lora_weights[f'{lora_key}.lora_down.weight'] = down.cpu()
                lora_weights[f'{lora_key}.lora_up.weight'] = up.cpu()
        return (lora_weights, )


class HyperLoRAApplyLoRANode:

    @classmethod
    def INPUT_TYPES(cls):
        return inputs_def(required=[
            custom_field('model', type_name='MODEL'),
            custom_field('lora', type_name='LORA'),
            float_field('weight', default=0.8, minimum=-1.5, maximum=1.5, step=0.01)
        ])

    RETURN_TYPES = ('MODEL', )
    FUNCTION = 'execute'
    CATEGORY = 'HyperLoRA'

    def execute(self, model: ModelPatcher, lora, weight):
        model, _ = load_lora_for_models(model, None, lora, weight, 0.0)
        return (model, )


class HyperLoRAFaceAttrNode:

    @classmethod
    def INPUT_TYPES(cls):
        return inputs_def(required=[
            custom_field('hyper_lora', type_name='HYPER_LORA'),
            image_field('images')
        ])

    RETURN_TYPES = ('FACE_ATTR', )
    FUNCTION = 'execute'
    CATEGORY = 'HyperLoRA'

    def execute(self, hyper_lora: HyperLoRA, images: torch.Tensor):
        images = tensor2images(images)
        face_attrs = []
        has_face = False
        for image in images:
            bgr_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            for size in range(640, 128, -128):
                hyper_lora.face_analyzer.det_model.input_size = (size, size)
                faces = hyper_lora.face_analyzer.get(bgr_image)
                if len(faces) > 0:
                    has_face = True
                    break
            face_attr = FaceAttrResp(n_face=len(faces), w=image.width, h=image.height, faces=[])
            for face in faces:
                face_attr.faces.append(FaceAttrInfo(rect=face.bbox, landmarks=face.landmark_2d_106))
            face_attrs.append(face_attr)
        assert has_face, 'No face detected!'
        return (face_attrs, )


class HyperLoRAUniLoaderNode:

    @classmethod
    def INPUT_TYPES(cls):
        cls.CONFIG_NODE = HyperLoRAConfigNode()
        cls.LOADER_NODE = HyperLoRALoaderNode()
        return inputs_def(required=[
            enum_field('image_processor', options=list_models('hyper_lora/clip_processor')),
            enum_field('image_encoder', options=list_models('hyper_lora/clip_vit')),
            enum_field('encoder_types', options=[ 'clip', 'arcface', 'clip + arcface' ]),
            enum_field('face_analyzer', options=list_models('insightface/models')),
            enum_field('model', options=list_models('hyper_lora/hyper_lora')),
            enum_field('dtype', options=[ 'fp16', 'bf16', 'fp32' ])
        ])

    RETURN_TYPES = ('HYPER_LORA', )
    FUNCTION = 'execute'
    CATEGORY = 'HyperLoRA'

    def execute(self, image_processor, image_encoder, encoder_types, face_analyzer, model, dtype):
        config = HyperLoRAUniLoaderNode.CONFIG_NODE.execute(**{
            'image_processor': image_processor,
            'image_encoder': image_encoder,
            'resampler.dim': 1024,
            'resampler.dim_head': 64,
            'resampler.heads': 12,
            'resampler.depth': 4,
            'resampler.ff_mult': 4,
            'encoder_types': encoder_types,
            'face_analyzer': face_analyzer,
            'id_embed_dim': 512,
            'num_id_tokens': 16,
            'hyper_dim': 128,
            'lora_rank': 8,
            'has_base_lora': False
        })[0]
        return HyperLoRAUniLoaderNode.LOADER_NODE.execute(config, model, dtype)


class HyperLoRAUniGenerateIDLoRANode:

    @classmethod
    def INPUT_TYPES(cls):
        cls.FACE_ATTR_NODE = HyperLoRAFaceAttrNode()
        cls.ID_COND_NODE = HyperLoRAIDCondNode()
        cls.GEN_ID_LORA_NODE = HyperLoRAGenerateIDLoRANode()
        return inputs_def(required=[
            custom_field('hyper_lora', type_name='HYPER_LORA'),
            image_field('images'),
            bool_field('grayscale', default=False),
            bool_field('remove_background', default=True)
        ])

    RETURN_TYPES = ('LORA', )
    FUNCTION = 'execute'
    CATEGORY = 'HyperLoRA'

    def execute(self, hyper_lora, images, grayscale, remove_background):
        face_attrs = HyperLoRAUniGenerateIDLoRANode.FACE_ATTR_NODE.execute(hyper_lora, images)[0]
        id_conds = HyperLoRAUniGenerateIDLoRANode.ID_COND_NODE.execute(hyper_lora, images, face_attrs, grayscale, remove_background)[0]
        return HyperLoRAUniGenerateIDLoRANode.GEN_ID_LORA_NODE.execute(hyper_lora, id_conds)


HYPER_LORA_CLASS_MAPPINGS = {
    'HyperLoRAConfig': HyperLoRAConfigNode,
    'HyperLoRALoader': HyperLoRALoaderNode,
    'HyperLoRAIDCond': HyperLoRAIDCondNode,
    'HyperLoRABaseCond': HyperLoRABaseCondNode,
    'HyperLoRAGenerateIDLoRA': HyperLoRAGenerateIDLoRANode,
    'HyperLoRAGenerateBaseLoRA': HyperLoRAGenerateBaseLoRANode,
    'HyperLoRAApplyLoRA': HyperLoRAApplyLoRANode,
    'HyperLoRAFaceAttr': HyperLoRAFaceAttrNode,
    'HyperLoRAUniLoader': HyperLoRAUniLoaderNode,
    'HyperLoRAUniGenerateIDLoRA': HyperLoRAUniGenerateIDLoRANode
}

HYPER_LORA_DISPLAY_NAME_MAPPINGS = {
    'HyperLoRAConfig': 'HyperLoRA Config',
    'HyperLoRALoader': 'HyperLoRA Loader',
    'HyperLoRAIDCond': 'HyperLoRA ID Cond',
    'HyperLoRABaseCond': 'HyperLoRA Base Cond',
    'HyperLoRAGenerateIDLoRA': 'HyperLoRA Generate ID LoRA',
    'HyperLoRAGenerateBaseLoRA': 'HyperLoRA Generate Base LoRA',
    'HyperLoRAApplyLoRA': 'HyperLoRA Apply LoRA',
    'HyperLoRAFaceAttr': 'HyperLoRA Face Attr',
    'HyperLoRAUniLoader': 'HyperLoRA Uni Loader',
    'HyperLoRAUniGenerateIDLoRA': 'HyperLoRA Uni Generate ID LoRA'
}
