import { Progress, LevelResult, LevelsData } from './types'
import { XP_PER_LEVEL, MAX_PLAYER_LEVEL } from './config'

const KEY = 'codeaap_progress'

const DEFAULT: Progress = {
  player_name: '',
  player_xp: 0,
  player_level: 1,
  levels_completed: {},
  badges_earned: [],
  islands_unlocked: [1],
}

export function loadProgress(): Progress {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return { ...DEFAULT }
    const parsed = JSON.parse(raw) as Progress
    // fill missing keys
    return { ...DEFAULT, ...parsed }
  } catch {
    return { ...DEFAULT }
  }
}

export function saveProgress(p: Progress): void {
  localStorage.setItem(KEY, JSON.stringify(p))
}

export function completeLevel(
  progress: Progress,
  result: LevelResult,
  levelsData: LevelsData,
): { updated: Progress; newBadges: string[] } {
  const p = { ...progress }
  const key = `${result.island_id}-${result.level_id}`
  const prev = p.levels_completed[key]
  const prevStars = prev?.stars ?? 0

  if (result.stars > prevStars) {
    const bonusXp = prevStars === 0 ? result.xp : Math.max(0, result.xp - (prev?.xp_earned ?? 0))
    p.player_xp += bonusXp
    p.levels_completed = {
      ...p.levels_completed,
      [key]: { stars: result.stars, xp_earned: result.xp },
    }
  }

  p.player_level = Math.min(MAX_PLAYER_LEVEL, 1 + Math.floor(p.player_xp / XP_PER_LEVEL))

  // Unlock next island
  const island = levelsData.islands.find(i => i.id === result.island_id)
  if (island) {
    const allKeys = island.levels.map(lv => `${island.id}-${lv.id}`)
    const allDone = allKeys.every(k => p.levels_completed[k])
    if (allDone) {
      const nextId = result.island_id + 1
      if (!p.islands_unlocked.includes(nextId)) {
        p.islands_unlocked = [...p.islands_unlocked, nextId]
      }
    }
  }

  const newBadges = checkBadges(p, result, levelsData)
  p.badges_earned = [...new Set([...p.badges_earned, ...newBadges])]

  saveProgress(p)
  return { updated: p, newBadges }
}

function checkBadges(p: Progress, result: LevelResult, levelsData: LevelsData): string[] {
  const earned = new Set(p.badges_earned)
  const newBadges: string[] = []
  const earn = (id: string) => { if (!earned.has(id)) { earned.add(id); newBadges.push(id) } }

  if (Object.keys(p.levels_completed).length >= 1) earn('first_win')
  if (result.stars === 3) earn('no_mistakes')

  for (const isl of levelsData.islands) {
    const allKeys = isl.levels.map(lv => `${isl.id}-${lv.id}`)
    if (allKeys.every(k => p.levels_completed[k])) earn(`island_${isl.id}`)
  }

  if (p.islands_unlocked.includes(2)) earn('explorer')

  const allCompleted = Object.values(p.levels_completed)
  if (allCompleted.length >= 3 && allCompleted.slice(-3).every(lv => lv.stars === 3)) earn('streak_3')

  const debugDone = levelsData.islands.flatMap(i => i.levels)
    .filter(lv => lv.type === 'debug' && p.levels_completed[`${levelsData.islands.find(i => i.levels.includes(lv))!.id}-${lv.id}`])
    .length
  if (debugDone >= 5) earn('bug_finder')

  const loopDone = levelsData.islands.some(isl =>
    isl.levels.some(lv => lv.type === 'loop' && p.levels_completed[`${isl.id}-${lv.id}`])
  )
  if (loopDone) earn('loop_master')

  const ifDone = levelsData.islands.some(isl =>
    isl.levels.some(lv => lv.type === 'if_else' && p.levels_completed[`${isl.id}-${lv.id}`])
  )
  if (ifDone) earn('if_master')

  const varDone = levelsData.islands.some(isl =>
    isl.levels.some(lv => lv.type === 'variable' && p.levels_completed[`${isl.id}-${lv.id}`])
  )
  if (varDone) earn('variable_master')

  const funcDone = levelsData.islands.some(isl =>
    isl.levels.some(lv => lv.type === 'function' && p.levels_completed[`${isl.id}-${lv.id}`])
  )
  if (funcDone) earn('function_master')

  const nestedDone = levelsData.islands.some(isl =>
    isl.levels.some(lv => lv.type === 'nested_loop' && p.levels_completed[`${isl.id}-${lv.id}`])
  )
  if (nestedDone) earn('nested_master')

  if ([...earned].length >= 5) earn('collector')

  const allIslandIds = levelsData.islands.map(i => i.id)
  if (allIslandIds.every(id => p.islands_unlocked.includes(id))) {
    const allKeys = levelsData.islands.flatMap(i => i.levels.map(lv => `${i.id}-${lv.id}`))
    if (allKeys.every(k => p.levels_completed[k])) earn('champion')
  }

  if (result.time < 30) earn('speed_star')

  return newBadges
}
