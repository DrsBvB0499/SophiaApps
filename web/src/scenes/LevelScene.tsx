import React, { useState, useEffect, useRef, useCallback } from 'react'
import Character from '../components/Character'
import { Island, Level, LevelResult } from '../types'
import { BLOCK_COLORS, ISLAND_ICONS } from '../config'
import { sounds } from '../sounds'

interface Props {
  island: Island
  level: Level
  onComplete: (result: LevelResult) => void
  onBack: () => void
}

type CharAction = 'idle' | 'walk-right' | 'walk-left' | 'jump' | 'grab' | 'dance'
type FeedbackKind = 'correct' | 'wrong' | ''

// Character size constants (size prop = 90)
const CHAR_WIDTH  = 90
const CHAR_HEIGHT = 90 * 1.25  // 112.5
const CHAR_LEFT   = 40         // left: 40 in game area
const CHAR_BOTTOM = 26         // bottom: 26 in game area
const BANANA_RIGHT = 32        // right: 32 in game area
const BANANA_TOP_HIGH = 18     // top: 18 when banana is high

const LevelScene: React.FC<Props> = ({ island, level, onComplete, onBack }) => {
  const [mistakes, setMistakes]   = useState(0)
  const [feedback, setFeedback]   = useState<FeedbackKind>('')
  const [running, setRunning]     = useState(false)
  const [charAction, setCharAction] = useState<CharAction>('idle')
  const [charX, setCharX]         = useState(0)
  const [charY, setCharY]         = useState(0)   // negative = up
  const [flipChar, setFlipChar]   = useState(false)
  const [bananaEaten, setBananaEaten] = useState(false)
  const [showYum, setShowYum]         = useState(false)
  const startTime = useRef(Date.now())
  const feedbackTimer = useRef<ReturnType<typeof setTimeout>>()
  const gameAreaRef  = useRef<HTMLDivElement>(null)
  const [gameDims, setGameDims] = useState({ w: 320, h: 200 })

  // Banana is high only when the level explicitly says so
  const bananaHigh = level.banana_high ?? false

  // Sequence state
  const [program, setProgram]   = useState<string[]>([])
  const [available, setAvailable] = useState<string[]>(level.available_blocks ?? [])

  // Choice state
  const [choiceAnswered, setChoiceAnswered] = useState(false)
  const [choiceResult, setChoiceResult]     = useState<'correct' | 'wrong' | ''>('')

  // Debug state
  const [debugAnswered, setDebugAnswered] = useState(false)
  const [clickedDebugIdx, setClickedDebugIdx] = useState<number | null>(null)

  // Loop state
  const [selectedCount, setSelectedCount] = useState(1)

  // Measure game area
  useEffect(() => {
    const el = gameAreaRef.current
    if (!el) return
    const update = () => setGameDims({ w: el.clientWidth, h: el.clientHeight })
    update()
    const obs = new ResizeObserver(update)
    obs.observe(el)
    return () => obs.disconnect()
  }, [])

  // Reset when level changes
  useEffect(() => {
    setMistakes(0); setFeedback(''); setRunning(false)
    setCharAction('idle'); setCharX(0); setCharY(0); setFlipChar(false)
    setBananaEaten(false); setShowYum(false)
    setProgram([]); setAvailable(level.available_blocks ?? [])
    setChoiceAnswered(false); setChoiceResult('')
    setDebugAnswered(false); setClickedDebugIdx(null)
    setSelectedCount(1)
    startTime.current = Date.now()
  }, [level])

  const showFeedback = useCallback((kind: FeedbackKind, mistakes_: number = mistakes) => {
    setFeedback(kind)
    clearTimeout(feedbackTimer.current)
    if (kind === 'correct') {
      sounds.correct()
    } else {
      sounds.wrong()
      setMistakes(mistakes_ + 1)
    }
    feedbackTimer.current = setTimeout(() => setFeedback(''), kind === 'wrong' ? 1500 : 800)
  }, [mistakes])

  const runAnimation = useCallback((onDone: () => void) => {
    setRunning(true)
    setCharX(0); setCharY(0); setBananaEaten(false)

    // Strip explicit 'grab' from actions — we always end with our own eat sequence
    const actions = (level.character_actions ?? []).filter(a => a !== 'grab')

    // ── Step-size calculation ─────────────────────────────────────
    // Monkey center starts at: CHAR_LEFT + CHAR_WIDTH/2
    // Banana center at:        gameDims.w - BANANA_RIGHT - ~20 (half emoji)
    const charCenterStart = CHAR_LEFT + CHAR_WIDTH / 2
    const bananaCenterX   = gameDims.w - BANANA_RIGHT - 20
    const totalDistX      = Math.max(80, bananaCenterX - charCenterStart)
    const moveRightCount  = actions.filter(a => a === 'move_right').length
    const stepX           = moveRightCount > 0 ? totalDistX / moveRightCount : totalDistX

    // ── Jump height calculation ───────────────────────────────────
    // When banana is at top: BANANA_TOP_HIGH from top of game area.
    // Monkey head (top of SVG) at rest: gameDims.h - CHAR_BOTTOM - CHAR_HEIGHT from top.
    // translateY needed to bring head to banana top:
    //   charY = BANANA_TOP_HIGH - (gameDims.h - CHAR_BOTTOM - CHAR_HEIGHT)
    //         = BANANA_TOP_HIGH - gameDims.h + CHAR_BOTTOM + CHAR_HEIGHT
    const jumpY = bananaHigh
      ? BANANA_TOP_HIGH - gameDims.h + CHAR_BOTTOM + CHAR_HEIGHT
      : -45  // small decorative hop

    const STEP_MS = 550
    let step = 0
    let currentX = 0
    let jumped = false

    const next = () => {
      if (step >= actions.length) {
        // ── End sequence: grab → eat → yum → dance ──────────────
        setCharAction('grab')
        setTimeout(() => {
          setBananaEaten(true)
          setShowYum(true)
          sounds.win()
          setTimeout(() => setShowYum(false), 1400)
          setTimeout(() => {
            setCharY(0)
            setCharAction('dance')
            setRunning(false)
            onDone()
          }, 650)
        }, 480)
        return
      }

      const a = actions[step++]
      if (a === 'move_right') {
        setFlipChar(false); setCharAction('walk-right')
        currentX += stepX; setCharX(currentX)
      } else if (a === 'move_left') {
        setFlipChar(true); setCharAction('walk-left')
        currentX -= stepX; setCharX(currentX)
      } else if (a === 'jump') {
        setCharAction('jump')
        setCharY(jumpY)
        jumped = true
        // Bounce back down only for decorative hops (not when reaching high banana)
        if (!bananaHigh) setTimeout(() => setCharY(0), STEP_MS * 0.85)
      }
      setTimeout(next, STEP_MS)
    }

    if (actions.length === 0) {
      // No actions — just eat directly
      setTimeout(next, 100)
    } else {
      next()
    }
    void jumped  // used implicitly via closure
  }, [level, gameDims, bananaHigh])

  const finishLevel = useCallback(() => {
    const elapsed = (Date.now() - startTime.current) / 1000
    const thresh = level.star_thresholds
    const m = mistakes
    const stars = m <= thresh['3'] ? 3 : m <= thresh['2'] ? 2 : 1
    const xpBase = level.xp
    const xp = stars === 3 ? xpBase : stars === 2 ? Math.floor(xpBase * 2 / 3) : Math.floor(xpBase / 2)
    onComplete({ island_id: island.id, level_id: level.id, stars, xp, time: elapsed, mistakes: m })
  }, [island, level, mistakes, onComplete])

  // ── Sequence ────────────────────────────────────────────────────
  function addBlock(label: string) {
    setProgram(p => [...p, label])
    setAvailable(a => { const i = a.indexOf(label); return [...a.slice(0, i), ...a.slice(i + 1)] })
  }
  function removeBlock(idx: number) {
    const label = program[idx]
    setProgram(p => p.filter((_, i) => i !== idx))
    setAvailable(a => [...a, label])
  }
  function runSequence() {
    if (program.join(',') === (level.correct_sequence ?? []).join(',')) {
      showFeedback('correct', mistakes)
      setTimeout(() => runAnimation(finishLevel), 900)
    } else {
      showFeedback('wrong')
    }
  }

  // ── Choice ──────────────────────────────────────────────────────
  function chooseOption(opt: string) {
    if (choiceAnswered) return
    setChoiceAnswered(true)
    if (opt === level.correct_block) {
      setChoiceResult('correct')
      showFeedback('correct', mistakes)
      setTimeout(() => runAnimation(finishLevel), 900)
    } else {
      setChoiceResult('wrong')
      showFeedback('wrong')
    }
  }

  // ── Debug ───────────────────────────────────────────────────────
  function clickDebugBlock(idx: number) {
    if (debugAnswered) return
    setDebugAnswered(true)
    setClickedDebugIdx(idx)
    if (idx === level.wrong_index) {
      showFeedback('correct', mistakes)
      setTimeout(() => runAnimation(finishLevel), 900)
    } else {
      showFeedback('wrong')
    }
  }

  // ── Loop ────────────────────────────────────────────────────────
  function runLoop() {
    if (selectedCount === level.correct_count) {
      showFeedback('correct', mistakes)
      setTimeout(() => runAnimation(finishLevel), 900)
    } else {
      showFeedback('wrong')
    }
  }

  const islandColor = island.color

  // ── Island-specific scene colours ─────────────────────────────
  const ISLAND_BG: Record<number, string> = {
    1: 'linear-gradient(180deg, #87CEEB 0%, #b8dff0 55%, #7abb7a 100%)',
    2: 'linear-gradient(180deg, #1a3a1a 0%, #2a5a2a 65%, #3a6a2a 100%)',
    3: 'linear-gradient(180deg, #a0cce8 0%, #c0ddf0 55%, #d8eef8 100%)',
  }
  const GROUND_COLOR: Record<number, string>    = { 1: '#3a8a3a', 2: '#4a6a2a', 3: '#88b8d8' }
  const GROUND_SHADOW: Record<number, string>   = { 1: '#2a5a2a', 2: '#2a4a1a', 3: '#5a88a8' }
  const CLIFF_COLOR: Record<number, string>     = { 1: '#8B6040', 2: '#3a5a20', 3: '#4878b0' }
  const CLIFF_TOP_COLOR: Record<number, string> = { 1: '#3a8a3a', 2: '#2a6a2a', 3: '#a0d0f0' }
  const ROCK_COLOR: Record<number, string>      = { 1: '#7f8c8d', 2: '#5a7a4a', 3: '#8ab0d0' }

  const obstacle = level.obstacle ?? 'none'

  return (
    <div style={{
      display: 'flex', flexDirection: 'column', height: '100%',
      background: 'linear-gradient(180deg, #1A1A2E 0%, #1A2040 100%)',
      overflow: 'hidden',
    }}>
      {/* ── Header ───────────────────────────────────────────────── */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 10, padding: '7px 12px',
        background: 'rgba(0,0,0,0.4)', borderBottom: '2px solid rgba(100,100,200,0.3)',
        flexShrink: 0,
      }}>
        <button className="btn btn-panel btn-sm" onClick={() => { sounds.click(); onBack() }}>← Terug</button>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: '0.75rem', color: islandColor, fontFamily: 'var(--font-head)' }}>
            {ISLAND_ICONS[island.id]} {island.name}
          </div>
          <div style={{ fontFamily: 'var(--font-head)', fontSize: '1.05rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{level.title}</div>
        </div>
        <div style={{
          background: 'rgba(255,255,255,0.1)', borderRadius: 8,
          padding: '3px 10px', fontSize: '0.8rem', whiteSpace: 'nowrap',
        }}>
          {level.type === 'sequence' && '🔢 Volgorde'}
          {level.type === 'choice'   && '❓ Keuze'}
          {level.type === 'debug'    && '🐛 Fout zoeken'}
          {level.type === 'loop'     && '🔄 Herhaling'}
        </div>
      </div>

      {/* ── Instruction ─────────────────────────────────────────── */}
      <div style={{
        margin: '6px 10px 0',
        padding: '9px 14px',
        background: 'rgba(247,183,49,0.15)',
        border: '2px solid var(--primary)',
        borderRadius: 12,
        flexShrink: 0,
      }}>
        <p style={{ fontFamily: 'var(--font-head)', fontSize: 'clamp(0.9rem, 2.5vw, 1.15rem)', lineHeight: 1.35 }}>
          {level.instruction}
        </p>
      </div>

      {/* ── Game area ────────────────────────────────────────────── */}
      <div ref={gameAreaRef} style={{
        margin: '6px 10px 0',
        height: '22vh', minHeight: 130, maxHeight: 210, flexShrink: 0,
        background: ISLAND_BG[island.id] ?? 'rgba(30,50,80,0.6)',
        border: `2px solid ${island.color}66`,
        borderRadius: 14,
        position: 'relative', overflow: 'hidden',
      }}>

        {/* ── Clouds ─────────────────────────────────────────── */}
        {[18, 52, 78].map((x, i) => (
          <div key={i} style={{
            position: 'absolute', top: `${8 + i * 9}%`, left: `${x}%`,
            width: 55, height: 20,
            background: island.id === 3 ? 'rgba(255,255,255,0.55)' : 'rgba(255,255,255,0.18)',
            borderRadius: 20,
          }}/>
        ))}

        {/* ── Island-specific background decor ───────────────── */}
        {island.id === 1 && <>
          {/* Palm trunk */}
          <div style={{ position:'absolute', bottom: 28, left: 14, width: 8, height: 52, background: '#6B4226', borderRadius: '4px 4px 0 0' }}/>
          {/* Palm leaves */}
          <div style={{ position:'absolute', bottom: 76, left: -4,  width: 38, height: 18, background: '#2d8a2d', borderRadius: '50% 50% 20% 20%', transform: 'rotate(-8deg)' }}/>
          <div style={{ position:'absolute', bottom: 80, left:  8,  width: 30, height: 14, background: '#38a838', borderRadius: '50% 50% 20% 20%', transform: 'rotate(12deg)' }}/>
        </>}
        {island.id === 2 && <>
          {/* Left jungle tree */}
          <div style={{ position:'absolute', bottom: 28, left: 6,  width: 10, height: 80, background: '#3a2510', borderRadius: '5px 5px 0 0' }}/>
          <div style={{ position:'absolute', bottom: 96, left: -10, width: 48, height: 32, background: '#1a5a1a', borderRadius: '50%' }}/>
          {/* Smaller tree */}
          <div style={{ position:'absolute', bottom: 28, left: 28, width: 7,  height: 52, background: '#3a2510', borderRadius: '3px 3px 0 0' }}/>
          <div style={{ position:'absolute', bottom: 72, left: 14,  width: 34, height: 24, background: '#1a6a1a', borderRadius: '50%' }}/>
        </>}
        {island.id === 3 && <>
          {/* Snow mounds on edges */}
          <div style={{ position:'absolute', bottom: 25, left: -4,  width: 64, height: 20, background: '#ddeeff', borderRadius: '50% 50% 0 0', opacity: 0.85 }}/>
          <div style={{ position:'absolute', bottom: 25, left: 50,  width: 44, height: 14, background: '#cce4f4', borderRadius: '50% 50% 0 0', opacity: 0.7  }}/>
        </>}

        {/* ── Cliff (banana is high — monkey must jump up) ────── */}
        {bananaHigh && (
          <div style={{
            position: 'absolute', top: BANANA_TOP_HIGH + 26, bottom: 26, right: 0, width: 72,
            background: CLIFF_COLOR[island.id] ?? '#8B6040',
            borderRadius: '6px 6px 0 0',
          }}>
            <div style={{ position:'absolute', top:-9, left:-5, right:-5, height:11, background: CLIFF_TOP_COLOR[island.id] ?? '#3a8a3a', borderRadius:'4px 4px 0 0' }}/>
            {[10, 22, 34].map(t => (
              <div key={t} style={{ position:'absolute', top:t, left:8, right:8, height:2, background:'rgba(0,0,0,0.18)', borderRadius:1 }}/>
            ))}
          </div>
        )}

        {/* ── Stones (jump over a boulder mid-path) ──────────── */}
        {obstacle === 'stone' && (
          <div style={{ position:'absolute', bottom:29, left:'38%' }}>
            <div style={{ width:40, height:28, background: ROCK_COLOR[island.id] ?? '#7f8c8d', borderRadius:'50% 50% 40% 40%', boxShadow:'inset 0 -4px 0 rgba(0,0,0,0.25)', position:'relative' }}>
              <div style={{ position:'absolute', top:5, left:8, width:11, height:7, background:'rgba(255,255,255,0.22)', borderRadius:'50%' }}/>
            </div>
            <div style={{ position:'absolute', bottom:0, right:-22, width:24, height:16, background: ROCK_COLOR[island.id] ?? '#7f8c8d', borderRadius:'50% 50% 40% 40%', filter:'brightness(0.82)' }}/>
          </div>
        )}

        {/* ── River (jump far over water gap) ─────────────────── */}
        {obstacle === 'river' && <>
          {/* Water body */}
          <div style={{ position:'absolute', bottom:0, left:'30%', width:68, height:29, background:'linear-gradient(180deg,#4a9fd4 0%,#2a6fa0 100%)', borderRadius:'0 0 4px 4px', overflow:'hidden' }}>
            {/* Ripples */}
            <div style={{ position:'absolute', top:6,  left:6,  right:6,  height:3, background:'rgba(255,255,255,0.28)', borderRadius:2 }}/>
            <div style={{ position:'absolute', top:14, left:12, right:12, height:2, background:'rgba(255,255,255,0.18)', borderRadius:2 }}/>
            <div style={{ position:'absolute', top:21, left:8,  right:8,  height:2, background:'rgba(255,255,255,0.12)', borderRadius:2 }}/>
          </div>
          {/* Left bank */}
          <div style={{ position:'absolute', bottom:26, left:'30%', width:6, height:8, background: GROUND_COLOR[island.id] ?? '#4a7a3a', borderRadius:'2px 0 0 2px' }}/>
          {/* Right bank */}
          <div style={{ position:'absolute', bottom:26, left:'calc(30% + 62px)', width:6, height:8, background: GROUND_COLOR[island.id] ?? '#4a7a3a', borderRadius:'0 2px 2px 0' }}/>
        </>}

        {/* ── Ice mound (climb/jump over iceberg) ─────────────── */}
        {obstacle === 'ice_mound' && (
          <div style={{ position:'absolute', bottom:29, left:'36%' }}>
            {/* Main mound */}
            <div style={{ width:54, height:40, background:'linear-gradient(135deg,#c8e8f8 0%,#6090c0 100%)', borderRadius:'50% 50% 20% 20%', position:'relative', boxShadow:'0 -2px 0 rgba(255,255,255,0.6)' }}>
              <div style={{ position:'absolute', top:6, left:10, width:14, height:9, background:'rgba(255,255,255,0.45)', borderRadius:'50%' }}/>
              <div style={{ position:'absolute', top:4, left:30, width:7, height:5, background:'rgba(255,255,255,0.3)', borderRadius:'50%' }}/>
            </div>
            {/* Smaller chunk beside it */}
            <div style={{ position:'absolute', bottom:0, right:-26, width:28, height:18, background:'linear-gradient(135deg,#b8d8f0 0%,#5080b0 100%)', borderRadius:'50% 50% 20% 20%', filter:'brightness(0.9)' }}/>
          </div>
        )}

        {/* ── Ground line (split around river gap) ────────────── */}
        {obstacle === 'river' ? <>
          <div style={{ position:'absolute', bottom:26, left:14, width:'30%', height:4, background: GROUND_COLOR[island.id] ?? '#4a7a3a', borderRadius:2, boxShadow:`0 2px 0 ${GROUND_SHADOW[island.id] ?? '#2a5a2a'}` }}/>
          <div style={{ position:'absolute', bottom:26, left:'calc(30% + 68px)', right: bananaHigh ? 72 : 14, height:4, background: GROUND_COLOR[island.id] ?? '#4a7a3a', borderRadius:2, boxShadow:`0 2px 0 ${GROUND_SHADOW[island.id] ?? '#2a5a2a'}` }}/>
        </> : (
          <div style={{ position:'absolute', bottom:26, left:14, right: bananaHigh ? 72 : 14, height:4, background: GROUND_COLOR[island.id] ?? '#4a7a3a', borderRadius:2, boxShadow:`0 2px 0 ${GROUND_SHADOW[island.id] ?? '#2a5a2a'}` }}/>
        )}

        {/* ── Target item ─────────────────────────────────────── */}
        <div style={{
          position: 'absolute',
          right: BANANA_RIGHT,
          ...(bananaHigh ? { top: BANANA_TOP_HIGH } : { bottom: 30 }),
          fontSize: 'clamp(2rem, 5vw, 3rem)',
          filter: 'drop-shadow(0 2px 8px rgba(0,0,0,0.5))',
          transition: 'transform 0.3s ease, opacity 0.3s ease',
          transform: bananaEaten ? 'scale(0) rotate(180deg)' : 'scale(1)',
          opacity: bananaEaten ? 0 : 1,
          userSelect: 'none',
          zIndex: 2,
        }}>
          {ISLAND_ICONS[island.id] ?? '🍌'}
        </div>

        {/* ── "Lekker!" bubble ─────────────────────────────────── */}
        {showYum && (
          <div style={{
            position: 'absolute',
            right: BANANA_RIGHT + 10,
            ...(bananaHigh ? { top: BANANA_TOP_HIGH - 32 } : { bottom: 72 }),
            fontFamily: 'var(--font-head)', fontSize: '1.4rem',
            color: '#FFD700', textShadow: '0 2px 8px rgba(0,0,0,0.6)',
            animation: 'pop-in 0.2s ease', pointerEvents: 'none', zIndex: 10,
          }}>
            😋 Lekker!
          </div>
        )}

        {/* ── Character ────────────────────────────────────────── */}
        <div style={{
          position: 'absolute', bottom: CHAR_BOTTOM, left: CHAR_LEFT,
          transition: 'transform 0.5s ease',
          transform: `translateX(${charX}px) translateY(${charY}px)`,
          zIndex: 3,
        }}>
          <Character action={charAction} flipX={flipChar} size={CHAR_WIDTH}/>
        </div>
      </div>

      {/* ── Level UI (scrollable, can't overlap game area) ────────── */}
      <div className="scrollable" style={{
        flex: 1, margin: '0 10px', padding: '10px 0',
        minHeight: 0,
      }}>
        {level.type === 'sequence' && (
          <SequenceUI
            program={program} available={available} disabled={running}
            onAdd={addBlock} onRemove={removeBlock}
          />
        )}
        {level.type === 'choice' && (
          <ChoiceUI
            prefix={level.program_prefix ?? []}
            suffix={level.program_suffix ?? []}
            options={level.options ?? []}
            answered={choiceAnswered}
            choiceResult={choiceResult}
            correctBlock={level.correct_block ?? ''}
            disabled={running}
            onChoose={chooseOption}
          />
        )}
        {level.type === 'debug' && (
          <DebugUI
            blocks={level.program ?? []}
            wrongIndex={level.wrong_index ?? 0}
            answered={debugAnswered}
            clickedIdx={clickedDebugIdx}
            disabled={running}
            onClickBlock={clickDebugBlock}
          />
        )}
        {level.type === 'loop' && (
          <LoopUI
            baseBlock={level.base_block ?? ''}
            selectedCount={selectedCount}
            disabled={running}
            onSelect={setSelectedCount}
          />
        )}
      </div>

      {/* ── Run button (sequence + loop only) ─────────────────────── */}
      {(level.type === 'sequence' || level.type === 'loop') && (
        <div style={{
          padding: '8px 10px 12px',
          flexShrink: 0,
          borderTop: '2px solid rgba(100,100,200,0.2)',
        }}>
          <button className="btn btn-green btn-lg" style={{ width: '100%' }}
                  disabled={running || (level.type === 'sequence' && program.length === 0)}
                  onClick={level.type === 'sequence' ? runSequence : runLoop}>
            ▶ Uitvoeren!
          </button>
        </div>
      )}

      {/* ── Feedback banner ─────────────────────────────────────── */}
      {feedback && (
        <div className={`feedback-banner feedback-${feedback}`}>
          {feedback === 'correct' ? 'Goed zo! 🎉' : 'Fout! Probeer opnieuw 💪'}
        </div>
      )}
    </div>
  )
}

// ── Sub-components ────────────────────────────────────────────────────────

const SequenceUI: React.FC<{
  program: string[]; available: string[]; disabled: boolean
  onAdd: (l: string) => void; onRemove: (i: number) => void
}> = ({ program, available, disabled, onAdd, onRemove }) => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
    {/* Program zone */}
    <div style={{
      background: 'rgba(30,60,100,0.7)', border: '2px solid rgba(80,140,220,0.5)',
      borderRadius: 12, padding: '12px 14px', minHeight: 90,
    }}>
      <div style={{ fontSize: '0.8rem', color: 'rgba(150,200,255,0.8)', marginBottom: 8,
                    fontFamily: 'var(--font-head)' }}>
        Jouw programma — klik een blok om te verwijderen:
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
        {program.length === 0 && (
          <span style={{ color: 'rgba(150,160,180,0.6)', fontSize: '0.9rem', alignSelf: 'center' }}>
            Klik hieronder op een blok om het toe te voegen...
          </span>
        )}
        {program.map((label, i) => (
          <button key={i} className="code-block" disabled={disabled}
                  style={{ background: BLOCK_COLORS[(i + 3) % BLOCK_COLORS.length], color: '#1A1A2E' }}
                  onClick={() => !disabled && onRemove(i)}>
            {label} ✕
          </button>
        ))}
      </div>
    </div>

    {/* Available blocks */}
    <div>
      <div style={{ fontSize: '0.8rem', color: 'rgba(200,200,220,0.7)', marginBottom: 8,
                    fontFamily: 'var(--font-head)' }}>
        Beschikbare blokken:
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
        {available.map((label, i) => (
          <button key={i} className="code-block" disabled={disabled}
                  style={{ background: BLOCK_COLORS[i % BLOCK_COLORS.length], color: '#1A1A2E' }}
                  onClick={() => !disabled && onAdd(label)}>
            {label}
          </button>
        ))}
      </div>
    </div>
  </div>
)

const ChoiceUI: React.FC<{
  prefix: string[]; suffix: string[]; options: string[]
  answered: boolean; choiceResult: string; correctBlock: string; disabled: boolean
  onChoose: (opt: string) => void
}> = ({ prefix, suffix, options, answered, choiceResult, correctBlock, disabled, onChoose }) => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
    {/* Partial program display */}
    <div style={{
      background: 'rgba(30,60,100,0.6)', border: '2px solid rgba(80,140,220,0.4)',
      borderRadius: 12, padding: '12px 14px',
    }}>
      <div style={{ fontSize: '0.8rem', color: 'rgba(150,200,255,0.8)', marginBottom: 8,
                    fontFamily: 'var(--font-head)' }}>
        Het programma — welk blok past op de lege plek?
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, alignItems: 'center' }}>
        {prefix.map((label, i) => (
          <span key={i} className="code-block disabled"
                style={{ background: BLOCK_COLORS[i % BLOCK_COLORS.length], color: '#1A1A2E' }}>
            {label}
          </span>
        ))}
        {/* Blank slot */}
        <span style={{
          display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
          minWidth: 100, height: 56, borderRadius: 12,
          border: '3px dashed var(--primary)',
          background: answered ? 'rgba(32,191,107,0.2)' : 'rgba(247,183,49,0.1)',
          fontFamily: 'var(--font-head)', fontSize: '1.4rem', color: 'var(--primary)',
          transition: 'background 0.3s',
        }}>
          {answered ? correctBlock : '?'}
        </span>
        {suffix.map((label, i) => (
          <span key={i} className="code-block disabled"
                style={{ background: BLOCK_COLORS[(i + 2) % BLOCK_COLORS.length], color: '#1A1A2E' }}>
            {label}
          </span>
        ))}
      </div>
    </div>

    {/* Options */}
    <div>
      <div style={{ fontSize: '0.8rem', color: 'rgba(200,200,220,0.7)', marginBottom: 10,
                    fontFamily: 'var(--font-head)' }}>
        Kies het juiste blok:
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
        {options.map((opt, i) => {
          let bg = BLOCK_COLORS[i % BLOCK_COLORS.length]
          if (answered) {
            if (opt === correctBlock) bg = '#20BF6B'
            else if (i === options.indexOf(opt) && choiceResult === 'wrong') bg = '#FC5C65'
          }
          return (
            <button key={i} className="code-block"
                    disabled={disabled || answered}
                    style={{ background: bg, color: '#1A1A2E', width: '100%', justifyContent: 'center' }}
                    onClick={() => onChoose(opt)}>
              {opt}
            </button>
          )
        })}
      </div>
    </div>
  </div>
)

const DebugUI: React.FC<{
  blocks: string[]; wrongIndex: number; answered: boolean
  clickedIdx: number | null; disabled: boolean
  onClickBlock: (i: number) => void
}> = ({ blocks, wrongIndex, answered, clickedIdx, disabled, onClickBlock }) => (
  <div>
    <div style={{
      background: 'rgba(252,92,101,0.1)', border: '2px solid rgba(252,92,101,0.4)',
      borderRadius: 12, padding: '12px 14px', marginBottom: 12,
    }}>
      <p style={{ fontFamily: 'var(--font-head)', fontSize: '0.95rem', color: 'rgba(255,180,180,0.9)' }}>
        🐛 Er zit een fout in dit programma! Klik op het foute blok.
      </p>
    </div>
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
      {blocks.map((label, i) => {
        let bg = BLOCK_COLORS[i % BLOCK_COLORS.length]
        let extra = ''
        if (answered) {
          if (i === wrongIndex)  { bg = '#FC5C65'; extra = ' ← FOUT' }
          else { bg = '#20BF6B' }
        } else if (clickedIdx === i && clickedIdx !== wrongIndex) {
          bg = '#FC5C65'
        }
        return (
          <button key={i} className="code-block"
                  disabled={disabled || answered}
                  style={{ background: bg, color: '#1A1A2E', transition: 'background 0.3s' }}
                  onClick={() => !answered && onClickBlock(i)}>
            {label}{extra}
          </button>
        )
      })}
    </div>
  </div>
)

const LoopUI: React.FC<{
  baseBlock: string; selectedCount: number; disabled: boolean
  onSelect: (n: number) => void
}> = ({ baseBlock, selectedCount, disabled, onSelect }) => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
    {/* Loop display */}
    <div style={{
      background: 'rgba(247,183,49,0.1)', border: '2px solid rgba(247,183,49,0.4)',
      borderRadius: 12, padding: '14px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
        <span style={{ fontFamily: 'var(--font-head)', fontSize: '1.3rem', color: 'var(--primary)' }}>
          HERHAAL
        </span>
        <span style={{
          fontFamily: 'var(--font-head)', fontSize: '1.6rem', color: 'var(--secondary)',
          background: 'rgba(32,191,107,0.2)', borderRadius: 8, padding: '0 12px',
        }}>
          {selectedCount}×
        </span>
        <span style={{ fontFamily: 'var(--font-head)', fontSize: '1rem', color: 'rgba(255,255,255,0.6)' }}>
          keer:
        </span>
        <span className="code-block disabled"
              style={{ background: BLOCK_COLORS[2], color: '#1A1A2E' }}>
          {baseBlock}
        </span>
      </div>
    </div>

    {/* Count selector */}
    <div>
      <div style={{ fontSize: '0.85rem', color: 'rgba(200,200,220,0.7)', marginBottom: 10,
                    fontFamily: 'var(--font-head)' }}>
        Kies het aantal keer:
      </div>
      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
        {[1, 2, 3, 4, 5].map(n => (
          <button key={n} className="btn" disabled={disabled}
                  style={{
                    width: 70, height: 70,
                    background: n === selectedCount ? 'var(--primary)' : 'var(--secondary)',
                    color: 'var(--text-dark)',
                    fontFamily: 'var(--font-head)', fontSize: '1.6rem',
                    border: n === selectedCount ? '3px solid white' : 'none',
                  }}
                  onClick={() => { sounds.click(); onSelect(n) }}>
            {n}
          </button>
        ))}
      </div>
    </div>
  </div>
)

export default LevelScene
