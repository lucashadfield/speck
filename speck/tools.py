__all__ = ['SpeckWidget']

import ipywidgets

from speck.noise import SineNoise
from speck.colour import GradientColour


class SpeckWidget:
    weights_W = ipywidgets.FloatRangeSlider(
        value=[0, 1], min=0, max=1, steps=0.01, description='Line Weight'
    )

    weight_clipping_W = ipywidgets.FloatRangeSlider(
        value=[0, 1], min=0, max=1, steps=0.01, description='Weight Clipping'
    )

    noise_profile_W = ipywidgets.Dropdown(
        value='parallel',
        options=['parallel', 'reflect', 'independent'],
        description='Noise Profile',
    )
    noise_scale_W = ipywidgets.FloatSlider(
        value=0.5, min=0, max=2, steps=0.05, description='Noise Scale'
    )
    noise_wave_count_W = ipywidgets.IntSlider(
        value=3, min=1, max=6, steps=1, description='Wave Count'
    )
    noise_base_freq_W = ipywidgets.FloatSlider(
        value=3, min=1, max=10, steps=0.5, description='Base Frequency'
    )
    noise_freq_factor_W = ipywidgets.FloatRangeSlider(
        value=[1, 3], min=0, max=10, steps=0.5, description='Frequency Multipliers'
    )
    noise_phase_offset_range_W = ipywidgets.FloatRangeSlider(
        value=[0, 2], min=0, max=360, steps=15, description='Phase Offset (degrees)'
    )
    colour_top_W = ipywidgets.ColorPicker(
        concise=True, description='Top Colour', value='white', disabled=False
    )
    colour_bot_W = ipywidgets.ColorPicker(
        concise=True, description='Bottom Colour', value='red', disabled=False
    )

    def __init__(self, speck_plot):
        self.speck_plot = speck_plot

    def _widget_func(
        self,
        weights,
        weight_clipping,
        noise_profile,
        noise_scale,
        noise_wave_count,
        noise_base_freq,
        noise_freq_factor,
        noise_phase_offset_range,
        colour_top,
        colour_bot,
    ):
        noise = SineNoise(
            profile=noise_profile,
            scale=noise_scale,
            wave_count=noise_wave_count,
            base_freq=noise_base_freq,
            freq_factor=noise_freq_factor,
            phase_offset_range=noise_phase_offset_range,
        )

        colour = GradientColour((colour_top, colour_bot))

        return self.speck_plot.draw(
            weights=weights,
            weight_clipping=weight_clipping,
            noise=noise,
            colour=colour,
            seed=1,
        )

    def interact(self):

        return ipywidgets.interact(
            self._widget_func,
            weights=self.weights_W,
            weight_clipping=self.weight_clipping_W,
            noise_profile=self.noise_profile_W,
            noise_scale=self.noise_scale_W,
            noise_wave_count=self.noise_wave_count_W,
            noise_base_freq=self.noise_base_freq_W,
            noise_freq_factor=self.noise_freq_factor_W,
            noise_phase_offset_range=self.noise_phase_offset_range_W,
            colour_top=self.colour_top_W,
            colour_bot=self.colour_bot_W,
        )
