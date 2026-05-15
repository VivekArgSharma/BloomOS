import axios from 'axios'

import type { CatalogItem, ChatResponse, CompatibilityCheck, CommunityComment, CommunityFeed, CommunityLikeResponse, CommunityPost, CommunityProfile, CommunityProfilePage, DailyLog, DailyPlan, Garden, GardenAnalytics, Plant, PlantAnalytics, PlantDetails, UserBadges, UserStats, Weather } from '../types'
import { supabase } from './supabase'

const api = axios.create({
  baseURL: (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8001/api').replace(/\/$/, '') + '/',
})

api.interceptors.request.use(async (config) => {
  let token = 'mock-token'
  if (supabase) {
    const { data } = await supabase.auth.getSession()
    if (data.session?.access_token) {
      token = data.session.access_token
    }
  }
  config.headers.Authorization = `Bearer ${token}`
  return config
})

export async function fetchGardens() {
  const { data } = await api.get<Garden[]>('gardens')
  return data
}

export async function createGarden(payload: { name: string; location_type: string; city?: string }) {
  const { data } = await api.post<Garden>('gardens', payload)
  return data
}

export async function fetchGardenPlants(gardenId: string) {
  const { data } = await api.get<Plant[]>(`/gardens/${gardenId}/plants`)
  return data
}

export async function fetchGardenAnalytics(gardenId: string) {
  const { data } = await api.get<GardenAnalytics>(`gardens/${gardenId}/analytics`)
  return data
}

export async function fetchCatalog() {
  const { data } = await api.get<CatalogItem[]>('catalog')
  return data
}

export async function identifyPlant(payload: { file?: File | null; searchHint?: string }) {
  const form = new FormData()
  if (payload.searchHint) form.append('search_hint', payload.searchHint)
  if (payload.file) form.append('image', payload.file)
  const { data } = await api.post('plants/identify', form)
  return data as {
    matched_catalog: boolean
    confidence: number
    rationale: string
    plant: CatalogItem
  }
}

export async function createPlant(payload: {
  garden_id: string
  common_name: string
  species_name: string
  source: 'catalog' | 'image'
  care_profile: CatalogItem['care_profile']
}) {
  const { data } = await api.post<Plant>('plants', payload)
  return data
}

export async function fetchPlantDetails(plantId: string) {
  const { data } = await api.get<PlantDetails>(`plants/${plantId}`)
  return data
}

export async function fetchPlantLogs(plantId: string) {
  const { data } = await api.get<DailyLog[]>(`plants/${plantId}/logs`)
  return data
}

export async function fetchPlantTasks(plantId: string) {
  const { data } = await api.get<DailyPlan>(`plants/${plantId}/tasks`)
  return data
}

export async function fetchPlantAnalytics(plantId: string) {
  const { data } = await api.get<PlantAnalytics>(`plants/${plantId}/analytics`)
  return data
}

export async function completeTask(plantId: string, taskId: string) {
  const { data } = await api.post(`plants/${plantId}/tasks/${taskId}`)
  return data
}

export async function analyzePlant(plantId: string, payload: { file: File; observations: string }) {
  const form = new FormData()
  form.append('observations', payload.observations)
  form.append('image', payload.file)
  const { data } = await api.post<DailyLog>(`plants/${plantId}/analyze`, form)
  return data
}

export async function askPlantChat(plantId: string, question: string) {
  const { data } = await api.post<ChatResponse>('chat', { plant_id: plantId, question })
  return data
}

export async function fetchWeather(city?: string) {
  const { data } = await api.get<Weather>('weather', { params: city ? { city } : {} })
  return data
}

export async function fetchUserBadges() {
  const { data } = await api.get<UserBadges>('badges')
  return data
}

export async function fetchUserStats() {
  const { data } = await api.get<UserStats>('stats')
  return data
}

export async function fetchPlantCompatibility(plantId: string, locationType: string) {
  const { data } = await api.get<CompatibilityCheck>(`plants/${plantId}/compatibility`, {
    params: { location_type: locationType },
  })
  return data
}

export type AnalysisPreview = {
  health_score: number
  summary: string
  issues: string[]
  is_urgent: boolean
}

export async function previewPlantAnalysis(plantId: string, file: File, observations: string) {
  const form = new FormData()
  form.append('image', file)
  if (observations) form.append('observations', observations)
  const { data } = await api.post<AnalysisPreview>(`plants/${plantId}/preview-analysis`, form)
  return data
}

export async function fetchCommunityFeed(offset = 0, limit = 20) {
  const { data } = await api.get<CommunityFeed>('community/feed', { params: { offset, limit } })
  return data
}

export async function createCommunityPost(payload: { body: string; image_url?: string }) {
  const { data } = await api.post<CommunityPost>('community/posts', payload)
  return data
}

export async function deleteCommunityPost(postId: string) {
  await api.delete(`community/posts/${postId}`)
}

export async function updateCommunityPost(postId: string, payload: { body: string; image_url?: string }) {
  const { data } = await api.patch<CommunityPost>(`community/posts/${postId}`, payload)
  return data
}

export async function fetchCommunityComments(postId: string) {
  const { data } = await api.get<CommunityComment[]>(`community/posts/${postId}/comments`)
  return data
}

export async function createCommunityComment(postId: string, payload: { body: string }) {
  const { data } = await api.post<CommunityComment>(`community/posts/${postId}/comments`, payload)
  return data
}

export async function updateCommunityComment(commentId: string, payload: { body: string }) {
  const { data } = await api.patch<CommunityComment>(`community/comments/${commentId}`, payload)
  return data
}

export async function deleteCommunityComment(commentId: string) {
  await api.delete(`community/comments/${commentId}`)
}

export async function likeCommunityPost(postId: string) {
  const { data } = await api.post<CommunityLikeResponse>(`community/posts/${postId}/like`)
  return data
}

export async function unlikeCommunityPost(postId: string) {
  const { data } = await api.delete<CommunityLikeResponse>(`community/posts/${postId}/like`)
  return data
}

export async function fetchCommunityProfile() {
  const { data } = await api.get<CommunityProfile>('community/profile/me')
  return data
}

export async function updateCommunityProfile(payload: { username?: string; display_name?: string; avatar_url?: string; bio?: string }) {
  const { data } = await api.patch<CommunityProfile>('community/profile/me', payload)
  return data
}

export async function fetchCommunityProfilePage(username: string, offset = 0, limit = 20) {
  const { data } = await api.get<CommunityProfilePage>(`community/profiles/${username}`, { params: { offset, limit } })
  return data
}
