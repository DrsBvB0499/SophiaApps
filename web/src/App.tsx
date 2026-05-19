import React, { useState, useCallback } from 'react'
import { Island, Level, LevelResult, Progress, SceneName } from './types'
import { loadProgress, saveProgress, completeLevel } from './save'
import levelsJson from './data/levels.json'
import type { LevelsData } from './types'

import MenuScene        from './scenes/MenuScene'
import WorldMapScene    from './scenes/WorldMapScene'
import LevelScene       from './scenes/LevelScene'
import RewardScene      from './scenes/RewardScene'
import AchievementsScene from './scenes/AchievementsScene'

const levelsData = levelsJson as unknown as LevelsData

const App: React.FC = () => {
  const [scene, setScene]         = useState<SceneName>('menu')
  const [progress, setProgress]   = useState<Progress>(loadProgress)
  const [selIsland, setSelIsland] = useState<Island | null>(null)
  const [selLevel,  setSelLevel]  = useState<Level  | null>(null)
  const [result,    setResult]    = useState<LevelResult | null>(null)
  const [newBadges, setNewBadges] = useState<string[]>([])
  const [prevXp,    setPrevXp]    = useState(0)
  const [prevLevel, setPrevLevel] = useState(1)

  const updateName = useCallback((name: string) => {
    const p = { ...progress, player_name: name }
    setProgress(p)
    saveProgress(p)
  }, [progress])

  const selectLevel = useCallback((island: Island, level: Level) => {
    setSelIsland(island)
    setSelLevel(level)
    setScene('level')
  }, [])

  const handleComplete = useCallback((res: LevelResult) => {
    setResult(res)
    setPrevXp(progress.player_xp)
    setPrevLevel(progress.player_level)
    const { updated, newBadges: badges } = completeLevel(progress, res, levelsData)
    setProgress(updated)
    setNewBadges(badges)
    setScene('reward')
  }, [progress])

  const goToNextLevel = useCallback(() => {
    if (!selIsland || !selLevel) { setScene('world_map'); return }
    const island = levelsData.islands.find(i => i.id === selIsland.id)
    if (!island) { setScene('world_map'); return }
    const idx = island.levels.findIndex(lv => lv.id === selLevel.id)
    const next = island.levels[idx + 1]
    if (next) { setSelLevel(next); setScene('level') }
    else setScene('world_map')
  }, [selIsland, selLevel])

  const nextLevelForReward = useCallback((): Level | null => {
    if (!selIsland || !selLevel) return null
    const island = levelsData.islands.find(i => i.id === selIsland.id)
    if (!island) return null
    const idx = island.levels.findIndex(lv => lv.id === selLevel.id)
    return island.levels[idx + 1] ?? null
  }, [selIsland, selLevel])

  return (
    <>
      {scene === 'menu' && (
        <MenuScene
          progress={progress}
          onUpdateName={updateName}
          onPlay={() => setScene('world_map')}
          onBadges={() => setScene('achievements')}
        />
      )}
      {scene === 'world_map' && (
        <WorldMapScene
          progress={progress}
          levelsData={levelsData}
          onSelectLevel={selectLevel}
          onMenu={() => setScene('menu')}
          onBadges={() => setScene('achievements')}
        />
      )}
      {scene === 'level' && selIsland && selLevel && (
        <LevelScene
          key={`${selIsland.id}-${selLevel.id}`}
          island={selIsland}
          level={selLevel}
          onComplete={handleComplete}
          onBack={() => setScene('world_map')}
        />
      )}
      {scene === 'reward' && result && selIsland && selLevel && (
        <RewardScene
          result={result}
          newBadges={newBadges}
          prevXp={prevXp}
          prevLevel={prevLevel}
          progress={progress}
          island={selIsland}
          level={selLevel}
          nextLevel={nextLevelForReward()}
          onNext={goToNextLevel}
          onMap={() => setScene('world_map')}
        />
      )}
      {scene === 'achievements' && (
        <AchievementsScene
          progress={progress}
          onBack={() => setScene(progress.player_name ? 'menu' : 'menu')}
        />
      )}
    </>
  )
}

export default App
