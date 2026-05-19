export interface Level {
  id: number
  title: string
  type: 'sequence' | 'choice' | 'debug' | 'loop'
  instruction: string
  available_blocks?: string[]
  correct_sequence?: string[]
  program_prefix?: string[]
  program_suffix?: string[]
  correct_block?: string
  options?: string[]
  program?: string[]
  wrong_index?: number
  base_block?: string
  correct_count?: number
  character_actions?: string[]
  max_stars: number
  star_thresholds: { '3': number; '2': number; '1': number }
  xp: number
}

export interface Island {
  id: number
  name: string
  color: string
  position: [number, number]
  unlocked: boolean
  levels: Level[]
}

export interface LevelsData {
  islands: Island[]
}

export interface LevelProgress {
  stars: number
  xp_earned: number
}

export interface Progress {
  player_name: string
  player_xp: number
  player_level: number
  levels_completed: Record<string, LevelProgress>
  badges_earned: string[]
  islands_unlocked: number[]
}

export interface LevelResult {
  island_id: number
  level_id: number
  stars: number
  xp: number
  time: number
  mistakes: number
}

export type SceneName = 'menu' | 'world_map' | 'level' | 'reward' | 'achievements'
