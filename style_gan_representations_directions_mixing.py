# -*- coding: utf-8 -*-
"""style_gan_representations_directions_mixing.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ceNp_wQ458xrn9ujTsC4M723SZc8bz8W

![StyleGAN2 ADA](https://raw.githubusercontent.com/yagan93/stylegan-encoder/master/illustrations/stylegan2_ada.jpg)

In 2018 Nvidia introduced StyleGAN [A Style-Based Generator Architecture for Generative Adversarial Networks](https://arxiv.org/abs/1812.04948). Shortly after they released StyleGAN2 [Analyzing and Improving the Image Quality of StyleGAN](https://arxiv.org/abs/1912.04958) where they removed various artifacts. About 9 months ago they published a third paper called StyleGAN2 ADA [Training Generative Adversarial Networks with Limited Data](https://arxiv.org/abs/2006.06676) where they proposed an adaptive
discriminator augmentation mechanism that significantly stabilizes training in
limited data regimes. The approach does not require changes to loss functions
or network architectures, and is applicable both when training from scratch and when fine-tuning an existing GAN on another dataset. We demonstrate, on several datasets, that good results are now possible using only a few thousand training images, often matching StyleGAN2 results with an order of magnitude fewer images. They expect this to open up new application domains for GANs. Hereby, Nvidia released multiple pretrained networks as pickled instances available on [Google Drive](https://drive.google.com/drive/folders/1MASQyN5m0voPcx7-9K0r5gObhvvPups7).

If you are not familiar with GANs in general I advise you to browse through the notebooks created by [Jeff Heaton](https://github.com/jeffheaton). Besides, there are multiple pages that give you a feeling of what a [Generator](https://www.thispersondoesnotexist.com/) and [Discriminator](http://www.whichfaceisreal.com/) feel like in action. This notebook is intended to adress topics such as applying trained latent directions and creating own latent representations of raw images. This based on a fork by [Spiorf](https://github.com/spiorf).

### Applying latent directions to representations
First things first. **Clone the fork by yagan93** from github.
"""

# Forked from !git clone https://github.com/NVlabs/stylegan.git
# Forked from !git clone https://github.com/Puzer/stylegan-encoder.git
!git clone https://github.com/yagan93/stylegan-encoder.git stylegan

"""Install the required dependencies and make sure this **instance runs on a GPU** (runtime - change runetime - select GPU). Double check with the command **!nvidia-smi**. If Colab requires you to **restart the notebook**, do so! """

!pip3 uninstall tensorflow -y
!pip3 install tensorflow==1.15.2
!pip3 install keras==2.3.1
!pip3 install tensorflow-gpu==1.14
!nvidia-smi

"""Import the modules below. In case you run into **dnnlib/dnnlib.tflib errors**, affirm that the **correct tensorflow version is installed**."""

import sys
sys.path.insert(0, "/content/stylegan")
from tqdm.notebook import tqdm
import pickle
import torch
import PIL.Image
import matplotlib.pyplot as plt
import numpy as np
import stylegan.dnnlib.tflib as tflib
import stylegan.config
from stylegan.encoder.generator_model import Generator

"""**Download the trained network** as pickle instance from the provided google drive. If you run into **google quota** errors, try again later or log into a different account.

"""

URL_FFHQ = 'https://drive.google.com/uc?id=1MEGjdvVpUsu1jB4zrXZN7Y4kBBOzizDQ'
tflib.init_tf()
print(f'Loading networks from "{URL_FFHQ}"...')
with stylegan.dnnlib.util.open_url(URL_FFHQ, cache_dir=stylegan.config.cache_dir) as f:
    generator_network, discriminator_network, Gs_network = pickle.load(f)
generator = Generator(Gs_network, batch_size=1, randomize_noise=False)

"""Here's where the **fun begins**. For demonstration purposes we used the representations of trump and hillary. If you **keen on playing around with game of thrones characters** by [Iyaja](https://github.com/iyaja), go check out ffhq_dataset/latent_representations. Same goes for **latent directions** by [Spiorf](https://github.com/spiorf). You find them in the folder ffhq_dataset/latent_directions. You will notice that they are obviously biased."""

def generate_image(latent_vector):
  latent_vector = latent_vector.reshape((1, 18, 512))
  generator.set_dlatents(latent_vector)
  img_array = generator.generate_images()[0]
  img = PIL.Image.fromarray(img_array, 'RGB')
  return img.resize((256, 256))

def move_and_show(latent_vector, direction, coeffs):
  fig,ax = plt.subplots(1, len(coeffs), figsize=(15, 10), dpi=80)
  for i, coeff in enumerate(coeffs):
      new_latent_vector = latent_vector.copy()
      new_latent_vector[:8] = (latent_vector + coeff*direction)[:8]
      ax[i].imshow(generate_image(new_latent_vector))
      ax[i].set_title('Coeff: %0.1f' % coeff)
  [x.axis('off') for x in ax]
  plt.show()

def move_and_save(latent_vector, direction, coeffs):
  for i, coeff in enumerate(coeffs):
      new_latent_vector = latent_vector.copy()
      new_latent_vector[:8] = (latent_vector + coeff*direction)[:8]
      img = generate_image(new_latent_vector)
      img.save(f'./picture_{i}.png')

hillary_clinton = np.load('stylegan/ffhq_dataset/latent_representations/hillary_clinton_01.npy')
donald_trump = np.load('stylegan/ffhq_dataset/latent_representations/donald_trump_01.npy')

smile_direction = np.load('stylegan/ffhq_dataset/latent_directions/smile_direction.npy')
facialhair_direction = np.load('stylegan/ffhq_dataset/latent_directions/facialhair_direction.npy')
lipMakeup_direction = np.load('stylegan/ffhq_dataset/latent_directions/lipMakeup_direction.npy')
disgust_direction = np.load('stylegan/ffhq_dataset/latent_directions/disgust_direction.npy')

move_and_show(donald_trump, smile_direction, [-1, 0, 2])
move_and_save(hillary_clinton, smile_direction, [-1, 0, 2])

"""### Generate own latent representations of raw images
Create **all folders** needed for the following commands.
"""

!mkdir own_raw_images own_aligned_images own_generated_images own_latent_representations output

"""**Upload your own images** (common formats) to ./raw_images and align them for further encoding. If you want to dig a bit deeper into the **alignment process** go check out the [blog](https://www.programmersought.com/article/31946614351/)
on programmersought.com.
"""

!python3 stylegan/align_images.py own_raw_images/ own_aligned_images/

"""**Encode aligned images** and generate representations. This may take a while!"""

!python3 stylegan/encode_images.py own_aligned_images/ own_generated_images/ own_latent_representations/

"""**Adjust the np.load path** and replace YOUR_OWN_REPRESENTATION with the actual representation generated by the script stylegan/encode_images.py. You will find it in the folder own_latent_representations. **Smile**!"""

own_latent_representation = np.load('own_latent_representations/YOUR_OWN_REPRESENTATION.npy')

smile_direction = np.load('stylegan/ffhq_dataset/latent_directions/smile_direction.npy')
facialhair_direction = np.load('stylegan/ffhq_dataset/latent_directions/facialhair_direction.npy')
lipMakeup_direction = np.load('stylegan/ffhq_dataset/latent_directions/lipMakeup_direction.npy')
disgust_direction = np.load('stylegan/ffhq_dataset/latent_directions/disgust_direction.npy')

move_and_show(own_latent_representation, smile_direction, [-1, 0, 2])

"""The following code will **move between the provided coeffs** in the latent space, take a snapshot for each step and create a movie.mp4."""

def latent_space_video(latent_vector, direction, source_coeff, target_coeff, steps, output_dir):
  coeff_steps = (target_coeff-source_coeff)/steps if target_coeff>=source_coeff else (source_coeff-target_coeff)/steps
  temp_latent_vector = latent_vector.copy()
  idx = 0
  for i in tqdm(range(steps), desc=f"Step {idx}"):
    temp_latent_vector[:8] = (temp_latent_vector + coeff_steps*direction)[:8]
    img = generate_image(temp_latent_vector)
    img.save(f'{output_dir}/frame-{i}.png')
    idx += 1
  !ffmpeg -r 30 -i {output_dir}/frame-%d.png -vcodec mpeg4 -y {output_dir}/movie.mp4

latent_space_video(own_latent_representation, smile_direction, -1, 1, 100, "output")

"""Apply **style mixing** between own_latent_representation (primary) and donald_trump (secondary)."""

def draw_style_mixing_figure(png, Gs, w, h, src_dlatents, dst_dlatents, style_ranges):
    print(png)
    src_images = Gs.components.synthesis.run(src_dlatents, randomize_noise=False, **synthesis_kwargs)
    dst_images = Gs.components.synthesis.run(dst_dlatents, randomize_noise=False, **synthesis_kwargs)

    canvas = PIL.Image.new('RGB', (w * (len(src_dlatents) + 1), h * (len(dst_dlatents) + 1)), 'white')
    for col, src_image in enumerate(list(src_images)):
        canvas.paste(PIL.Image.fromarray(src_image, 'RGB'), ((col + 1) * w, 0))
    for row, dst_image in enumerate(list(dst_images)):
        canvas.paste(PIL.Image.fromarray(dst_image, 'RGB'), (0, (row + 1) * h))
        row_dlatents = np.stack([dst_dlatents[row]] * len(src_dlatents))
        row_dlatents[:, style_ranges[row]] = src_dlatents[:, style_ranges[row]]
        row_images = Gs.components.synthesis.run(row_dlatents, randomize_noise=False, **synthesis_kwargs)
        for col, image in enumerate(list(row_images)):
            canvas.paste(PIL.Image.fromarray(image, 'RGB'), ((col + 1) * w, (row + 1) * h))
    canvas.save(png)
    return canvas.resize((512,512))


synthesis_kwargs = dict(output_transform=dict(func=tflib.convert_images_to_uint8, nchw_to_nhwc=True), minibatch_size=1)
_Gs_cache = dict()
draw_style_mixing_figure('style-mixing.png', Gs_network, w=1024, h=1024, src_dlatents=donald_trump.reshape((1, 18, 512)), dst_dlatents=own_latent_representation.reshape((1, 18, 512)), style_ranges=[range(6,14)])