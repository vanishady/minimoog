from pyo import *
            

class MiniMoog(PyoObject):

    """
    This class instances a subtractive synthesizer with 3 oscillators, a noise generator and one fourth-order lowpass resonant filter Moog alike.
    You can control the oscillators, the noise generator and filter parameters via GUI.
    You can play the syntheziser using you computer keyboard or the MIDI keyboard on your desktop.
    :Parent: :py:class:`PyoObject`
    :Args:
      type1 : int, optional
          Waveform type of the first oscillator. Eight possible values :  
            0. Saw up
            1. Saw down  
            2. Square  
            3. Triangle  
            4. Pulse  
            5. Bipolar pulse  
            6. Sample and hold  
            7. Modulated Sine
            Defaults to 0.           
      sharp1 : float, optional
          Sharpness factor of the first oscillator. Sharper waveform results  
          in more harmonics in the spectrum. Defaults to 0.5.          
      mul1 : float, optional
          Multiplication factor of the first oscillator. It allows to set the oscillator amplitude.
          It goes from 0 to 1. Defaults to 0.5.
          
      type2 : int, optional
          Waveform type of the second oscillator. Eight possible values :  
            0. Saw up
            1. Saw down  
            2. Square  
            3. Triangle  
            4. Pulse  
            5. Bipolar pulse  
            6. Sample and hold  
            7. Modulated 
            Default to 0.
      sharp2 : float, optional
          Sharpness factor of the second oscillator. Sharper waveform results  
          in more harmonics in the spectrum. Defaults to 0.5.
      mul2 : float, optional
          Multiplication factor of the second oscillator. It allows to set the oscillator amplitude.
          It goes from 0 to 1. Defaults to 0.1.
      interval2 : int, optional
          Number of semitones to add or to substract to the main frequency (oscillator-1).
          Detune Range: [-8, +8] semitones. Defaults to 0.
      range2 : int, optional
          Selects the fundamental octave for the second oscillator over a 5 octave range [1, 6]. Defaults to 1.
          
      switch3 : int, optional
          Set the third oscillator on\off (1 - 0). Defaults to 0 (off).
      type3 : int, optional
          Waveform type of the third oscillator. Eight possible values :  
            0. Saw up
            1. Saw down  
            2. Square  
            3. Triangle  
            4. Pulse  
            5. Bipolar pulse  
            6. Sample and hold  
            7. Modulated Sine
            Default to 0.
      sharp3 : float, optional
          Sharpness factor of the third oscillator. Sharper waveform results  
          in more harmonics in the spectrum. Defaults to 0.5.
      mul3 : float, optional
          Multiplication factor of the third oscillator. It allows to set the oscillator amplitude.
          It goes from 0 to 1. Defaults to 0.1.
      interval3 : int, optional
          Number of semitones to add or to substract to the main frequency (oscillator-1).
          Detune Range: [-8, +8] semitones. Defaults to 0.
      range3 : int, optional
          Selects the fundamental octave for the third oscillator over a 5 octave range [1, 6]. Defaults to 1.
          
      cutoffFact : float, optional
          Factor of the cutoff frequency of the filter. Defaults to 0.5.
      res: float, optional  
          Amount of Resonance of the filter, usually between 0 (no resonance)  
          and 1 (medium resonance). Default to 0.5

      voiceSel : int, optional
          Determines what type of noise is used.
          0 - White Noise
          1 - Pink Noise
          Defaults to 0.
      mulWhiteNoise : float, optional
          Multiplication factor of noise generator. It allows to set the noise amplitude.
          It goes from 0 to 1. Defaults to 0.
      mulPinkNoise : float, optional
          Multiplication factor of noise generator. It allows to set the noise amplitude.
          It goes from 0 to 1. Defaults to 0.

      lfotremolo : float, optional
          Frequency of lfo2, providing a tremolo effect.
          Defaults to 2.
      selector_adsrtremolo : float, optional
          Interpolates between ADSR envelope (self._env) and LFO (lfo1).
          Defaults to 0 (ADSR envelope).
          
      lfovibrato : float, optional
          Frequency of lfo2, providing a vibrato effect.
          Defaults to 2.
      selector_adsrvibrato : float, optional
          Interpolates between no modulation on frequency (self._nomod), ADSR envelope (self._env) and LFO (lfo2).
          Defaults to 0 (no modulation).
          
          
    >>> s=Server().boot()
    >>> myminimoog = MiniMoog().out()
    >>> myminimoog.ctrl()
    """

    def __init__(self, type1=0, sharp1=1, mul1=0.5,
                 type2=0, sharp2=1, mul2=0.1, interval2=0, range2=0,
                 switch3=0,type3=0, sharp3=1, mul3=0.1, interval3=0, range3=0,
                 cutoffFact=0.5, res=0.5,  
                 voiceSel=0, mulWhiteNoise=0, mulPinkNoise=0,
                 lfotremolo=2, selector_adsrtremolo=0, lfovibrato=2, selector_adsrvibrato=0):
        
        # Call superclass (PyoObject) constructor
        super().__init__()
        
        # Define and initialize instance attributes
        self._type1 = type1           
        self._sharp1 = sharp1
        self._mul1 = mul1
        
        self._type2 = type2
        self._sharp2 = sharp2
        self._mul2 = mul2
        self._interval2 = interval2
        self._range2 = range2

        self._switch3 = switch3
        self._type3 = type3
        self._sharp3 = sharp3
        self._mul3 = mul3
        self._interval3 = interval3
        self._range3 = range3
        
        self._cutoffFact = cutoffFact
        self._res = res
        
        self._voiceSel = voiceSel
        self._mulWhiteNoise = mulWhiteNoise
        self._mulPinkNoise = mulPinkNoise

        self._lfotremolo = lfotremolo
        self._nomod = Sig(1)
        self._lfovibrato = lfovibrato
        self._selector_adsrtremolo = selector_adsrtremolo
        self._selector_adsrvibrato = selector_adsrvibrato

        # pitches in Hz
        notes = Notein()
        # Show a keyboard widget to supply MIDI events
        notes.keyboard()
       
        # Note pitches
        self._freqs = MToF(notes["pitch"])
        
        # ADSR on note amplitudes
        self._env = MidiAdsr(notes["velocity"], attack=0.05, decay=0.4, sustain=0.5, release=0.5, mul=0.65)

        # Creates an LFO for tremolo
        self._lfo1 = LFO(freq = lfotremolo, type=7, mul=0.5, add=1)
        self._ampmodmix = Selector([self._env, self._lfo1]) # (0=ADSR, 1=Tremolo)
        
        # Creates an LFO for vibrato
        self._lfo2 = LFO(freq = lfovibrato, type=1, mul=0.1, add=1)
        self._freqmodmix = Selector([self._nomod, self._env, self._lfo2]) # (0=No Modulation, 1=ADSR, 2=Vibrato)
        

        # Define oscillator bank
        # Create the first oscillator
        self._osc1 = LFO(freq=self._freqs*self._freqmodmix, sharp=self._sharp1, type=self._type1, mul=self._ampmodmix*self._mul1)
        # Add the first oscillator to the second one
        self._osc2 = LFO(freq=(self._osc1.freq + (2**(1/12))*self._interval2)*self._range2, sharp=self._sharp2,
                         type=self._type2, mul=self._ampmodmix*self._mul2, add=self._osc1)
        # Add the sum the previuos two oscillators to the third one
        self._osc3 = LFO(freq=(self._osc1.freq + (2**(1/12))*self._interval3)*self._range3, sharp=self._sharp3,
                         type=self._type3, mul=self._ampmodmix*self._mul3*self._switch3, add=self._osc2)
        
        # Noise generator
        self._whitenoise = Noise()
        self._pinknoise = PinkNoise()
        self._sel = Selector([self._whitenoise,self._pinknoise]) #(0=White, 1=Pink)

        # ADSR Filter
        self._envfilt = MidiAdsr(notes["velocity"],attack=0.05, decay=0.4, sustain=0.5, release=0.5, mul=0.65)
        
        # Filter the result of the sum of the three oscillators and noise generator with a Moog ladder filter alike
        self._filt = MoogLP(input=self._osc3+self._sel, freq=self._envfilt*20000*self._cutoffFact, res=self._res)
    
        # Make the signal stereo
        self._stereo = Pan(self._filt, outs=2, pan=0.5)

        # Define output seen by outside world: self._base_objs
        # Returned by getBaseObjects() method
        self._base_objs = self._stereo.getBaseObjects()

    def ctrl(self, map_list=None, title=None, wxnoserver=False):

        # Oscillator Bank
        self._map_list_osc = [SLMap(0, 7, "lin", "type1", self._type1, res='int', dataOnly=True), 
                              SLMap(0, 1, "lin", "sharp1", self._sharp1, res='float'), 
                              SLMap(0, 7, "lin", "type2", self._type2, res='int', dataOnly=True),
                              SLMap(0, 1, "lin", "sharp2", self._sharp2, res='float'),                              
                              SLMap(0, 1, "lin", "switch3", self._switch3, res='int', dataOnly=True),
                              SLMap(0, 7, "lin", "type3", self._type3, res='int', dataOnly=True),
                              SLMap(0, 1, "lin", "sharp3", self._sharp3, res='float')]
        super().ctrl(self._map_list_osc, 'Oscillator Bank', wxnoserver)

        # Range and semitones
        self._map_list_bank = [SLMap(-8, 8, "lin", "interval2", self._interval2, res='int', dataOnly=True),
                              SLMap(1, 6, "lin", "range2", self._range2, res='int', dataOnly=True),
                              SLMap(-8, 8, "lin", "interval3", self._interval3, res='int', dataOnly=True),
                              SLMap(1, 6, "lin", "range3", self._range3, res='int', dataOnly=True)]
        super().ctrl(self._map_list_bank, 'Oscillator Bank Control', wxnoserver)

        # Mixer and noise generator
        self._map_list_mixer = [SLMap(0.1, 1, "lin", "mul1", self._mul1, res='float', dataOnly=True),
                                SLMap(0.1, 1, "lin", "mul2", self._mul2, res='float', dataOnly=True),
                                SLMap(0.1, 1, "lin", "mul3", self._mul3, res='float', dataOnly=True),
                                SLMap(0, 1, "lin", "voiceSel", self._voiceSel, res='int', dataOnly=True),
                                SLMap(0, 1, "lin", "mulWhiteNoise", self._mulWhiteNoise, res='float', dataOnly=True),
                                SLMap(0, 1, "lin", "mulPinkNoise", self._mulPinkNoise, res='float', dataOnly=True)]
        super().ctrl(self._map_list_mixer, 'Mixer', wxnoserver)

        # Filter
        self._map_list_filt = [SLMap(0, 1, "lin", "cutoffFact", self._cutoffFact, res='float'),
                               SLMap(0, 1, "lin", "res", self._res, res='float')]
        super().ctrl(self._map_list_filt, 'Filter', wxnoserver)

        # ADSR on filter
        self._envfilt.ctrl(title = 'ADSR - FILTER')

        # ADSR on amplitude - LOUDNESS CONTOUR
        self._env.ctrl(title = 'ADSR - LOUDNESS CONTOUR')

        # Amplitude Modulation Mix
        self._map_list_ampmodmix = [SLMap(0, 1, "lin", "selector_adsrtremolo", self._selector_adsrtremolo, res='float', dataOnly=True),
                                    SLMap(1, 10, "lin", "lfotremolo", self._lfotremolo, res='float', dataOnly=True)]
        super().ctrl(self._map_list_ampmodmix, 'Amplitude Modulation Mix', wxnoserver)

        # Frequency Modulation Mix
        self._map_list_freqmodmix = [SLMap(0, 2, "lin", "selector_adsrvibrato", self._selector_adsrvibrato, res='float', dataOnly=True),
                                     SLMap(1, 10, "lin", "lfovibrato", self._lfovibrato, res='float', dataOnly=True)]
        super().ctrl(self._map_list_freqmodmix, 'Frequency Modulation Mix', wxnoserver)

                           

    def play(self, dur=0, delay=0):
        self._osc1.play(dur, delay)
        self._osc2.play(dur, delay)
        self._osc3.play(dur, delay)
        self._filt.play(dur, delay)
        self._stereo.play(dur, delay)
        return super().play(dur, delay)

    def stop(self):
        self._osc1.stop()
        self._osc2.stop()
        self._osc3.stop()
        self._filt.stop()
        self._stereo.stop()
        return super().stop()

    def out(self, chnl=0, inc=1, dur=0, delay=0):
        self._osc1.play(dur, delay)
        self._osc2.play(dur, delay)
        self._osc3.play(dur, delay)
        self._filt.play(dur, delay)
        self._stereo.play(dur, delay)
        return super().out(chnl, inc, dur, delay)

    def setType1(self, x):
        """
        Replace the `type1` attribute.
        :Args:
            x : int
                New `type1` attribute.
        """
        self._type1 = x
        self._osc1.type = x

    def setSharp1(self, x):
        """
        Replace the `sharp1` attribute.
        :Args:
            x : float 
                New `sharp1` attribute.
        """
        self._sharp1 = x
        self._osc1.sharp = x

    def setMul1(self, x):
        """
        Replace the `mul1` attribute.
        :Args:
            x : float 
                New `mul1` attribute.
        """
        self._mul1 = x
        self._osc1.mul = x*self._ampmodmix

    
    def setType2(self, x):
        """
        Replace the `type2` attribute.
        :Args:
            x : int
                New `type2` attribute.
        """
        self._type2 = x
        self._osc2.type = x

    def setSharp2(self, x):
        """
        Replace the `sharp2` attribute.
        :Args:
            x : float 
                New `sharp2` attribute.
        """
        self._sharp2 = x
        self._osc2.sharp = x

    def setMul2(self, x):
        """
        Replace the `mul2` attribute.
        :Args:
            x : float 
                New `mul2` attribute.
        """
        self._mul2 = x
        self._osc2.mul = x*self._ampmodmix

    def setInterval2(self, x):
        """
        Replace the `interval2` attribute.
        :Args:
            x : int
                New `interval2` attribute.
        """
        self._interval2 = x
        self._osc2.freq = (self._osc1.freq + (2**(1/12))*x)*self._range2

    def setRange2(self, x):
        """
        Replace the `range2` attribute.
        :Args:
            x : int
                New `range2` attribute.
        """
        self._range2 = x
        self._osc2.freq = (self._osc1.freq + (2**(1/12))*self._interval2)*x

    def setSwitch3(self, x):
        """
        Replace the `switch3` attribute.
        :Args:
            x : int
                New `switch3` attribute.
        """
        self._switch3 = x
        self._osc3.mul = x*self._ampmodmix*self._mul3

    def setType3(self, x):
        """
        Replace the `type3` attribute.
        :Args:
            x : int
                New `type3` attribute.
        """
        self._type3 = x
        self._osc3.type = x

    def setSharp3(self, x):
        """
        Replace the `sharp3` attribute.
        :Args:
            x : float 
                New `sharp3` attribute.
        """
        self._sharp3 = x
        self._osc3.sharp = x

    def setMul3(self, x):
        """
        Replace the `mul3` attribute.
        :Args:
            x : float 
                New `mul3` attribute.
        """
        self._mul3 = x
        self._osc3.mul = self._ampmodmix*x*self._switch3

    def setInterval3(self, x):
        """
        Replace the `interval3` attribute.
        :Args:
            x : int
                New `interval3` attribute.
        """
        self._interval3 = x
        self._osc3.freq = (self._osc1.freq + (2**(1/12))*x)*self._range3

    def setRange3(self, x):
        """
        Replace the `range3` attribute.
        :Args:
            x : int
                New `range3` attribute.
        """
        self._range3 = x
        self._osc3.freq = (self._osc1.freq + (2**(1/12))*self._interval3)*x

    def setVoiceSel(self, x):
        """
        Replace the `voiceSel` attribute.
        :Args:
            x : int
                New `VoiseSel` attribute.
        """
        self._voiceSel = x
        self._sel.voice = x    

    def setMulWhiteNoise(self, x):
        """
        Replace the `mulWhiteNoise` attribute.
        :Args:
            x : float 
                New `mulWhiteNoise` attribute.
        """
        self._mulWhiteNoise = x
        self._whitenoise.mul = x

    def setMulPinkNoise(self, x):
        """
        Replace the `mulPinkNoise` attribute.
        :Args:
            x : float 
                New `mulPinkNoise` attribute.
        """
        self._mulPinkNoise = x
        self._pinknoise.mul = x

    def setCutoffFact(self, x):
        """
        Replace the `cutoffFact` attribute.
        :Args:
            x : float 
                New `cutoffFact` attribute.
        """
        self._cutoffFact = x
        self._filt.freq = self._envfilt*20000*x
    
    def setRes(self, x):
        """
        Replace the `res` attribute.
        :Args:
            x : float 
                New `res` attribute.
        """
        self._res = x
        self._filt.res = x
        
    def setLFOtremolo(self, x):
        """
        Replace the `lfotremolo` attribute.
        :Args:
            x : float 
                New `lfotremolo` attribute.
        """
        self._lfotremolo = x
        self._lfo1.freq = x


    def setLFOvibrato(self, x):
        """
        Replace the `lfovibrato` attribute.
        :Args:
            x : float 
                New `lfovibrato` attribute.
        """
        self._lfovibrato = x
        self._lfo2.freq = x

    def setSelectorADSRVibrato(self, x):
        """
        Replace the `selector_adsrvibrato` attribute.
        :Args:
            x : float 
                New `selector_adsrvibrato` attribute.
        """
        self._selector_adsrvibrato = x
        self._freqmodmix.voice = x
    
    def setSelectorADSRTremolo(self, x):
        """
        Replace the `selector_adsrtremolo` attribute.
        :Args:
            x : float 
                New `selector_adsrtremolo` attribute.
        """
        self._selector_adsrtremolo = x
        self._ampmodmix.voice = x

    @property
    def type1(self):
        """int. Type of osc1."""
        return self._type1
    @type1.setter
    def type1(self, x):
        self.setType1(x)
    
    @property
    def sharp1(self):
        """float. Sharp of osc1."""
        return self._sharp1
    @sharp1.setter
    def sharp1(self, x):
        self.setSharp1(x)

    @property
    def mul1(self):
        """float. Mul of osc1."""
        return self._mul1
    @mul1.setter
    def mul1(self, x):
        self.setMul1(x)
    
    @property
    def type2(self):
        """int. Type of osc2."""
        return self._type2
    @type2.setter
    def type2(self, x):
        self.setType2(x)
    
    @property
    def sharp2(self):
        """float. Sharp of osc2."""
        return self._sharp2
    @sharp2.setter
    def sharp2(self, x):
        self.setSharp2(x)
        
    @property
    def mul2(self):
        """float. Mul of osc2."""
        return self._mul2
    @mul2.setter
    def mul2(self, x):
        self.setMul2(x)

    @property
    def interval2(self):
        """int. Interval of osc2."""
        return self._interval2
    @interval2.setter
    def interval2(self, x):
        self.setInterval2(x)

    @property
    def range2(self):
        """int. Range of osc2."""
        return self._range2
    @range2.setter
    def range2(self, x):
        self.setRange2(x)
        
    @property
    def switch3(self):
        """int. Switch of osc3."""
        return self._switch3
    @switch3.setter
    def switch3(self, x):
        self.setSwitch3(x)

    @property
    def type3(self):
        """int. Type of osc3."""
        return self._type3
    @type3.setter
    def type3(self, x):
        self.setType3(x)

    @property
    def sharp3(self):
        """float. Sharp of osc3."""
        return self._sharp3
    @sharp3.setter
    def sharp3(self, x):
        self.setSharp3(x)

    @property
    def mul3(self):
        """float. Mul of osc3."""
        return self._mul3
    @mul3.setter
    def mul3(self, x):
        self.setMul3(x)

    @property
    def interval3(self):
        """int. Interval of osc3."""
        return self._interval3
    @interval3.setter
    def interval3(self, x):
        self.setInterval3(x)

    @property
    def range3(self):
        """int. Range of osc3."""
        return self._range3
    @range3.setter
    def range3(self, x):
        self.setRange3(x)
        
    @property
    def voiceSel(self):
        """int. Selector of Noise Generator."""
        return self._voiceSel
    @voiceSel.setter
    def voiceSel(self, x):
        self.setVoiceSel(x)
        
    @property
    def mulWhiteNoise(self):
        """float. Mul of White Noise Generator."""
        return self._mulWhiteNoise
    @mulWhiteNoise.setter
    def mulWhiteNoise(self, x):
        self.setMulWhiteNoise(x)

    @property
    def mulPinkNoise(self):
        """float. Mul of Pink Noise Generator."""
        return self._mulPinkNoise
    @mulPinkNoise.setter
    def mulPinkNoise(self, x):
        self.setMulPinkNoise(x)
        
    @property
    def cutoffFact(self):
        """float. CutoffFact of filt."""
        return self._cutoffFact
    @cutoffFact.setter
    def cutoffFact(self, x):
        self.setCutoffFact(x)

    @property
    def res(self):
        """float. Res of filt."""
        return self._res
    @res.setter
    def res(self, x):
        self.setRes(x)

    @property
    def lfotremolo(self):
        """float. Frequency of lfo2."""
        return self._lfotremolo
    @lfotremolo.setter
    def lfotremolo(self, x):
        self.setLFOtremolo(x)

    @property
    def lfovibrato(self):
        """float. Frequency of lfo1."""
        return self._lfovibrato
    @lfovibrato.setter
    def lfovibrato(self, x):
        self.setLFOvibrato(x)

    @property
    def selector_adsrtremolo(self):
        """float. Interpolation between ADSR and lfo1."""
        return self._selector_adsrtremolo
    @selector_adsrtremolo.setter
    def selector_adsrtremolo(self, x):
        self.setSelectorADSRTremolo(x)
        

    @property
    def selector_adsrvibrato(self):
        """float. Interpolation between no modulation, ADSR and lfo2."""
        return self._selector_adsrvibrato
    @selector_adsrvibrato.setter
    def selector_adsrvibrato(self, x):
        self.setSelectorADSRVibrato(x)




if __name__ == "__main__":
    
    s=Server().boot()
    s.amp=0.5

    myminimoog = MiniMoog().out()
    myminimoog.ctrl()

    s.gui(locals())
