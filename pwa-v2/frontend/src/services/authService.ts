import api from './api'
import { LoginCredentials, SignupData, AuthResponse, User } from '../types'

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const { data } = await api.post<AuthResponse>('/auth/login', credentials)
    return data
  },

  async signup(signupData: SignupData): Promise<AuthResponse> {
    const { data } = await api.post<AuthResponse>('/auth/signup', signupData)
    return data
  },

  async logout(): Promise<void> {
    await api.post('/auth/logout')
  },

  async getProfile(): Promise<User> {
    const { data } = await api.get<User>('/profile')
    return data
  },

  async updateProfile(updates: Partial<User>): Promise<User> {
    const { data } = await api.put<User>('/profile', updates)
    return data
  },
}
