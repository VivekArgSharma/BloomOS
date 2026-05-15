export type Garden = {
  id: string
  name: string
  location_type: string
  city?: string | null
  health_score: number
  plant_count: number
}

export type CareProfile = {
  water_interval_days: number
  light: string
  humidity: string
  fertilizer: string
  soil: string
  notes: string[]
}

export type Plant = {
  id: string
  garden_id: string
  common_name: string
  species_name: string
  source: 'catalog' | 'image'
  care_profile: CareProfile
  current_health_score: number
  recovery_mode: boolean
}

export type CatalogItem = {
  id: string
  common_name: string
  species_name: string
  difficulty: 'easy' | 'moderate' | 'advanced'
  tags: string[]
  care_profile: CareProfile
}

export type DailyTask = {
  id: string
  title: string
  description: string
  category: 'water' | 'monitor' | 'feed' | 'sunlight' | 'photo'
  completed: boolean
}

export type DailyPlan = {
  id: string
  plant_id: string
  tasks: DailyTask[]
  weather_snapshot: {
    summary: string
    temperature_c: number
    humidity: number
    rain_chance: number
  }
}

export type DailyLog = {
  id: string
  photo_url: string
  observations: string
  analysis: {
    health_score: number
    visible_issues: string[]
    soil_moisture: string
    recommended_action: string
    diary_entry: string
  }
  created_at: string
}

export type PlantDetails = {
  plant: Plant
  latest_log?: DailyLog | null
  plan?: DailyPlan | null
}

export type Weather = {
  city: string
  summary: string
  temperature_c: number
  humidity: number
  rain_chance: number
}

export type ChatResponse = {
  answer: string
  grounding: string[]
}

export type HealthPoint = {
  label: string
  score: number
}

export type CompletionPoint = {
  label: string
  completed: number
  total: number
  rate: number
}

export type IssueCount = {
  issue: string
  count: number
}

export type PlantAnalytics = {
  plant_id: string
  current_health: number
  average_health: number
  health_delta: number
  streak_days: number
  task_completion_rate: number
  watering_consistency: number
  issue_breakdown: IssueCount[]
  health_history: HealthPoint[]
  completion_history: CompletionPoint[]
  insight: string
}

export type GardenPlantSnapshot = {
  plant_id: string
  common_name: string
  health_score: number
  completion_rate: number
  recovery_mode: boolean
}

export type GardenAnalytics = {
  garden_id: string
  overall_health: number
  average_completion_rate: number
  plants_in_recovery: number
  healthiest_plant?: string | null
  needs_attention_plant?: string | null
  issue_breakdown: IssueCount[]
  health_history: HealthPoint[]
  plant_snapshots: GardenPlantSnapshot[]
  recommended_focus: string
}

export type Badge = {
  id: string
  name: string
  description: string
  icon: string
  unlocked: boolean
}

export type UserBadges = {
  badges: Badge[]
  total_unlocked: number
  total_available: number
}

export type UserStats = {
  garden_count: number
  plant_count: number
  current_streak: number
  longest_streak: number
  total_tasks_completed: number
  total_photos_uploaded: number
  recovery_mode_exits: number
  chat_questions_asked: number
  weather_decisions: number
  plants_at_health_90_plus: number
}

export type CompatibilityCheck = {
  compatible: boolean
  confidence: number
  issues: string[]
  recommendations: string[]
  light_compatibility: Record<string, any>
  humidity_compatibility: Record<string, any>
}

export type CommunityProfile = {
  id: string
  username: string
  display_name: string
  avatar_url?: string | null
  bio?: string | null
}

export type CommunityPost = {
  id: string
  author: CommunityProfile
  body: string
  image_url?: string | null
  like_count: number
  comment_count: number
  viewer_has_liked: boolean
  created_at: string
  updated_at?: string | null
  is_owner: boolean
}

export type CommunityComment = {
  id: string
  post_id: string
  author: CommunityProfile
  body: string
  created_at: string
  updated_at?: string | null
  is_owner: boolean
}

export type CommunityFeed = {
  posts: CommunityPost[]
  next_offset?: number | null
}

export type CommunityLikeResponse = {
  post_id: string
  like_count: number
  viewer_has_liked: boolean
}

export type CommunityProfilePage = {
  profile: CommunityProfile
  posts: CommunityPost[]
  next_offset?: number | null
}
