import React, { useState, useEffect } from 'react'
import Character from '../components/Character'
import { Progress } from '../types'
import { sounds } from '../sounds'

interface Props {
  progress: Progress
  onUpdateName: (name: string) => void
  onPlay: () => void
  onBadges: () => void
}

const MenuScene: React.FC<Props> = ({ progress, onUpdateName, onPlay, onBadges }) => {
  const [inputName, setInputName] = useState(progress.player_name)
  const [nameConfirmed, setNameConfirmed] = useState(!!progress.player_name)
  const [error, setError] = useState('')

  useEffect(() => { setInputName(progress.player_name); setNameConfirmed(!!progress.player_name) }, [progress.player_name])

  function confirmName() {
    const n = inputName.trim()
    if (!n) { setError('Vul je naam in!'); return }
    onUpdateName(n)
    setNameConfirmed(true)
    sounds.correct()
  }

  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      justifyContent: 'center', height: '100vh', gap: '24px',
      background: 'radial-gradient(ellipse at 50% 0%, #2A2A6E 0%, #1A1A2E 70%)',
      padding: '24px',
    }}>
      {/* Stars background */}
      <div style={{ position: 'absolute', inset: 0, overflow: 'hidden', pointerEvents: 'none' }}>
        {Array.from({ length: 60 }, (_, i) => (
          <div key={i} style={{
            position: 'absolute',
            width: i % 5 === 0 ? 4 : 2,
            height: i % 5 === 0 ? 4 : 2,
            borderRadius: '50%',
            background: 'white',
            opacity: 0.3 + (i % 5) * 0.1,
            top: `${(i * 17) % 100}%`,
            left: `${(i * 23) % 100}%`,
          }}/>
        ))}
      </div>

      {/* Logo */}
      <div style={{ textAlign: 'center', position: 'relative' }}>
        <h1 style={{
          fontFamily: 'var(--font-head)',
          fontSize: 'clamp(3rem, 8vw, 5rem)',
          color: 'var(--primary)',
          textShadow: '0 4px 20px rgba(247,183,49,0.4)',
          lineHeight: 1,
        }}>CodeAap</h1>
        <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: '1.1rem', marginTop: 8 }}>
          Leer coderen, stap voor stap!
        </p>
      </div>

      {/* Monkey */}
      <Character action={nameConfirmed ? 'dance' : 'idle'} size={130}/>

      {/* Name input or play buttons */}
      {!nameConfirmed ? (
        <div className="panel" style={{ width: '100%', maxWidth: 400, textAlign: 'center' }}>
          <p style={{ fontFamily: 'var(--font-head)', fontSize: '1.4rem', marginBottom: 16 }}>
            Wat is jouw naam?
          </p>
          <input
            autoFocus
            value={inputName}
            maxLength={12}
            onChange={e => { setInputName(e.target.value); setError('') }}
            onKeyDown={e => e.key === 'Enter' && confirmName()}
            style={{
              width: '100%', padding: '12px 16px',
              borderRadius: 12, border: '2px solid var(--primary)',
              background: 'rgba(0,0,0,0.3)', color: 'white',
              fontFamily: 'var(--font-head)', fontSize: '1.4rem',
              outline: 'none', textAlign: 'center',
            }}
            placeholder="Typ je naam..."
          />
          {error && <p style={{ color: 'var(--accent)', marginTop: 8 }}>{error}</p>}
          <button className="btn btn-green btn-lg" style={{ marginTop: 16, width: '100%' }}
                  onClick={confirmName}>
            OK!
          </button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14, width: '100%', maxWidth: 320 }}>
          <p style={{ textAlign: 'center', fontFamily: 'var(--font-head)', fontSize: '1.5rem', color: 'var(--primary)' }}>
            Hoi, {progress.player_name}! 👋
          </p>
          <button className="btn btn-green btn-lg" style={{ width: '100%' }}
                  onClick={() => { sounds.click(); onPlay() }}>
            ▶ Spelen
          </button>
          <button className="btn btn-primary" style={{ width: '100%' }}
                  onClick={() => { sounds.click(); onBadges() }}>
            🏅 Mijn Badges
          </button>
          <button className="btn btn-panel btn-sm" style={{ width: '100%' }}
                  onClick={() => setNameConfirmed(false)}>
            Naam wijzigen
          </button>
        </div>
      )}
    </div>
  )
}

export default MenuScene
