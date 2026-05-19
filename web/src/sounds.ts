let ctx: AudioContext | null = null

function getCtx(): AudioContext {
  if (!ctx) ctx = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)()
  return ctx
}

function tone(freq: number, dur: number, type: OscillatorType = 'sine', vol = 0.25) {
  try {
    const c = getCtx()
    const osc = c.createOscillator()
    const gain = c.createGain()
    osc.connect(gain)
    gain.connect(c.destination)
    osc.type = type
    osc.frequency.value = freq
    gain.gain.setValueAtTime(vol, c.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.001, c.currentTime + dur)
    osc.start(c.currentTime)
    osc.stop(c.currentTime + dur)
  } catch { /* ignore */ }
}

export const sounds = {
  click:   () => tone(700, 0.06, 'square', 0.15),
  correct: () => { tone(523, 0.15); setTimeout(() => tone(659, 0.15), 100); setTimeout(() => tone(784, 0.25), 200) },
  wrong:   () => tone(220, 0.3, 'sawtooth', 0.2),
  win:     () => { [523,659,784,1047].forEach((f, i) => setTimeout(() => tone(f, 0.2), i * 150)) },
  badge:   () => { for (let i = 0; i < 8; i++) setTimeout(() => tone(500 + i * 80, 0.12), i * 60) },
}
